import re
import subprocess
from shlex import quote


class ADB:
    def __init__(self, device=None):
        if device is None:
            from device import DeviceUI
            device = DeviceUI()
        self.device = device
        self.cmd_prefix = ['adb', '-s', device.serial]

    def run_cmd(self, args):
        if isinstance(args, str):
            args = args.split()
        cmd = [] + self.cmd_prefix
        cmd += args
        # print(cmd)
        r = subprocess.check_output(cmd).strip()
        if not isinstance(r, str):
            r = r.decode()
        return r

    def shell(self, args):
        if isinstance(args, str):
            args = args.split()
        shell_args = ['shell'] + [quote(arg) for arg in args ]
        return self.run_cmd(shell_args)

    def get_installed_apps(self):
        app_lines = self.shell("pm list packages -f").splitlines()
        app_line_re = re.compile("package:(?P<apk_path>.+)=(?P<package>[^=]+)")
        package_to_path = {}
        for app_line in app_lines:
            m = app_line_re.match(app_line)
            if m:
                package_to_path[m.group('package')] = m.group('apk_path')
        return package_to_path