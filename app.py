class App:
    def __init__(self, apk_path):
        """
       create an App instance
       :param app_path: local file path of app
       :return:
       """
        assert apk_path is not None
        self.apk_path = apk_path
        from androguard.core.bytecodes.apk import APK
        self.apk = APK(self.apk_path)
        self.package_name = self.apk.get_package()
        self.main_activity = self.apk.get_main_activity()
        self.permissions = self.apk.get_permissions()
        self.activities = self.apk.get_activities()


if __name__ == '__main__':
    app_path = './app/amaze.apk'
    app = App(app_path)
    print(app.main_activity)
    print(app.permissions)