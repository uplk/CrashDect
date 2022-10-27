class Intent:
    def __init__(self, prefix="start", suffix=None):
        self.action_type = "intent"
        self.prefix = prefix
        self.suffix = suffix

        self.cmd = None
        self.get_cmd()

    def get_cmd(self):
        if self.cmd is not None:
            return self.cmd
        cmd = "am "
        if self.prefix:
            cmd += self.prefix
        if self.prefix:
            cmd += " " + self.suffix
        self.cmd = cmd
        return self.cmd