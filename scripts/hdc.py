import tempfile
import json
import uuid
import shlex
import socket
import subprocess
from typing import Union, List
from dataclasses import dataclass


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
        if result.exit_code == 0:
            return lport
        raise RuntimeError("HDC forward port error", result.output)

    def rm_forward(self, lport: int, rport: int) -> int:
        result = _execute_command(f"hdc -t {self.serial} fport rm tcp:{lport} tcp:{rport}")
        if result.exit_code == 0:
            return lport
        raise RuntimeError("HDC forward port error", result.output)

    def send_file(self, lpath: str, rpath: str) -> None:
        result = _execute_command(f"hdc -t {self.serial} file send {lpath} {rpath}")
        if result.exit_code != 0:
            raise RuntimeError("HDC send file error", result.output)

    def recv_file(self, rpath: str, lpath: str) -> None:
        result = _execute_command(f"hdc -t {self.serial} file recv {rpath} {lpath}")
        if result.exit_code != 0:
            raise RuntimeError("HDC receive file error", result.output)

    def uninstall(self, bundlename: str) -> None:
        result = _execute_command(f"hdc -t {self.serial} uninstall {bundlename}")
        if result.exit_code != 0:
            raise RuntimeError("HDC uninstall error", result.output)

    def install(self, apkpath: str) -> None:
        result = _execute_command(f"hdc -t {self.serial} install {apkpath}")
        if result.exit_code != 0:
            raise RuntimeError("HDC install error", result.output)

    def shell(self, cmd: str) -> CommandResult:
        result = _execute_command(f"hdc -t {self.serial} shell {cmd}")
        if result.exit_code != 0:
            raise RuntimeError("HDC shell error", f"{cmd}\n{result.output}\n{result.error}")
        return result

    def list_apps(self) -> List[str]:
        result = self.shell("bm dump -a")
        raw = result.output.split('\n')
        return [item.strip() for item in raw]

    def send_key(self, key_id: int) -> None:
        """
        keyId: 1 -> home
        keyId: 2 -> back
        ...
        https://issuereporter.developer.huawei.com/detail/240306161416050/comment
        https://www.seaxiang.com/blog/b3944403863b4baf91fd1c5f471c6126

        """
        self.shell(f"uinput -K -d {key_id} -u {key_id}")

    def hide_keyboard(self) -> None:
        self.shell("uinput -K -d 2 -i 2 -u 2")

    def tap(self, x: int, y: int) -> None:
        self.shell(f"uinput -T -c {x} {y}")

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration: int = 300) -> None:
        self.shell(f"uinput -T -m {x1} {y1} {x2} {y2} {duration}")

    def input_text(self, x: int, y: int, text: str) -> None:
        self.shell(f"uitest uiInput inputText {x} {y} {text}")

    def clear_app_data(self, package_name: str) -> None:
        self.shell(f"bm clean -n {package_name} -d")

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