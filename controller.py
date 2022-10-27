import logging
import time

from event import EventLog
from model import MODEL_RANDOM, RandomModel


class Controller:
    def __init__(self, device, app, model_name, throttle, script_path=None):
        self.logger = logging.getLogger('InputEventManager')
        self.logger.setLevel(level=logging.INFO)
        self.enabled = True

        self.device = device
        self.app = app
        self.model_name = model_name
        self.throttle = throttle
        self.model = None
        self.event_log = None

        self.model = self.get_model(device, app)

    def get_model(self, device, app):
        if self.model_name == MODEL_RANDOM:
            model = RandomModel(self.device, self.app)
        else:
            self.logger.warning("No valid input policy specified. Using policy \"none\".")
            model = None

        return model

    def add_event(self, event):
        if event is None:
            return
        self.event_log = EventLog(self.device, self.app, event)
        self.event_log.start()
        time.sleep(self.throttle / 1000)
        self.event_log.stop()

    def start(self):
        self.logger.info("start sending events, policy is %s" % self.model_name)
        self.model.start(self)
        self.stop()
        self.logger.info("Finish sending events")

    def stop(self):
        print("Activity Coverage: ", len(self.model.activities) / len(self.model.all_activities))
        self.enabled = False
