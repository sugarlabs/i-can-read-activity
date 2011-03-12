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
from sugar.graphics.icon import Icon
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
        super(InfusedActivity,self).__init__(handle)
        self.reading = False

        self._setup_toolbars(_have_toolbox)

        # Create a canvas
        canvas = gtk.DrawingArea()
        canvas.set_size_request(gtk.gdk.screen_width(), \
                                gtk.gdk.screen_height())
        self.set_canvas(canvas)
        canvas.show()
        self.show_all()

        self._page = Page(canvas,
                          parent=self,
                          colors= profile.get_color().to_string().split(','))

        # Restore game state from Journal or start new game
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

        self._new_page_button = _button_factory('new-page',
                                                _('Next letter'),
                                                self._new_page_cb, toolbar)

        _separator_factory(toolbar)

        self._read_button = _button_factory('media-playback-start',
                                                _('Read'),
                                                self._read_cb, toolbar)

        self.status = _label_factory(_(''), toolbar)

        if _have_toolbox:
            _separator_factory(toolbox.toolbar, False, True)

            stop_button = StopButton(self)
            stop_button.props.accelerator = '<Ctrl>q'
            toolbox.toolbar.insert(stop_button, -1)
            stop_button.show()

    def _new_page_cb(self, button=None):
        ''' Start a new letter. '''
        self._page.page_index += 1
        self._page.new_page()
        self.reading = False
        self._read_button.set_icon('media-playback-start')
        self._read_button.set_tooltip(_('Show letter'))

    def _read_cb(self, button=None):
        ''' Start a new page. '''
        if not self.reading:
            self.reading = True
            self._page.read()
            self._read_button.set_icon('system-restart')
            self._read_button.set_tooltip(_('Show letter'))
        else:
            self.reading = False
            self._page.reload()
            self._read_button.set_icon('media-playback-start')
            self._read_button.set_tooltip(_('Read'))

    def write_file(self, file_path):
        ''' Write status to the Journal '''
        if not hasattr(self, '_page'):
            return
        self.metadata['page'] = str(self._page.page_index)

    def _restore(self):
        ''' Load up cards until we get to the page we stopped on. '''
        try:
            n = int(self.metadata['page'])
        except:
            n = 0
        for i in range(n):
            self._new_page_cb()
