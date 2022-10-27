import logging
import sys
from threading import Timer

from app import App
from controller import Controller
from device import DeviceUI


class SingleBot:
    def __init__(self,
                 device_serial,
                 package_name,
                 apk_path,
                 timeout,
                 throttle,
                 output_path,
                 keep_app,
                 model_name,
                 grant_permission):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.device_serial      = device_serial
        self.package_name       = package_name
        self.apk_path           = apk_path
        self.timeout            = timeout
        self.throttle           = throttle
        self.output_path        = output_path
        self.keep_app           = keep_app
        self.model_name         = model_name
        self.grant_permission   = grant_permission
        self.timer              = None


        self.device     = DeviceUI(serial=device_serial, output_path=output_path, grant_permission=grant_permission)
        self.app        = App(apk_path)
        if self.package_name == "":
            self.package_name = self.app.package_name
        self.controller = Controller(
            device      = self.device,
            app         = self.app,
            model_name  = self.model_name,
            throttle    = self.throttle
        )

    def start(self):
        try:
            if self.timeout > 0:
                self.timer = Timer(self.timeout, self.stop)
                self.timer.start()

            self.device.set_up()
            self.device.connect()
            self.device.install_app(self.app)
            self.device.logcat()
            self.controller.start()
        except KeyboardInterrupt:
            self.logger.info("Keyboard interrupt.")
        except Exception:
            import traceback
            traceback.print_exc()
            self.stop()
            sys.exit(-1)

    def stop(self):
        if self.timer and self.timer.is_alive():
            self.timer.cancel()
        if not self.keep_app:
            self.device.uninstall_app(self.app)
        if self.controller:
            self.controller.stop()
        # self.device.stop()



