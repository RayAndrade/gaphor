"""
Adapters for the Property Editor

# TODO: make all labels align top-left
# Add hidden columns for list stores where i can put the actual object
# being edited.

"""

import gtk
from gaphor.core import _, inject
from gaphor.ui.interfaces import IPropertyPage
from gaphor.diagram import items
from zope import interface, component
from gaphor import UML

class NamedItemPropertyPage(object):
    """
    An adapter which works for any named item view.

    It also sets up a table view which can be extended.
    """

    interface.implements(IPropertyPage)
    component.adapts(items.NamedItem)

    def __init__(self, context):
        self.context = context
        self.size_group = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
        
    def construct(self):
        page = gtk.VBox()
        hbox = gtk.HBox()
        page.pack_start(hbox, expand=False)

        label = gtk.Label(_('Name'))
        label.set_justify(gtk.JUSTIFY_LEFT)
        self.size_group.add_widget(label)
        hbox.pack_start(label, expand=False)
        entry = gtk.Entry()        
        entry.set_text(self.context.subject.name or '')
        entry.connect('changed', self._on_name_change)
        hbox.pack_start(entry)
        page.show_all()
        return page

    def _on_name_change(self, entry):
        self.context.subject.name = entry.get_text()
        
component.provideAdapter(NamedItemPropertyPage, name='Properties')
    
    
class ClassPropertyPage(NamedItemPropertyPage):
    """
    Adapter which shows a property page for a class view.
    """

    interface.implements(IPropertyPage)
    component.adapts(items.ClassItem)

    def __init__(self, context):
        super(ClassPropertyPage, self).__init__(context)
        
    def construct(self):
        page = super(ClassPropertyPage, self).construct()

        # Abstract toggle
        hbox = gtk.HBox()
        label = gtk.Label(_("Abstract"))
        label.set_justify(gtk.JUSTIFY_LEFT)
        self.size_group.add_widget(label)
        hbox.pack_start(label, expand=False)
        button = gtk.CheckButton()
        button.set_active(self.context.subject.isAbstract)
        button.connect('toggled', self._on_abstract_change)
        hbox.pack_start(button)
        hbox.show_all()
        page.pack_start(hbox, expand=False)

        hbox.show_all()

        page.pack_start(hbox, expand=True)

        return page

    def _on_abstract_change(self, button):
        self.context.subject.isAbstract = button.get_active()

component.provideAdapter(ClassPropertyPage, name='Properties')


class AttributesPropertyPage(object):
    """
    An editor for attributes associated with classes and interfaces

    Tagged values are stored in a ListSore: tag, value, taggedValue. taggedValue
    is an UML model element (hidden).
    """

    interface.implements(IPropertyPage)
    component.adapts(items.ClassItem)

    element_factory = inject('element_factory')

    def __init__(self, context):
        super(AttributesPropertyPage, self).__init__()
        self.context = context
        
    def construct(self):
        page = gtk.VBox()

        # Show attributes toggle
        hbox = gtk.HBox()
        label = gtk.Label(_("Show attributes"))
        label.set_justify(gtk.JUSTIFY_LEFT)
        hbox.pack_start(label, expand=False)
        button = gtk.CheckButton()
        button.set_active(self.context.show_attributes)
        button.connect('toggled', self._on_show_attributes_change)
        hbox.pack_start(button)
        hbox.show_all()
        page.pack_start(hbox, expand=False)

        # Attributes list store:
        attributes = gtk.ListStore(str, object)
        
        for attribute in self.context.subject.ownedAttribute:
            attributes.append([attribute.render(), attribute])
        attributes.append(['', None])
        
        self.attributes = attributes
        
        tree_view = gtk.TreeView(attributes)
        tree_view.set_rules_hint(True)
        
        renderer = gtk.CellRendererText()
        renderer.set_property('editable', True)
        renderer.connect("edited", self._on_cell_edited, 0)
        tag_column = gtk.TreeViewColumn('Attribute', renderer, text=0)
        tree_view.append_column(tag_column)
        
        page.pack_start(tree_view)
        tree_view.show_all()

        return page
        
    def _on_show_attributes_change(self, button):
        self.context.show_attributes = button.get_active()
        self.context.request_update()
        
    def _on_cell_edited(self, cellrenderertext, path, new_text, col):
        """
        Update the model and UML element based on fresh user input.
        """
        attr = self.attributes[path]

        iter = self.attributes.get_iter(path)

        # Delete attribute if both tag and value are empty
        if not new_text and attr[1]:
            attr[1].unlink()
            self.attributes.remove(iter)
            return

        # Add a new attribute:
        if new_text and not attr[1]:
            a = self.element_factory.create(UML.Property)
            self.context.subject.ownedAttribute = a
            attr[1] = a
            self.attributes.append(['', None])

        # Apply new_text to Attribute
        if attr[1]:
            attr[1].parse(new_text)
            attr[0] = attr[1].render()

component.provideAdapter(AttributesPropertyPage, name='Attributes')


class OperationsPropertyPage(object):
    """
    An editor for operations associated with classes and interfaces

    Tagged values are stored in a ListSore: tag, value, taggedValue. taggedValue
    is an UML model element (hidden).
    """

    interface.implements(IPropertyPage)
    component.adapts(items.ClassItem)

    element_factory = inject('element_factory')

    def __init__(self, context):
        super(OperationsPropertyPage, self).__init__()
        self.context = context
        
    def construct(self):
        page = gtk.VBox()

        # Show operations toggle
        hbox = gtk.HBox()
        label = gtk.Label(_("Show operations"))
        label.set_justify(gtk.JUSTIFY_LEFT)
        hbox.pack_start(label, expand=False)
        button = gtk.CheckButton()
        button.set_active(self.context.show_operations)
        button.connect('toggled', self._on_show_operations_change)
        hbox.pack_start(button)
        hbox.show_all()
        page.pack_start(hbox, expand=False)

        # Operations list store:
        operations = gtk.ListStore(str, object)
        
        for operation in self.context.subject.ownedOperation:
            operations.append([operation.render(), operation])
        operations.append(['', None])
        
        self.operations = operations
        
        tree_view = gtk.TreeView(operations)
        tree_view.set_rules_hint(True)
        
        renderer = gtk.CellRendererText()
        renderer.set_property('editable', True)
        renderer.connect("edited", self._on_cell_edited, 0)
        tag_column = gtk.TreeViewColumn('Operation', renderer, text=0)
        tree_view.append_column(tag_column)
        
        page.pack_start(tree_view)
        tree_view.show_all()

        return page
        
    def _on_show_operations_change(self, button):
        self.context.show_operations = button.get_active()
        self.context.request_update()
        
    def _on_cell_edited(self, cellrenderertext, path, new_text, col):
        """
        Update the model and UML element based on fresh user input.
        """
        attr = self.operations[path]

        iter = self.operations.get_iter(path)

        # Delete operation if both tag and value are empty
        if not new_text and attr[1]:
            attr[1].unlink()
            self.operations.remove(iter)
            return

        # Add a new operation:
        if new_text and not attr[1]:
            a = self.element_factory.create(UML.Operation)
            self.context.subject.ownedOperation = a
            attr[1] = a
            self.operations.append(['', None])

        # Apply new_text to Operation
        if attr[1]:
            attr[1].parse(new_text)
            attr[0] = attr[1].render()

component.provideAdapter(OperationsPropertyPage, name='Operations')


class TaggedValuePage(object):
    """
    An editor for tagged values associated with elements.

    Tagged values are stored in a ListSore: tag, value, taggedValue. taggedValue
    is an UML model element (hidden).
    """

    interface.implements(IPropertyPage)
    component.adapts(items.NamedItem)

    element_factory = inject('element_factory')
    def __init__(self, context):
        super(TaggedValuePage, self).__init__()
        self.context = context
        
    def construct(self):
        page = gtk.VBox()

        tagged_values = gtk.ListStore(str, str, object)
        
        for tagged_value in self.context.subject.taggedValue:
            tag, value = tagged_value.value.split("=")
            tagged_values.append([tag, value, tagged_value])
        tagged_values.append(['','', None])
        
        self.tagged_values = tagged_values
        
        tree_view = gtk.TreeView(tagged_values)
        tree_view.set_rules_hint(True)
        
        renderer = gtk.CellRendererText()
        renderer.set_property('editable', True)
        renderer.connect("edited", self._on_cell_edited, 0)
        tag_column = gtk.TreeViewColumn('Tag', renderer, text=0)
        tree_view.append_column(tag_column)
        
        renderer = gtk.CellRendererText()
        renderer.set_property('editable', True)
        renderer.connect("edited", self._on_cell_edited, 1)
        
        value_column = gtk.TreeViewColumn('Value', renderer, text=1)
        tree_view.append_column(value_column)
        
        page.pack_start(tree_view)
        tree_view.show_all()
        return page
        
    def _on_cell_edited(self, cellrenderertext, path, new_text, col):
        """
        Update the model and UML element based on fresh user input.
        """
        tv = self.tagged_values[path]

        tv[col] = new_text

        iter = self.tagged_values.get_iter(path)

        # Delete tagged value if both tag and value are empty
        if not tv[0] and not tv[1] and tv[2]:
            tv[2].unlink()
            self.tagged_values.remove(iter)
        
        # Add a new tagged value:
        elif (tv[0] or tv[1]) and not tv[2]:
            tag = self.element_factory.create(UML.LiteralSpecification)
            tag.value = "%s=%s"%(tv[0], tv[1])
            self.context.subject.taggedValue.append(tag)
            tv[2] = tag
            self.tagged_values.append(['','', None])
        
component.provideAdapter(TaggedValuePage, name='Tagged values')


# vim:sw=4:et:ai
