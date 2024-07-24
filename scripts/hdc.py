import subprocess
import tempfile
import json
import uuid
import shlex
import socket
from typing import Union, List
from collections import namedtuple


class _FreePort(object):
    def __init__(self):
        self._start = 10000
        self._end = 20000
        self._now = self._start - 1

    def get(self):
        while True:
            self._now += 1
            if self._now > self._end:
                self._now = self._start
            if not self.is_port_in_use(self._now):
                return self._now

    def is_port_in_use(self, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0


def _execute_command(cmdargs: Union[str, List[str]]):
    if isinstance(cmdargs, (list, tuple)):
        cmdline: str = ' '.join(list(map(shlex.quote, cmdargs)))
    elif isinstance(cmdargs, str):
        cmdline = cmdargs
    else:
        raise TypeError("cmdargs type invalid", type(cmdargs))
    try:
        process = subprocess.Popen(cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, error = process.communicate()
        output = output.decode('utf-8')
        error = error.decode('utf-8')
        print(cmdline)
        print(f"{output}\n{error}")
        return output, error
    except Exception as e:
        return None, str(e)


def list_devices() -> List[str]:
    devices = []
    output, error = _execute_command('hdc list targets')
    if not error and output:
        lines = output.strip().split('\n')
        for line in lines:
            devices.append(line.strip())
    return devices


ShellResponse = namedtuple("ShellResponse", ("output", "exit_code"))


class HdcWrapper:

    def __init__(self, serial) -> None:
        self.serial = serial

    def forward_port(self, rport: int) -> int:
        lport: int = _FreePort().get()
        output, error = _execute_command(f"hdc -t {self.serial} fport tcp:{lport} tcp:{rport}")
        if not error:
            return lport
        raise RuntimeError("HDC forward port error", output)

    def rm_forward(self, lport: int, rport: int) -> int:
        output, error = _execute_command(f"hdc -t {self.serial} fport rm tcp:{lport} tcp:{rport}")
        if not error:
            return lport
        raise RuntimeError("HDC forward port error", output)

    def send_file(self, lpath: str, rpath: str) -> None:
        output, error = _execute_command(f"hdc -t {self.serial} file send {lpath} {rpath}")
        if error:
            raise RuntimeError("HDC send file error", output)

    def recv_file(self, rpath: str, lpath: str) -> None:
        output, error = _execute_command(f"hdc -t {self.serial} file recv {rpath} {lpath}")
        if error:
            raise RuntimeError("HDC send file error", output)

    def uninstall(self, bundlename: str):
        output, error = _execute_command(f"hdc -t {self.serial} uninstall {bundlename}")
        if error:
            raise RuntimeError("HDC uninstall error", output)

    def install(self, apkpath: str):
        output, error = _execute_command(f"hdc -t {self.serial} install {apkpath}")
        if error:
            raise RuntimeError("HDC install error", output)

    def shell(self, cmd: str):
        output, error = _execute_command(f"hdc -t {self.serial} shell {cmd}")
        if error:
            raise RuntimeError("HDC shell error", f"{cmd}\n{output}\n{error}")
        return ShellResponse(output, error)

    def list_apps(self, serial: str) -> Union[List]:
        output = self.shell(serial, "bm dump -a").output
        raw = output.split('\n')
        return [item.strip() for item in raw]

    def send_key(self, keyId: int):
        """
        keyId: 1 -> home
        keyId: 2 -> back
        ...
        https://issuereporter.developer.huawei.com/detail/240306161416050/comment
        https://www.seaxiang.com/blog/b3944403863b4baf91fd1c5f471c6126

        """
        self.shell(f"uinput -K -d {keyId} -u {keyId}")

    def hide_keyboard(self):
        self.shell("uinput -K -d 2 -i 2 -u 2")

    def tap(self, x, y):
        self.shell(f"uinput -T -c {x} {y}")

    def swipe(self, x1, y1, x2, y2, duration=300):
        "uinput -T -m x1 y1 x2 y2 time"
        self.shell(f"uinput -T -m {x1} {y1} {x2} {y2} {duration}")

    def input_text(self, x, y, text: str):
        # hdc shell uitest uiInput inputText 100 100 hello
        self.shell(f"uitest uiInput inputText {x} {y} {text}")

    def clear_app_data(self, package_name: str):
        "bm clean -n {package_name} -d"
        self.shell(f"bm clean -n {package_name} -d")

    def screenshot(self, path: str) -> str:
        self.verbose = False
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

            f.close()
            return data