# -*- coding: iso-8859-1 -*-

from xml.dom.minidom import Node


class DummyNode:

    def __init__(self, value=None):
        self.value = value


def getText(node):
    return reduce(lambda x, y: x + y.data,
        filter(lambda n: n.nodeType == Node.TEXT_NODE, node.childNodes), "")


def getAttribute(node, attribute, default=None):
    if node.attributes.get(attribute):
        return node.attributes.get(attribute).value
    else:
        return default


class RequiredAttributeNotFoundError(Exception):
    pass


def getRequiredAttribute(node, attribute):
    if node.attributes.get(attribute):
        return node.attributes.get(attribute).value
    else:
        raise RequiredAttributeNotFoundError("Required attribute %s not found!" % attribute)


def getChildsByName(node, elementName):
    return filter(lambda n: n.nodeType == Node.ELEMENT_NODE and n.nodeName == elementName, node.childNodes)


def getChildsByNames(node, elementNames):
    return filter(lambda n: n.nodeType == Node.ELEMENT_NODE and n.nodeName in elementNames, node.childNodes)


def getChildByName(node, elementName):
    l = getChildsByName(node, elementName)
    if len(l) == 1:
        return l[0]
    else:
        assert(len(l) == 0)
        return None
