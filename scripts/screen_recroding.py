# -*- coding: utf-8 -*-

import socket
import json
import time
import os
import typing
import subprocess
import atexit
import hashlib
import threading
import numpy as np
from queue import Queue
from datetime import datetime

import cv2

from functools import cached_property

from hdc import HdcWrapper


ABC_RPC_PORT = 8012


class HmScreenRecorder:
    """Record the screen."""
    def __init__(self, serial: str):
        self.hdc = HdcWrapper(serial)
        self.sock = None
        self.jpeg_queue = Queue()
        self.threads: typing.List[threading.Thread] = []
        self.stop_event = threading.Event()

        # Register the instance method to be called at exit
        atexit.register(self._rm_local_port)

    @cached_property
    def local_port(self):
        return self.hdc.forward_port(ABC_RPC_PORT)

    def _rm_local_port(self):
        self.hdc.rm_forward(self.local_port, ABC_RPC_PORT)

    def _connect(self):
        """Create socket and connect to the RPC server."""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(3)
        self.sock.connect((("127.0.0.1", self.local_port)))

    def _send_message(self, api: str, args: list):
        """Send an RPC message to the server."""
        _msg = {
            "module": "com.ohos.devicetest.hypiumApiHelper",
            "method": "Captures",
            "params": {
                "api": api,
                "args": args
            },
            "request_id": datetime.now().strftime("%Y%m%d%H%M%S%f")
        }
        msg = json.dumps(_msg, ensure_ascii=False, separators=(',', ':'))
        print(msg)
        self.sock.sendall(msg.encode('utf-8') + b'\n')

    def _recv_mesaage(self, buff_size: int = 1024, decode=False) -> typing.Union[bytearray, str]:
        try:
            relay = self.sock.recv(buff_size)
            if decode:
                relay = relay.decode()
            return relay
        except (socket.timeout, UnicodeDecodeError) as e:
            # socket.timeout
            # UnicodeDecodeError
            print(e)
            if decode:
                return ''
            return bytearray()

    def start(self, file_path: str):
        """
        Starts screen recording.

        This method restarts the UI test service, establishes a connection with the RPC server,
        sends a message to start screen capturing, and begins the recording and video writing threads.

        Args:
            file_path (str): Path where the recorded video will be saved.

        Raises:
            RuntimeError: If the screen capture fails to start.
        """
        self._init_so_resource()
        self._restart_uitest_service()

        self._connect()

        self._video_path = file_path
        self._send_message("startCaptureScreen", [])

        reply: str = self._recv_mesaage(1024, decode=True)
        if "true" in reply:
            record_th = threading.Thread(target=self._record_worker)
            writer_th = threading.Thread(target=self._video_writer)
            record_th.start()
            writer_th.start()
            self.threads.extend([record_th, writer_th])
        else:
            raise RuntimeError("Failed to start hm screen capture.")

    def _record_worker(self):
        """Capture screen frames and save current frames."""

        # JPEG start and end markers.
        start_flag = b'\xff\xd8'
        end_flag = b'\xff\xd9'
        buffer = bytearray()
        while not self.stop_event.is_set():
            try:
                buffer += self._recv_mesaage(4096 * 1024)
            except Exception as e:
                print(f"Error receiving data: {e}")
                break

            start_idx = buffer.find(start_flag)
            end_idx = buffer.find(end_flag)
            while start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                # Extract one JPEG image
                jpeg_image: bytearray = buffer[start_idx:end_idx + 2]
                self.jpeg_queue.put(jpeg_image)

                buffer = buffer[end_idx + 2:]

                # Search for the next JPEG image in the buffer
                start_idx = buffer.find(start_flag)
                end_idx = buffer.find(end_flag)

    def _video_writer(self):
        """Write frames to video file."""
        cv2_instance = None
        while not self.stop_event.is_set():
            if not self.jpeg_queue.empty():
                jpeg_image = self.jpeg_queue.get(timeout=0.1)
                img = cv2.imdecode(np.frombuffer(jpeg_image, np.uint8), cv2.IMREAD_COLOR)
                if cv2_instance is None:
                    height, width = img.shape[:2]
                    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                    cv2_instance = cv2.VideoWriter(self._video_path, fourcc, 10, (width, height))

                cv2_instance.write(img)

        if cv2_instance:
            cv2_instance.release()

    def stop(self):
        """Stop screen recording."""
        try:
            self.stop_event.set()
            for t in self.threads:
                t.join()

            if self.sock:
                self._send_message("stopCaptureScreen", [])
                self._recv_mesaage(1024, decode=True)
                self.sock.close()
        except Exception as e:
            print(f"An error occurred: {e}")

    def _init_so_resource(self):
        "Initialize the agent.so resource on the device."

        def __get_so_local_path() -> str:
            current_path = os.path.dirname(os.path.realpath(__file__))
            return os.path.join(os.path.dirname(current_path), 'scripts', 'agent.so')

        def __check_device_so_file_exists() -> bool:
            """Check if the agent.so file exists on the device."""
            command = "[ -f /data/local/tmp/agent.so ] && echo 'so exists' || echo 'so not exists'"
            result = self.hdc.shell(command).output.strip()
            return "so exists" in result

        def __get_remote_md5sum() -> str:
            """Get the MD5 checksum of the file on the device."""
            command = "md5sum /data/local/tmp/agent.so | awk '{ print $1 }'"
            result = self.hdc.shell(command).output.strip()
            return result

        def __get_local_md5sum(f: str) -> str:
            """Calculate the MD5 checksum of a local file."""
            hash_md5 = hashlib.md5()
            with open(f, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()

        local_path = __get_so_local_path()
        remote_path = "/data/local/tmp/agent.so"

        if __check_device_so_file_exists() and __get_local_md5sum(local_path) == __get_remote_md5sum():
            return
        self.hdc.send_file(local_path, remote_path)

    def _restart_uitest_service(self):
        """
        Restart the UITest daemon. Screen recording depends on this process.
        Note: 'hdc shell aa test' will also start a uitest daemon.
        $ hdc shell ps -ef |grep uitest
        shell        44306     1 25 11:03:37 ?    00:00:16 uitest start-daemon singleness
        shell        44416     1 2 11:03:42 ?     00:00:01 uitest start-daemon com.krunner.hm.atx@4x9@1"
        """
        try:
            # pids: list = self.hdc.shell("pidof uitest").output.strip().split()
            result = self.hdc.shell("ps -ef | grep uitest | grep singleness").output.strip()
            lines = result.splitlines()
            for line in lines:
                if 'uitest start-daemon singleness' in line:
                    parts = line.split()
                    pid = parts[1]
                    self.hdc.shell(f"kill -9 {pid}")
                    print(f"Killed uitest process with PID {pid}")

            self.hdc.shell("uitest start-daemon singleness")
            time.sleep(.5)

        except subprocess.CalledProcessError as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    recorder = HmScreenRecorder("FMR0223C13000649")
    recorder.start("test.mp4")
    input("Press Enter to stop...")
    recorder.stop()