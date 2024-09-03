# -*- coding: utf-8 -*-

import tempfile
import json
import uuid
import shlex
import socket
import subprocess
from typing import Union, List
from dataclasses import dataclass

from keycode import KeyCode


class _FreePort:
    def __init__(self):
        self._start = 10000
        self._end = 20000
        self._now = self._start - 1

    def get(self) -> int:
        while True:
            self._now += 1
            if self._now > self._end:
                self._now = self._start
            if not self.is_port_in_use(self._now):
                return self._now

    @staticmethod
    def is_port_in_use(port: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0


@dataclass
class CommandResult:
    output: str
    error: str
    exit_code: int


def _execute_command(cmdargs: Union[str, List[str]]) -> CommandResult:
    if isinstance(cmdargs, (list, tuple)):
        cmdline: str = ' '.join(list(map(shlex.quote, cmdargs)))
    elif isinstance(cmdargs, str):
        cmdline = cmdargs

    try:
        process = subprocess.Popen(cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, error = process.communicate()
        output = output.decode('utf-8')
        error = error.decode('utf-8')
        exit_code = process.returncode
        return CommandResult(output, error, exit_code)
    except Exception as e:
        return CommandResult("", str(e), -1)


def list_devices() -> List[str]:
    devices = []
    result = _execute_command('hdc list targets')
    if result.exit_code == 0 and result.output:
        lines = result.output.strip().split('\n')
        for line in lines:
            devices.append(line.strip())
    return devices


class HdcWrapper:
    def __init__(self, serial: str) -> None:
        self.serial = serial

    def forward_port(self, rport: int) -> int:
        lport: int = _FreePort().get()
        result = _execute_command(f"hdc -t {self.serial} fport tcp:{lport} tcp:{rport}")
        if result.exit_code != 0:
            raise RuntimeError("HDC forward port error", result.output)
        return lport

    def rm_forward(self, lport: int, rport: int) -> int:
        result = _execute_command(f"hdc -t {self.serial} fport rm tcp:{lport} tcp:{rport}")
        if result.exit_code != 0:
            raise RuntimeError("HDC forward port error", result.output)
        return lport

    def send_file(self, lpath: str, rpath: str):
        result = _execute_command(f"hdc -t {self.serial} file send {lpath} {rpath}")
        if result.exit_code != 0:
            raise RuntimeError("HDC send file error", result.output)
        return result

    def recv_file(self, rpath: str, lpath: str):
        result = _execute_command(f"hdc -t {self.serial} file recv {rpath} {lpath}")
        if result.exit_code != 0:
            raise RuntimeError("HDC receive file error", result.output)
        return result

    def uninstall(self, bundlename: str):
        result = _execute_command(f"hdc -t {self.serial} uninstall {bundlename}")
        if result.exit_code != 0:
            raise RuntimeError("HDC uninstall error", result.output)
        return result

    def install(self, apkpath: str):
        result = _execute_command(f"hdc -t {self.serial} install {apkpath}")
        if result.exit_code != 0:
            raise RuntimeError("HDC install error", result.output)
        return result

    def shell(self, cmd: str, error_raise=True) -> CommandResult:
        result = _execute_command(f"hdc -t {self.serial} shell {cmd}")
        if result.error and error_raise:
            raise RuntimeError("HDC shell error", f"{cmd}\n{result.output}\n{result.error}")
        return result

    def list_apps(self) -> List[str]:
        result = self.shell("bm dump -a")
        raw = result.output.split('\n')
        return [item.strip() for item in raw]

    def start_app(self, package_name: str, ability_name: str):
        return self.shell(f"aa start -a {ability_name} -b {package_name}")

    def stop_app(self, package_name: str):
        return self.shell(f"aa force-stop {package_name}")

    def wakeup(self):
        self.shell("power-shell wakeup")

    def send_key(self, key_code: Union[KeyCode, int]) -> None:
        if isinstance(key_code, KeyCode):
            key_code = key_code.value
        self.shell(f"uitest uiInput keyEvent {key_code}")

    def go_home(self):
        self.send_key(KeyCode.HOME)

    def back(self):
        self.send_key(KeyCode.BACK)

    def click(self, x: int, y: int):
        self.shell(f"uitest uiInput click {x} {y}")

    def doubleClick(self, x: int, y: int):
        self.shell(f"uitest uiInput doubleClick {x} {y}")

    def longClick(self, x: int, y: int):
        self.shell(f"uitest uiInput longClick {x} {y}")

    def swipe(self, x1, y1, x2, y2, speed=1000):
        """
        speed为滑动速率, 范围:200~40000, 不在范围内设为默认值为600, 单位: 像素点/秒
        """
        self.shell(f"uitest uiInput swipe {x1} {y1} {x2} {y2} {speed}")

    def drag(self, x1, y1, x2, y2, speed=1000):
        """
        speed为滑动速率, 范围:200~40000, 不在范围内设为默认值为600, 单位: 像素点/秒
        """
        self.shell(f"uitest uiInput drag {x1} {y1} {x2} {y2} {speed}")

    def input_text(self, x: int, y: int, text: str):
        self.shell(f"uitest uiInput inputText {x} {y} {text}")

    def screenshot(self, path: str) -> str:
        _uuid = uuid.uuid4().hex
        _tmp_path = f"/data/local/tmp/_tmp_{_uuid}.jpeg"
        self.shell(f"snapshot_display -f {_tmp_path}")
        self.recv_file(_tmp_path, path)
        self.shell(f"rm -rf {_tmp_path}")  # remove local path
        return path

    def dump_hierarchy(self) -> dict:
        _tmp_path = "/data/local/tmp/_tmp.json"
        self.shell(f"uitest dumpLayout -p {_tmp_path}")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as f:
            path = f.name
            self.recv_file(_tmp_path, path)

            try:
                with open(path, 'r') as file:
                    data = json.load(file)
            except Exception as e:
                print(f"Error loading JSON file: {e}")
                data = {}

            return data