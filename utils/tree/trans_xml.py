import re
import xml.etree.ElementTree as ET
import collections
from utils.tree.node import Node, Point


def element_to_node(attr):
    node = Node()
    node.index              = int(attr['index'])
    node.text               = attr['text']
    node.resource_id        = attr['resource-id']
    node.class_             = attr['class']
    node.package            = attr['package']
    node.content_desc       = attr['content-desc']
    node.checkable          = False if attr['checkable'] == "false" else True
    node.checked            = False if attr['checked'] == "false" else True
    node.clickable          = False if attr['clickable'] == "false" else True
    node.enabled            = False if attr['enabled'] == "false" else True
    node.focusable          = False if attr['focusable'] == "false" else True
    node.focused            = False if attr['focused'] == "false" else True
    node.scrollable         = False if attr['scrollable'] == "false" else True
    node.long_clickable     = False if attr['long-clickable'] == "false" else True
    node.password           = False if attr['password'] == "false" else True
    node.selected           = False if attr['selected'] == "false" else True
    node.visible_to_user    = False if attr['visible-to-user'] == "false" else True
    bounds                  = attr['bounds']

    source_bounds = re.compile('\[([^ ]+),([^ ]+)\]\[([^ ]+),([^ ]+)\]')
    dist_activities = source_bounds.search(bounds)
    if dist_activities:
        node.bounds = Point(dist_activities.group(1),
                            dist_activities.group(2),
                            dist_activities.group(3),
                            dist_activities.group(4))
    return node


def hash_tag_attrib(attrib):
    val = attrib['index'] + attrib['text'] + attrib['resource-id'] + attrib['class'] + attrib['package'] + attrib['content-desc'] + attrib['bounds']
    return hash(val)


def get_root_tree(element):
    element_node_table = {}
    q = collections.deque()
    q.append(element)

    root = element_to_node(element.attrib)
    hash_attrib = hash_tag_attrib(element.attrib)
    element_node_table[hash_attrib] = root

    while q:
        el = q.pop()

        attrib = el.attrib
        hash_attrib = hash_tag_attrib(attrib)
        if hash_attrib not in element_node_table.keys():
            element_node_table[hash_attrib] = element_to_node(attrib)
        temp_root_node = element_node_table[hash_attrib]

        for child in el:
            q.append(child)

            child_node = element_to_node(child.attrib)
            temp_root_node.children.append(child_node)
            child_node.parent = temp_root_node

            hash_attrib = hash_tag_attrib(child.attrib)
            element_node_table[hash_attrib] = child_node

    return root


def xml_to_tree(xml):
    elements = []

    root_et = ET.fromstring(xml)
    q = collections.deque()
    q.append(root_et)

    # 过滤 hierarchy, 得到n个element
    el = q.pop()
    assert el.tag == "hierarchy"
    for child in el:
        elements.append(child)

    # 遍历n个element，获取对应n个树
    roots = []
    for el in elements:
        root = get_root_tree(el)
        roots.append(root)

    return roots
