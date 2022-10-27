import xml.etree.cElementTree as ET
from xml.etree.ElementTree import ElementTree, Element
import collections


EDIT_CLASS                  = "android.widget.EditText"
ACTION_EDIT                 = "edit"
ACTION_CLICK                = "click"
ACTION_LONG_CLICK           = "long_click"
ACTION_SCROLL_LEFT_TO_RIGHT = "scroll_left_to_right"
ACTION_SCROLL_RIGHT_TO_LEFT = "scroll_right_to_left"
ACTION_SCROLL_UP_TO_DOWN    = "scroll_up_to_down"
ACTION_SCROLL_DOWN_TO_UP    = "scroll_down_to_up"
ACTION_UIAUTOMATOR          = "uiautomator"
ACTION_INTENT               = "intent"
ACTION_KEY_EVENT            = "key"
ACTION_BACK_EVENT           = "back"


class Point:
    def __init__(self, left_x, left_y, right_x, right_y):
        self.left_x = int(left_x)
        self.left_y = int(left_y)
        self.right_x = int(right_x)
        self.right_y = int(right_y)

        self.x = (self.left_x + self.right_x) / 2
        self.y = (self.left_y + self.right_y) / 2

    @property
    def str(self):
        return f'[%s,%s][%s,%s]' %(self.left_x, self.left_y, self.right_x, self.right_y)


class Node:
    def __init__(self):
        self.index = 0
        self.text = ""
        self.resource_id = ""
        self.class_ = ""
        self.package = ""
        self.content_desc = ""
        self.checkable = False
        self.checked = False
        self.clickable = False
        self.enabled = False
        self.focusable = False
        self.focused = False
        self.scrollable = False
        self.long_clickable = False
        self.password = False
        self.selected = False
        self.visible_to_user = False
        self.bounds = Point(0, 0, 0, 0)
        self.children = []
        self.parent = None

    @property
    def str(self):
        return f'<index=%s text="%s" class="%s" resource-id="%s" package="%s" content-desc="%s" clickabele="%s">' % \
               (self.index, self.text, self.class_, self.resource_id, self.package, self.content_desc, self.clickable)

    @staticmethod
    def get_nodes_from_tree(tree):
        q = collections.deque()
        q.append(tree)
        nodes = []
        while q:
            node = q.pop()
            actions = Node.get_actions_from_node(node)
            if actions:
                nodes.append(node)

            for child in node.children:
                q.append(child)

        return nodes

    @staticmethod
    def get_actions_from_node(node):
        actions = []
        class_ = node.class_
        clickable = node.clickable
        long_clickable = node.long_clickable
        scrollable = node.long_clickable

        # if class_ == EDIT_CLASS:
        #     actions.append(ACTION_EDIT)
        if clickable:
            actions.append(ACTION_CLICK)
        elif long_clickable:
            actions.append(ACTION_LONG_CLICK)
        elif scrollable:
            actions.append(ACTION_SCROLL_LEFT_TO_RIGHT)
            actions.append(ACTION_SCROLL_UP_TO_DOWN)
            actions.append(ACTION_SCROLL_RIGHT_TO_LEFT)
            actions.append(ACTION_SCROLL_DOWN_TO_UP)
        return actions
