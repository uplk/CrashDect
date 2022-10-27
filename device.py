import logging
import os.path
import re
import subprocess
import time
from sys import stdout

import uiautomator2 as u2

from intent import Intent
from adb import ADB
from app import App
from utils.tree.trans_xml import xml_to_tree
from utils.tree import node


class DeviceState:
    def __init__(self, device, xml, foreground_activity, tag=None, screenshot_path=None, screenshot_time=None):
        self.device = device
        self.foreground_activity = foreground_activity
        if tag is None:
            from datetime import datetime
            tag = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        self.tag = tag
        self.screenshot_path = screenshot_path
        self.xml = xml
        self.screenshot_time = screenshot_time

    @property
    def state_dict(self):
        return {
            "foreground_activity": self.foreground_activity,
            "screenshot_path": self.screenshot_path,
            "screenshot_time": self.screenshot_time
        }


class Display:
    def __init__(self):
        self.width = 0
        self.height = 0

    def get_attribute(self, display):
        self.width = display['width']
        self.height = display['height']


class Battery:
    def __init__(self):
        self.acPowered = False
        self.usbPowered = False
        self.status = 0
        self.health = 0
        self.present = False
        self.level = 0
        self.scale = 0
        self.voltage = 0
        self.temperature = 0
        self.technology = 0

    def get_attribute(self, battery):
        self.acPowered = battery['acPowered']
        self.usbPowered = battery['usbPowered']
        self.status = battery['status']
        self.health = battery['health']
        self.present = battery['present']
        self.level = battery['level']
        self.scale = battery['scale']
        self.voltage = battery['voltage']
        self.temperature = battery['temperature']
        self.technology = battery['technology']


class Memory:
    def __init__(self):
        self.total = 0
        self.around = 0

    def get_attribute(self, memory):
        self.total = memory['total']
        self.around = memory['around']


class Cpu:
    def __init__(self):
        self.cores = 0
        self.hardware = ""

    def get_attribute(self, cpu):
        self.cores = cpu['cores']
        self.hardware = cpu['hardware']
        return self


class DeviceInfo:
    def __init__(self):
        self.udid = ""
        self.version = ""
        self.serial = ""
        self.brand = ""
        self.model = ""
        self.hwaddr = ""
        self.sdk = ""
        self.agent_version = ""
        self.display = Display()
        self.battery = Battery()
        self.memory = Memory()
        self.cpu = Cpu()

    def get_attribute(self, device_info):
        self.udid = device_info['udid']
        self.version = device_info['version']
        self.brand = device_info['brand']
        self.model = device_info['model']
        self.hwaddr = device_info['hwaddr']
        self.sdk = device_info['sdk']
        self.agent_version = device_info['agentVersion']
        self.display = Display()
        self.battery = Battery()
        self.memory = Memory()
        # self.cpu = Cpu()

        self.display.get_attribute(device_info['display'])
        self.battery.get_attribute(device_info['battery'])
        self.memory.get_attribute(device_info['memory'])

        # self.cpu.get_attribute(device_info['cpu'])


class DeviceUI:
    def __init__(self, serial=None, output_path=None, grant_permission=None):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.serial = serial
        self.grant_permission = grant_permission
        self.adb = ADB(device=self)
        self.ui = None
        self.device_info = DeviceInfo()
        self.output_path = output_path
        if output_path is not None:
            if not os.path.isdir(output_path):
                os.makedirs(output_path)

    def connect(self):
        self.ui = u2.connect_usb(self.serial)
        self.device_info.get_attribute(self.ui.device_info)

    def get_top_activity_name(self):
        r = self.adb.shell("dumpsys activity activities")
        # * Hist #0: ActivityRecord{6d65b24 u0 com.bbk.launcher2/.Launcher d0 s0 t1}
        source_activity_line = re.compile('\* Hist #\d+: ActivityRecord{[^ ]+ [^ ]+ ([^ ]+) [^ ]+ [^ ]+ [^ ]+}')
        dist_activities = source_activity_line.search(r)
        if dist_activities:
            return dist_activities.group(1)
        else:
            source_activity_line = re.compile('\* Hist #\d+: ActivityRecord{[^ ]+ [^ ]+ ([^ ]+) t(\d+)}')
            dist_activities = source_activity_line.search(r)
            if dist_activities:
                return dist_activities.group(1)

        return None

    def is_foreground(self, app):
        if isinstance(app, str):
            package_name = app
        elif isinstance(app, App):
            package_name = app.package_name
        else:
            self.logger.error("package name is null")
            package_name = ""

        top_activity_name = self.get_top_activity_name()
        if top_activity_name is None:
            print("top_activity is None")
            return False
        return top_activity_name.startswith(package_name)

    def start_app(self, app):
        self.ui.app_start(app.package_name)

    def install_app(self, app):
        assert isinstance(app, App)
        package_name = app.package_name
        if package_name not in self.adb.get_installed_apps():
            install_cmd = ["adb", "-s", self.serial, "install"]
            if self.grant_permission:
                install_cmd.append("-g")
            install_cmd.append(app.apk_path)
            install_p = subprocess.Popen(install_cmd, stdout=subprocess.PIPE)
            while package_name not in self.adb.get_installed_apps():
                print("Please wait while installing the app...")
                time.sleep(2)

    def uninstall_app(self, app):
        if isinstance(app, App):
            package_name = app.package_name
        else:
            package_name = app
        if package_name in self.adb.get_installed_apps():
            uninstall_cmd = ["adb", "-s", self.serial, "uninstall", package_name]
            uninstall_p = subprocess.Popen(uninstall_cmd, stdout=subprocess.PIPE)
            while package_name in self.adb.get_installed_apps():
                print("Please wait while uninstalling the app...")
                time.sleep(2)
            # uninstall_p.terminate()

    def push_file(self, local_file, remote_dir="/sdcard/"):
        if not os.path.exists(local_file):
            print("push_file file does not exist: %s" % local_file)
        self.adb.run_cmd(["push", local_file, remote_dir])

    def pull_file(self, remote_file, local_file):
        self.adb.run_cmd(["pull", remote_file, local_file])

    def take_screenshot(self):
        timestamp = int(time.time() * 1000)
        local_image_dir = os.path.join(self.output_path, "temp")
        if not os.path.exists(local_image_dir):
            os.makedirs(local_image_dir)
        local_image_path = os.path.join(local_image_dir, "%s_%s.png" % (self.serial, timestamp))
        self.ui.screenshot(local_image_path)
        return local_image_path,  timestamp

    def get_current_state(self):
        self.logger.debug("getting current device state...")
        current_state = None
        try:
            xml = self.ui.dump_hierarchy()
            tree = xml_to_tree(xml)
            foreground_activity = self.get_top_activity_name()
            screenshot_path, timestamp = self.take_screenshot()
            self.logger.debug("finish getting current device state...")
            current_state = DeviceState(self,
                                        xml=xml,
                                        foreground_activity=foreground_activity,
                                        screenshot_path=screenshot_path,
                                        screenshot_time=timestamp
                                       )
        except Exception as e:
            self.logger.warning("exception in get_current_state: %s" % e)
            import traceback
            traceback.print_exc()
        self.logger.debug("finish getting current device state...")
        if not current_state:
            self.logger.warning("Failed to get current state!")
        return current_state

    def get_screenshot_time(self, screenshot_path):
        screenshot_time = screenshot_path[screenshot_path.find('_')+1 : screenshot_path.find('.')]
        return screenshot_time

    def logcat(self):
        path = os.path.join(self.output_path, self.serial + "-logcat.txt")
        index = 1
        while os.path.exists(path):
            path = os.path.join(self.output_path, self.serial + "-logcat" + str(index) + ".txt")
            index += 1

        subprocess.run(["adb", "-s", self.serial,"push", "logcat", "-b", "crash",  ">", path])

    def wait_for_device(self):
        try:
            subprocess.check_call(["adb", "-s", self.serial, "wait-for-device"])
        except:
            self.logger.warning("error waiting for device")

    def set_up(self):
        self.wait_for_device()

    def stop(self):
        self.ui.stop()

    def send_intent(self, intent):
        if isinstance(intent, Intent):
            cmd = intent.get_cmd()
        else:
            cmd = intent
        print("Intent Event: ", cmd)
        return self.adb.shell(cmd)

    def send_event(self, event):
        event.send(self)



