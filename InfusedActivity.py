#Copyright (c) 2011 Walter Bender

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

import gtk
import gobject

import sugar
from sugar.activity import activity
from sugar import profile
try:
    from sugar.graphics.toolbarbox import ToolbarBox
    _have_toolbox = True
except ImportError:
    _have_toolbox = False

if _have_toolbox:
    from sugar.bundle.activitybundle import ActivityBundle
    from sugar.activity.widgets import ActivityToolbarButton
    from sugar.activity.widgets import StopButton
    from sugar.graphics.toolbarbox import ToolbarButton

from sugar.graphics.toolbutton import ToolButton
from sugar.graphics.menuitem import MenuItem
from sugar.graphics.combobox import ComboBox
from sugar.graphics.toolcombobox import ToolComboBox
from sugar.datastore import datastore

from gettext import gettext as _
import locale
import os.path

from page import Page

SERVICE = 'org.sugarlabs.InfusedActivity'
IFACE = SERVICE
PATH = '/org/augarlabs/InfusedActivity'


def _button_factory(icon_name, tooltip, callback, toolbar, cb_arg=None,
                    accelerator=None):
    """Factory for making toolbar buttons"""
    my_button = ToolButton(icon_name)
    my_button.set_tooltip(tooltip)
    my_button.props.sensitive = True
    if accelerator is not None:
        my_button.props.accelerator = accelerator
    if cb_arg is not None:
        my_button.connect('clicked', callback, cb_arg)
    else:
        my_button.connect('clicked', callback)
    if hasattr(toolbar, 'insert'):  # the main toolbar
        toolbar.insert(my_button, -1)
    else:  # or a secondary toolbar
        toolbar.props.page.insert(my_button, -1)
    my_button.show()
    return my_button


def _label_factory(label, toolbar):
    """ Factory for adding a label to a toolbar """
    my_label = gtk.Label(label)
    my_label.set_line_wrap(True)
    my_label.show()
    toolitem = gtk.ToolItem()
    toolitem.add(my_label)
    toolbar.insert(toolitem, -1)
    toolitem.show()
    return my_label


def _combo_factory(options, tooltip, toolbar, callback, default=0):
    """ Combo box factory """
    combo = ComboBox()
    if hasattr(combo, 'set_tooltip_text'):
        combo.set_tooltip_text(tooltip)
    combo.connect('changed', callback)
    for i, o in enumerate(options):
        combo.append_item(i, o, None)
    combo.set_active(default)
    tool = ToolComboBox(combo)
    toolbar.insert(tool, -1)
    return combo


def _separator_factory(toolbar, visible=True, expand=False):
    """ Factory for adding a separator to a toolbar """
    separator = gtk.SeparatorToolItem()
    separator.props.draw = visible
    separator.set_expand(expand)
    toolbar.insert(separator, -1)
    separator.show()


class InfusedActivity(activity.Activity):
    """ Infused Reading guide """

    def __init__(self, handle):
        """ Initialize the toolbars and the reading board """
        super(InfusedActivity, self).__init__(handle)
        self.reading = False
        self.testing = False

        if 'LANG' in os.environ:
            language = os.environ['LANG'][0:2]
        elif 'LANGUAGE' in os.environ:
            language = os.environ['LANGUAGE'][0:2]
        else:
            language = 'en'
        if os.path.exists(os.path.join('~', 'Activities', 'Infused.activity')):
            self._path = os.path.join('~', 'Activities', 'Infused.activity',
                                      'lessons', language)
        else:
            self._path = os.path.join('.', 'lessons', language)

        self._setup_toolbars(_have_toolbox)

        # Create a canvas
        self.sw = gtk.ScrolledWindow()
        self.set_canvas(self.sw)
        self.sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.sw.show()
        canvas = gtk.DrawingArea()
        width = gtk.gdk.screen_width()
        height = gtk.gdk.screen_height() * 2
        canvas.set_size_request(width, height)
        self.sw.add_with_viewport(canvas)
        canvas.show()

        self._level = self._levels_combo.get_active()
        self._page = Page(canvas, self._path, self._levels[self._level],
                          parent=self)

        # Restore state from Journal or start new session
        if 'page' in self.metadata:
            self._restore()
        else:
            self._page.new_page()

    def _setup_toolbars(self, have_toolbox):
        """ Setup the toolbars.. """

        # no sharing
        self.max_participants = 1

        if have_toolbox:
            toolbox = ToolbarBox()

            # Activity toolbar
            activity_button = ActivityToolbarButton(self)

            toolbox.toolbar.insert(activity_button, 0)
            activity_button.show()

            self.set_toolbar_box(toolbox)
            toolbox.show()
            toolbar = toolbox.toolbar

        else:
            # Use pre-0.86 toolbar design
            games_toolbar = gtk.Toolbar()
            toolbox = activity.ActivityToolbox(self)
            self.set_toolbox(toolbox)
            toolbox.add_toolbar(_('Page'), page_toolbar)
            toolbox.show()
            toolbox.set_current_toolbar(1)
            toolbar = page_toolbar

            # no sharing
            if hasattr(toolbox, 'share'):
                toolbox.share.hide()
            elif hasattr(toolbox, 'props'):
                toolbox.props.visible = False

        self._levels = self._get_levels(self._path)
        self._levels_combo = _combo_factory(self._levels, _('Select lesson'),
                                            toolbar, self._levels_cb)

        _separator_factory(toolbar)

        self._list_button = _button_factory(
            'format-justify-fill', _('Letter list'), self._list_cb, toolbar)

        _separator_factory(toolbar)

        self._prev_page_button = _button_factory(
            'list-remove', _('Previous letter'), self._prev_page_cb, toolbar)

        self._next_page_button = _button_factory(
            'list-add', _('Next letter'), self._next_page_cb, toolbar)

        _separator_factory(toolbar)

        self._read_button = _button_factory(
            'go-down', _('Read the sounds one at a time.'),
            self._read_cb, toolbar)

        _separator_factory(toolbar)

        self._test_button = _button_factory('go-right', _('Self test'),
            self._test_cb, toolbar)

        self.status = _label_factory('', toolbar)

        if _have_toolbox:
            _separator_factory(toolbox.toolbar, False, True)

            stop_button = StopButton(self)
            stop_button.props.accelerator = '<Ctrl>q'
            toolbox.toolbar.insert(stop_button, -1)
            stop_button.show()

    def _levels_cb(self, combobox=None):
        """ The combo box has changed. """
        if hasattr(self, '_levels_combo'):
            i = self._levels_combo.get_active()
            if i != -1 and i != self._level:
                self._level = i
                self._page.load_level(self._path, self._levels[self._level])
            self._page.page = 0
            self._page.new_page()
        return

    def _list_cb(self, button=None):
        ''' Letter list '''
        self._page.page_list()
        self.reading = False

    def _prev_page_cb(self, button=None):
        ''' Start a new letter. '''
        if self._page.page > 0:
            self._page.page -= 1
        self._page.new_page()
        self.reading = False
        self.testing = False
        self._read_button.set_icon('go-down')
        self._read_button.set_tooltip(_('Show letter'))

    def _next_page_cb(self, button=None):
        ''' Start a new letter. '''
        self._page.page += 1
        self._page.new_page()
        self.reading = False
        self.testing = False
        self._read_button.set_icon('go-down')
        self._read_button.set_tooltip(_('Show letter'))

    def _read_cb(self, button=None):
        ''' Start a new page. '''
        if not self.reading:
            self.reading = True
            self.testing = False
            self._page.read()
            self._read_button.set_icon('go-up')
            self._read_button.set_tooltip(_('Show letter'))
        else:
            self.reading = False
            self.testing = False
            self._page.reload()
            self._read_button.set_icon('go-down')
            self._read_button.set_tooltip(_('Read the sounds one at a time.'))

    def _test_cb(self, button=None):
        ''' Start a test. '''
        if not self.testing:
            self.testing = True
            self._page.test()
            self._test_button.set_icon('go-left')
            self._test_button.set_tooltip(_('Return to reading'))
        else:
            self.testing = False
            self._page.reload()
            self._test_button.set_icon('go-right')
            self._test_button.set_tooltip(_('Self test'))

    def write_file(self, file_path):
        ''' Write status to the Journal '''
        if not hasattr(self, '_page'):
            return
        self.metadata['page'] = str(self._page.page)
        self.metadata['level'] = str(self._level)

    def _restore(self):
        ''' Load up cards until we get to the page we stopped on. '''
        if 'level' in self.metadata:
            n = int(self.metadata['level'])
            self._level = n
            self._levels_combo.set_active(n)
            self._page.load_level(self._path, self._levels[self._level])
            self._page.page = 0
            self._page.new_page()
        if 'page' in self.metadata:
            n = int(self.metadata['page'])
            for i in range(n):
                self._next_page_cb()

    def _get_levels(self, path):
        """ Look for level files in lessons directory. """

        level_files = []
        if path is not None:
            candidates = os.listdir(path)
            for c in candidates:
                if c[0:6] == 'cards.' and c[0] != '#' and c[0] != '.' and \
                        c[-1] != '~':
                    level_files.append(c.split('.')[1])
        return level_files
