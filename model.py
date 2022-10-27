import logging
import random
from abc import abstractmethod

from intent import Intent
from event import Event, IntentEvent, KeyEvent
from utils.tree.node import Node, ACTION_BACK_EVENT
from utils.tree.trans_xml import xml_to_tree

MODEL_RANDOM = "random"


class Model:
    def __init__(self, device, app):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.device = device
        self.app = app

        self.all_activities = app.activities
        self.activities = set()

    def start(self, controller):
        while controller.enabled:
            try:
                event = self.generate_event()
                controller.add_event(event)
                self.get_coverage(controller)
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.logger.warning("exception during sending events: %s" % e)
                import traceback
                traceback.print_exc()
                continue

    @abstractmethod
    def generate_event(self):
        pass

    def get_coverage(self, controller):
        self.activities.add(controller.event_log.from_state.foreground_activity)
        self.activities.add(controller.event_log.to_state.foreground_activity)


class RandomModel(Model):
    def __init__(self, device, app):
        super(RandomModel, self).__init__(device, app)

    def generate_event(self):
        if not self.device.is_foreground(self.app):
            component = self.app.package_name
            if self.app.main_activity:
                component += "/%s" % self.app.main_activity
            return IntentEvent(Intent(suffix=component))

        trees = xml_to_tree(self.device.ui.dump_hierarchy())
        tree = None
        for temp_tree in trees:
            package_name = temp_tree.package
            if package_name == self.app.package_name:
                tree = temp_tree
        nodes = Node.get_nodes_from_tree(tree)
        if len(nodes) == 0:
            return KeyEvent(ACTION_BACK_EVENT)
        node = self.select_node(nodes)

        actions = node.get_actions_from_node(node)
        action_type = self.select_action(actions)

        return Event().from_action_type(node, action_type)
        # return Event(node=node, action_type=action_type)

    def select_node(self, nodes):
        node_num = len(nodes) - 1
        random_index = random.randint(0, node_num)
        return nodes[random_index]

    def select_action(self, actions):
        action_num = len(actions) - 1
        random_index = random.randint(0, action_num)
        return actions[random_index]
