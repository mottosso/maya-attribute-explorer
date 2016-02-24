from PySide import QtGui
from maya import cmds


data = {"currentWidget": None}


def show():
    """Show GUI for currently selected node

    Usage:
        Select a node in Maya, and run this function.

    """

    try:
        node = cmds.ls(sl=True)[0]
    except:
        return cmds.warning("Select a node to inspect")

    attrs = _parse_node(node)

    parent = {o.objectName(): o for o in QtGui.qApp.topLevelWidgets()}
    parent = parent["MayaWindow"]

    window = QtGui.QDialog(parent)
    window.setWindowTitle("Inspect \"%s\"" % node)

    widget = QtGui.QTreeWidget()
    _fill_widget(widget, attrs)

    for i in range(widget.invisibleRootItem().childCount()):
        child = widget.invisibleRootItem().child(i)
        widget.collapseItem(child)

    layout = QtGui.QVBoxLayout(window)
    layout.addWidget(widget)

    window.show()
    window.resize(300, 700)

    data["currentWidget"] = widget
    return widget


def _parse_node(node):
    """Generate a dictionary from attributes of `node`

    Arguments:
        node (str): Absolute path to node

    """

    attrs = {}

    for attr in cmds.listAttr(node):
        value = None
        try:
            value = cmds.getAttr(node + "." + attr, silent=True)
        except (RuntimeError, ValueError):
            value = "Value cannot be read"

        attrs[attr] = value

    return attrs


def _fill_item(item, data):
    """Recursively append contents of `data` to `item`

    Arguments:
        item (QListWidgetItem): Parent item of new data
        data (any): dict, list or string of data

    """

    item.setExpanded(True)

    if type(data) is dict:
        for key in sorted(data):
            value = data[key]

            child = QtGui.QTreeWidgetItem()
            child.setText(0, unicode(key))
            child.setExpanded(False)
            item.addChild(child)
            _fill_item(child, value)

    elif type(data) is list:
        for value in data:
            child = QtGui.QTreeWidgetItem()
            item.addChild(child)
            if type(value) is dict:     
                child.setText(0, '[dict]')
                _fill_item(child, value)
            elif type(value) is list:
                child.setText(0, '[list]')
                _fill_item(child, value)
            else:
                child.setText(0, unicode(value))
            child.setExpanded(False)

    else:
        child = QtGui.QTreeWidgetItem()
        child.setText(0, unicode(data))
        item.addChild(child)


def _fill_widget(widget, data):
    """Populate `widget` with data from `data

    Arguments:
        widget (QListWidget): Parent view
        data (dict): Dictionary of data

    """

    widget.clear()
    _fill_item(widget.invisibleRootItem(), data)
