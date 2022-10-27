import json
import os
import threading
import time
from abc import abstractmethod

from intent import Intent
from utils.tree.node import ACTION_CLICK, ACTION_LONG_CLICK, ACTION_SCROLL_LEFT_TO_RIGHT, ACTION_SCROLL_RIGHT_TO_LEFT, \
    ACTION_SCROLL_UP_TO_DOWN, ACTION_SCROLL_DOWN_TO_UP, ACTION_EDIT, ACTION_UIAUTOMATOR, ACTION_INTENT, ACTION_KEY_EVENT


class Event:
    def __init__(self, node=None, action_type=None):
        self.node = node
        self.action_type = action_type
        self.log_lines = None

    def from_action_type(self, node, action_type):
        if action_type == ACTION_CLICK:
            return ClickEvent(node)
        elif action_type == ACTION_LONG_CLICK:
            return LongClickEvent(node)
        elif action_type == ACTION_SCROLL_DOWN_TO_UP:
            return ScrollUpEvent(node)
        elif action_type == ACTION_SCROLL_UP_TO_DOWN:
            return ScrollDownEvent(node)
        elif action_type == ACTION_SCROLL_LEFT_TO_RIGHT:
            return ScrollRightEvent(node)
        elif action_type == ACTION_SCROLL_RIGHT_TO_LEFT:
            return ScrollLeftEvent(node)

    @abstractmethod
    def send(self, device):
        raise NotImplementedError

    @property
    def event_json(self):
        event_dict = {"action":         self.action_type,
                      "text":           self.node.text,
                      "class":          self.node.class_,
                      "resource_id":    self.node.resource_id,
                      "package_name":   self.node.package,
                      "content_desc":   self.node.content_desc,
                      "bounds":         self.node.bounds.str}
        return json.dumps(event_dict)

    @property
    def event_dict(self):
        return {"action":         self.action_type,
                "text":           self.node.text,
                "class":          self.node.class_,
                "resource_id":    self.node.resource_id,
                "package_name":   self.node.package,
                "content_desc":   self.node.content_desc,
                "bounds":         self.node.bounds.str}


class ClickEvent(Event):
    def __init__(self, node):
        super().__init__()
        self.action_type = ACTION_CLICK
        self.node = node
        self.x = node.bounds.x
        self.y = node.bounds.y

    def send(self, device):
        device.ui.click(self.x, self.y)
        return True


class LongClickEvent(Event):
    def __init__(self, node):
        super().__init__()
        self.action_type = ACTION_LONG_CLICK
        self.node = node
        self.x = node.bounds.x
        self.y = node.bounds.y

    def send(self, device):
        device.ui.long_click(self.x, self.y)
        return True


class ScrollUpEvent(Event):
    def __init__(self, node):
        super().__init__()
        self.action_type = ACTION_SCROLL_DOWN_TO_UP
        self.node = node
        self.left_x = node.bounds.left_x
        self.left_y = node.bounds.left_y
        self.right_x = node.bounds.right_x
        self.right_y = node.bounds.right_y

    def send(self, device):
        device.ui.swipe_ext("up", box=(self.left_x, self.left_y, self.right_x, self.right_y))
        return True


class ScrollDownEvent(Event):
    def __init__(self, node):
        super().__init__()
        self.action_type = ACTION_SCROLL_UP_TO_DOWN
        self.node = node
        self.left_x = node.bounds.left_x
        self.left_y = node.bounds.left_y
        self.right_x = node.bounds.right_x
        self.right_y = node.bounds.right_y

    def send(self, device):
        device.ui.swipe_ext("down", box=(self.left_x, self.left_y, self.right_x, self.right_y))
        return True


class ScrollRightEvent(Event):
    def __init__(self, node):
        super().__init__()
        self.action_type = ACTION_SCROLL_LEFT_TO_RIGHT
        self.node = node
        self.left_x = node.bounds.left_x
        self.left_y = node.bounds.left_y
        self.right_x = node.bounds.right_x
        self.right_y = node.bounds.right_y

    def send(self, device):
        device.ui.swipe_ext("right", box=(self.left_x, self.left_y, self.right_x, self.right_y))
        return True


class ScrollLeftEvent(Event):
    def __init__(self, node):
        super().__init__()
        self.action_type = ACTION_SCROLL_RIGHT_TO_LEFT
        self.node = node
        self.left_x = node.bounds.left_x
        self.left_y = node.bounds.left_y
        self.right_x = node.bounds.right_x
        self.right_y = node.bounds.right_y

    def send(self, device):
        device.ui.swipe_ext("left", box=(self.left_x, self.left_y, self.right_x, self.right_y))
        return True


class IntentEvent(Event):
    def __init__(self, intent=None):
        super().__init__()
        self.action_type = ACTION_INTENT
        if isinstance(intent, Intent):
            self.intent = intent.get_cmd()
        elif isinstance(intent, str):
            self.intent = intent

    def send(self, device):
        device.send_intent(intent=self.intent)
        print("send start app intent")
        return True

    @property
    def event_json(self):
        event_dict = {"action":  self.action_type,
                      "intent":  self.intent}
        return json.dumps(event_dict)

    @property
    def event_dict(self):
        return {"action": self.action_type,
                "intent": self.intent}


class KeyEvent(Event):
    def __init__(self, name=None):
        super().__init__()
        self.action_type = ACTION_KEY_EVENT
        self.name = name

    def send(self, device):
        device.ui.press(self.name)
        return True

    @property
    def event_json(self):
        event_dict = {"action":     self.action_type,
                      "key_event":  self.name}
        return json.dumps(event_dict)

    @property
    def event_dict(self):
        event_dict = {"action": self.action_type,
                      "key_event": self.name}
        return event_dict


class EventLog:
    def __init__(self, device, app, event, tag=None):
        self.device = device
        self.app = app
        self.event = event
        if tag is None:
            tag = int(round(time.time() * 1000))
        self.tag = tag
        self.from_state = None
        self.to_state = None

    def to_dict(self):
        return{
            "tag":          self.tag,
            "event":        self.event.event_dict,
            "from_state":   self.from_state.state_dict,
            "to_state":     self.to_state.state_dict,
        }

    def start(self):
        self.from_state = self.device.get_current_state()
        self.device.send_event(self.event)

    def stop(self):
        self.to_state = self.device.get_current_state()
        save_thread = threading.Thread(target=self.save())
        save_thread.start()

    def save(self):
        events_output_path = os.path.join(self.device.output_path, "events")
        if not os.path.exists(events_output_path):
            os.makedirs(events_output_path)

        # write event json
        event_json_file_path = "%s/event_%s.json" % (events_output_path, self.tag)
        event_json_file = open(event_json_file_path, "w")
        json.dump(self.to_dict(), event_json_file, indent=2)
        event_json_file.close()

        # write tree
        from_xml        = self.from_state.xml
        to_xml          = self.to_state.xml
        from_xml_time   = self.from_state.screenshot_time
        to_xml_time     = self.to_state.screenshot_time
        xml_output_path = os.path.join(self.device.output_path, "xmls")
        if not os.path.exists(xml_output_path):
            os.makedirs(xml_output_path)

        from_xml_path = "%s/%s.xml" % (xml_output_path, from_xml_time)
        with open(from_xml_path, "w", encoding="utf-8") as f:
            f.write(from_xml)
            f.close()

        to_xml_path = "%s/%s.xml" % (xml_output_path, to_xml_time)
        with open(to_xml_path, "w", encoding="utf-8") as f:
            f.write(to_xml)
            f.close()


