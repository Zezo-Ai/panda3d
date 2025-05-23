"""Inspectors allow you to visually browse through the members of
various Python objects.  To open an inspector, import this module, and
execute ``inspector.inspect(anObject)``.

I start IDLE with this command line::

   idle.py -c "from inspector import inspect"

so that I can just type: ``inspect(anObject)`` any time.

See :ref:`inspection-utilities` for more information.
"""

from __future__ import annotations

__all__ = ['inspect', 'inspectorFor', 'Inspector', 'ModuleInspector', 'ClassInspector', 'InstanceInspector', 'FunctionInspector', 'InstanceMethodInspector', 'CodeInspector', 'ComplexInspector', 'DictionaryInspector', 'SequenceInspector', 'SliceInspector', 'InspectorWindow']

import Pmw
import tkinter as tk

### public API


def inspect(anObject):
    """Opens up a window for visually inspecting the details of a given Python
    object.  See :ref:`inspection-utilities`.
    """
    inspector = inspectorFor(anObject)
    inspectorWindow = InspectorWindow(inspector)
    inspectorWindow.open()
    return inspectorWindow

### private

_InspectorMap: dict[str, str]


def inspectorFor(anObject):
    typeName = type(anObject).__name__.capitalize() + 'Type'
    if typeName in _InspectorMap:
        inspectorName = _InspectorMap[typeName]
    else:
        print(("Can't find an inspector for " + typeName))
        inspectorName = 'Inspector'
    inspector = globals()[inspectorName](anObject)
    return inspector


### initializing

def initializeInspectorMap() -> None:
    global _InspectorMap
    notFinishedTypes = ['BufferType',  'EllipsisType',  'FrameType', 'TracebackType', 'XRangeType']

    _InspectorMap = {
        'Builtin_function_or_methodType': 'FunctionInspector',
        'BuiltinFunctionType': 'FunctionInspector',
        'BuiltinMethodType': 'FunctionInspector',
        'ClassType': 'ClassInspector',
        'CodeType': 'CodeInspector',
        'ComplexType': 'Inspector',
        'DictionaryType': 'DictionaryInspector',
        'DictType': 'DictionaryInspector',
        'FileType': 'Inspector',
        'FloatType': 'Inspector',
        'FunctionType': 'FunctionInspector',
        'Instance methodType': 'InstanceMethodInspector',
        'InstanceType': 'InstanceInspector',
        'IntType': 'Inspector',
        'LambdaType': 'Inspector',
        'ListType': 'SequenceInspector',
        'LongType': 'Inspector',
        'MethodType': 'FunctionInspector',
        'ModuleType': 'ModuleInspector',
        'NoneType': 'Inspector',
        'SliceType': 'SliceInspector',
        'StringType': 'SequenceInspector',
        'TupleType': 'SequenceInspector',
        'TypeType': 'Inspector',
        'UnboundMethodType': 'FunctionInspector',
    }

    for each in notFinishedTypes:
        _InspectorMap[each] = 'Inspector'


### Classes

class Inspector:
    def __init__(self, anObject):
        self.object = anObject
        self.lastPartNumber = 0
        self.initializePartsList()
        self.initializePartNames()

    def __str__(self):
        return __name__ + '(' + str(self.object) + ')'

    def initializePartsList(self):
        self._partsList = []
        for each in sorted(self.namedParts()):
            self._partsList.append(each)
            #if not callable(getattr(self.object, each)):
            #    self._partsList.append(each)

    def initializePartNames(self):
        self._partNames = ['up'] + [str(each) for each in self._partsList]

    def title(self):
        "Subclasses may override."
        return self.objectType().__name__.capitalize()

    def getLastPartNumber(self):
        return self.lastPartNumber

    def selectedPart(self):
        return self.partNumber(self.getLastPartNumber())

    def namedParts(self):
        return dir(self.object)

    def stringForPartNumber(self, partNumber):
        object = self.partNumber(partNumber)
        doc = None
        if callable(object):
            doc = getattr(object, '__doc__', None)
        if doc:
            return str(object) + '\n' + str(doc)
        else:
            return str(object)

    def partNumber(self, partNumber):
        self.lastPartNumber = partNumber
        if partNumber == 0:
            return self.object
        else:
            part = self.privatePartNumber(partNumber)
            return getattr(self.object, part)

    def inspectorFor(self, part):
        return inspectorFor(part)

    def privatePartNumber(self, partNumber):
        return self._partsList[partNumber - 1]

    def partNames(self):
        return self._partNames

    def objectType(self):
        return type(self.object)

###


class ModuleInspector(Inspector):
    def namedParts(self):
        return ['__dict__']


class ClassInspector(Inspector):
    def namedParts(self):
        return ['__bases__'] + list(self.object.__dict__.keys())

    def title(self):
        return self.object.__name__ + ' Class'


class InstanceInspector(Inspector):
    def title(self):
        return self.object.__class__.__name__

    def namedParts(self):
        return ['__class__'] + dir(self.object)

###


class FunctionInspector(Inspector):
    def title(self):
        return self.object.__name__ + "()"


class InstanceMethodInspector(Inspector):
    def title(self):
        return str(self.object.__self__.__class__) + "." + self.object.__name__ + "()"


class CodeInspector(Inspector):
    def title(self):
        return str(self.object)

###


class ComplexInspector(Inspector):
    def namedParts(self):
        return ['real', 'imag']

###


class DictionaryInspector(Inspector):

    def initializePartsList(self):
        Inspector.initializePartsList(self)
        for each in sorted(self.object):
            self._partsList.append(each)

    def partNumber(self, partNumber):
        self.lastPartNumber = partNumber
        if partNumber == 0:
            return self.object
        key = self.privatePartNumber(partNumber)
        if key in self.object:
            return self.object[key]
        else:
            return getattr(self.object, key)


class SequenceInspector(Inspector):
    def initializePartsList(self):
        Inspector.initializePartsList(self)
        for each in range(len(self.object)):
            self._partsList.append(each)

    def partNumber(self, partNumber):
        self.lastPartNumber = partNumber
        if partNumber == 0:
            return self.object
        index = self.privatePartNumber(partNumber)
        if isinstance(index, int):
            return self.object[index]
        else:
            return getattr(self.object, index)


class SliceInspector(Inspector):
    def namedParts(self):
        return ['start', 'stop', 'step']


### Initialization
initializeInspectorMap()


class InspectorWindow:
    def __init__(self, inspector):
        self.inspectors = [inspector]

    def topInspector(self):
        return self.inspectors[len(self.inspectors) - 1]

    def selectedPart(self):
        return self.topInspector().selectedPart()

    def inspectedObject(self):
        return self.topInspector().object

    def open(self):
        self.top= tk.Toplevel()
        self.top.geometry('650x315')
        self.createViews()
        self.update()

    #Private - view construction
    def createViews(self):
        self.createMenus()
        # Paned widget for dividing two halves
        self.framePane = Pmw.PanedWidget(self.top, orient = tk.HORIZONTAL)
        self.createListWidget()
        self.createTextWidgets()
        self.framePane.pack(expand = 1, fill = tk.BOTH)

    def setTitle(self):
        self.top.title('Inspecting: ' + self.topInspector().title())

    def createListWidget(self):
        listFrame = self.framePane.add('list')
        listWidget = self.listWidget = Pmw.ScrolledListBox(
            listFrame, vscrollmode = 'static')
        listWidget.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        # If you click in the list box, take focus so you can navigate
        # with the cursor keys
        listbox = listWidget.component('listbox')
        listbox.bind('<ButtonPress-1>',
                        lambda e, l = listbox: l.focus_set())
        listbox.bind('<ButtonRelease-1>',  self.listSelectionChanged)
        listbox.bind('<Double-Button-1>', self.popOrDive)
        listbox.bind('<ButtonPress-3>', self.popupMenu)
        listbox.bind('<KeyRelease-Up>',  self.listSelectionChanged)
        listbox.bind('<KeyRelease-Down>',  self.listSelectionChanged)
        listbox.bind('<KeyRelease-Left>', lambda e, s = self: s.pop())
        listbox.bind('<KeyRelease-Right>', lambda e, s = self: s.dive())
        listbox.bind('<Return>',  self.popOrDive)

    def createTextWidgets(self):
        textWidgetsFrame = self.framePane.add('textWidgets')
        self.textPane = Pmw.PanedWidget(textWidgetsFrame, orient = tk.VERTICAL)
        textFrame = self.textPane.add('text', size = 200)
        self.textWidget = Pmw.ScrolledText(
            textFrame, vscrollmode = 'static', text_state = 'disabled')
        self.textWidget.pack(fill=tk.BOTH, expand=1)
        commandFrame = self.textPane.add('command')
        self.commandWidget = Pmw.ScrolledText(
            commandFrame, vscrollmode = 'static')
        self.commandWidget.insert(1.0, '>>> ')
        self.commandWidget.pack(fill = tk.BOTH, expand = 1)
        self.commandWidget.component('text').bind(
            '<KeyRelease-Return>', self.evalCommand)
        self.textPane.pack(expand = 1, fill = tk.BOTH)

    def createMenus(self):
        self.menuBar = tk.Menu(self.top)
        self.top.config(menu=self.menuBar)
        inspectMenu = tk.Menu(self.menuBar)
        self.menuBar.add_cascade(label='Inspect', menu=inspectMenu)
        inspectMenu.add_command(label='Pop', command=self.pop)
        inspectMenu.add_command(label='Dive', command=self.dive)
        inspectMenu.add_command(label='Inspect', command=self.inspect)
        helpMenu = tk.Menu(self.menuBar)
        self.menuBar.add_cascade(label='Help', menu=helpMenu)
        helpMenu.add_command(label='Instructions', command=self.showHelp)

    def fillList(self):
        self.listWidget.delete(0, tk.END)
        for each in self.topInspector().partNames():
            self.listWidget.insert(tk.END, each)
        self.listWidget.select_clear(0)

    # Event Handling
    def listSelectionChanged(self, event):
        partNumber = self.selectedIndex()
        if partNumber is None:
            partNumber = 0
        string = self.topInspector().stringForPartNumber(partNumber)
        self.textWidget.component('text').configure(state = 'normal')
        self.textWidget.delete('1.0', tk.END)
        self.textWidget.insert(tk.END, string)
        self.textWidget.component('text').configure(state = 'disabled')

    def popOrDive(self, event):
        """The list has been double-clicked. If the selection is 'self' then pop,
        otherwise dive into the selected part"""
        if self.selectedIndex() == 0:
            self.pop()
        else:
            self.dive()

    def evalCommand(self, event):
        """Eval text in commandWidget"""
        insertPt = self.commandWidget.index(tk.INSERT)
        commandLineStart = self.commandWidget.search(
            '>>> ', tk.INSERT, backwards = 1)
        if commandLineStart:
            commandStart = self.commandWidget.index(
                commandLineStart + ' + 4 chars')
            command = self.commandWidget.get(commandStart,
                                             commandStart + ' lineend')
            if command:
                partDict = {'this': self.selectedPart(),
                            'object': self.topInspector().object}
                result = eval(command, partDict)
                self.commandWidget.insert(tk.INSERT, repr(result) + '\n>>> ')
                self.commandWidget.see(tk.INSERT)

    # Menu Events
    def inspect(self):
        inspector = self.inspectorForSelectedPart()
        if inspector is None:
            return
        InspectorWindow(inspector).open()

    def pop(self):
        if len(self.inspectors) > 1:
            self.inspectors = self.inspectors[:-1]
            self.update()

    def dive(self):
        inspector = self.inspectorForSelectedPart()
        if inspector is None:
            return
        self.inspectors.append(inspector)
        self.update()

    def update(self):
        self.setTitle()
        self.fillList()
        # What is active part in this inspector
        partNumber = self.topInspector().getLastPartNumber()
        self.listWidget.select_clear(0)
        self.listWidget.activate(partNumber)
        self.listWidget.select_set(partNumber)
        self.listSelectionChanged(None)
        # Make sure selected item is visible
        self.listWidget.see(partNumber)
        # Make sure left side of listbox visible
        self.listWidget.xview_moveto(0.0)
        # Grab focus in listbox
        self.listWidget.component('listbox').focus_set()

    def showHelp(self):
        from direct.showbase import ShowBaseGlobal
        help = tk.Toplevel(ShowBaseGlobal.base.tkRoot)
        help.title("Inspector Help")
        frame = tk.Frame(help)
        frame.pack()
        text = tk.Label(
            frame, justify = tk.LEFT,
            text = "ListBox shows selected object's attributes\nDouble click or use right arrow on an instance variable to dive down.\nDouble click self or use left arrow to pop back up.\nUse up and down arrow keys to move from item to item in the current level.\n\nValue box (upper right) shows current value of selected item\n\nCommand box (lower right) is used to evaluate python commands\nLocal variables 'object' and 'this' are defined as the current object being inspected\nand the current attribute selected."
        )
        text.pack()

    #Private
    def selectedIndex(self):
        indices = list(map(int, self.listWidget.curselection()))
        if len(indices) == 0:
            return None
        partNumber = indices[0]
        return partNumber

    def inspectorForSelectedPart(self):
        partNumber = self.selectedIndex()
        if partNumber is None:
            return None
        part = self.topInspector().partNumber(partNumber)
        return self.topInspector().inspectorFor(part)

    def popupMenu(self, event):
        print(event)
        partNumber = self.selectedIndex()
        print(partNumber)
        if partNumber is None:
            return
        part = self.topInspector().partNumber(partNumber)
        print(part)
        from panda3d.core import NodePath
        from direct.fsm import ClassicFSM
        popupMenu = None
        if isinstance(part, NodePath):
            popupMenu = self.createPopupMenu(
                part,
                [('Explore', NodePath.explore),
                 ('Place', NodePath.place),
                 ('Set Color', NodePath.rgbPanel)])
        elif isinstance(part, ClassicFSM.ClassicFSM):
            from . import FSMInspector
            popupMenu = self.createPopupMenu(
                part,
                [('Inspect ClassicFSM', FSMInspector.FSMInspector)])
        print(popupMenu)
        if popupMenu:
            popupMenu.post(event.widget.winfo_pointerx(),
                           event.widget.winfo_pointery())

    def createPopupMenu(self, part, menuList):
        popupMenu = tk.Menu(self.top, tearoff = 0)
        for item, func in menuList:
            popupMenu.add_command(
                label = item,
                command = lambda p = part, f = func: f(p))
        return popupMenu
