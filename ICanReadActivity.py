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

from sugar.activity import activity
try:
    from sugar.graphics.toolbarbox import ToolbarBox, ToolbarButton
    _HAVE_TOOLBOX = True
except ImportError:
    _HAVE_TOOLBOX = False

if _HAVE_TOOLBOX:
    from sugar.activity.widgets import ActivityToolbarButton
    from sugar.activity.widgets import StopButton

from sugar.graphics.toolbutton import ToolButton
from sugar.graphics.combobox import ComboBox
from sugar.graphics.toolcombobox import ToolComboBox
from sugar.datastore import datastore
from sugar import profile

from gettext import gettext as _
import os.path

from page import Page
from utils.grecord import Grecord
from utils.play_audio import play_audio_from_file

SERVICE = 'org.sugarlabs.ICanReadActivity'
IFACE = SERVICE
PATH = '/org/sugarlabs/ICanReadActivity'


def _button_factory(icon_name, tooltip, callback, toolbar, cb_arg=None,
                    accelerator=None):
    ''' Factory for making toolbar buttons '''
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
    ''' Factory for adding a label to a toolbar '''
    my_label = gtk.Label(label)
    my_label.set_line_wrap(True)
    my_label.show()
    toolitem = gtk.ToolItem()
    toolitem.add(my_label)
    toolbar.insert(toolitem, -1)
    toolitem.show()
    return my_label


def _combo_factory(options, tooltip, toolbar, callback, default=0):
    ''' Combo box factory '''
    combo = ComboBox()
    if hasattr(combo, 'set_tooltip_text'):
        combo.set_tooltip_text(tooltip)
    combo.connect('changed', callback)
    for i, option in enumerate(options):
        combo.append_item(i, option.replace('-', ' '), None)
    combo.set_active(default)
    combo.show()
    tool = ToolComboBox(combo)
    tool.show()
    toolbar.insert(tool, -1)
    return combo


def _separator_factory(toolbar, visible=True, expand=False):
    ''' Factory for adding a separator to a toolbar '''
    separator = gtk.SeparatorToolItem()
    separator.props.draw = visible
    separator.set_expand(expand)
    toolbar.insert(separator, -1)
    separator.show()


def chooser(parent_window, filter, action):
    ''' Choose an object from the datastore and take some action '''
    from sugar.graphics.objectchooser import ObjectChooser

    _chooser = None
    try:
        _chooser = ObjectChooser(parent=parent_window, what_filter=filter)
    except TypeError:
        _chooser = ObjectChooser(None, parent_window,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
    if _chooser is not None:
        try:
            result = _chooser.run()
            if result == gtk.RESPONSE_ACCEPT:
                dsobject = _chooser.get_selected_object()
                action(dsobject)
                dsobject.destroy()
        finally:
            _chooser.destroy()
            del _chooser


class ICanReadActivity(activity.Activity):
    ''' ICanRead Reading guide '''

    def __init__(self, handle):
        ''' Initialize the toolbars and the reading board '''
        super(ICanReadActivity, self).__init__(handle)
        self.reading = False
        self.testing = False
        self.recording = False
        self.grecord = None
        self.datapath = get_path(activity, 'instance')

        if 'LANG' in os.environ:
            language = os.environ['LANG'][0:2]
        elif 'LANGUAGE' in os.environ:
            language = os.environ['LANGUAGE'][0:2]
        else:
            language = 'es'  # default to Spanish

        # FIXME: find some reasonable default situation
        language = 'es'

        if os.path.exists(os.path.join('~', 'Activities', 'ICanRead.activity')):
            self._lessons_path = os.path.join('~', 'Activities',
                                              'ICanRead.activity',
                                              'lessons', language)
        else:
            self._lessons_path = os.path.join('.', 'lessons', language)

        self._images_path = self._lessons_path.replace('lessons', 'images')
        self._sounds_path = self._lessons_path.replace('lessons', 'sounds')
        self._setup_toolbars()

        # Create a canvas
        self.scrolled_window = gtk.ScrolledWindow()
        self.set_canvas(self.scrolled_window)
        self.scrolled_window.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.scrolled_window.show()
        canvas = gtk.DrawingArea()
        width = gtk.gdk.screen_width()
        height = int(gtk.gdk.screen_height() * 2.75)
        canvas.set_size_request(width, height)
        self.scrolled_window.add_with_viewport(canvas)
        canvas.show()

        self._level = self._levels_combo.get_active()
        self._page = Page(canvas, self._lessons_path,
                          self._images_path, self._sounds_path,
                          self._levels[self._level],
                          parent=self)

        # Restore state from Journal or start new session
        if 'page' in self.metadata:
            self._restore()
        else:
            self._page.new_page()

        # Set up sound combo box
        self._reload_sound_combo()
        self._selected_sound = self.sounds_combo.get_active()


    def _setup_toolbars(self):
        ''' Setup the toolbars.. '''

        # no sharing
        self.max_participants = 1

        if _HAVE_TOOLBOX:
            toolbox = ToolbarBox()

            # Activity toolbar
            activity_button = ActivityToolbarButton(self)

            toolbox.toolbar.insert(activity_button, 0)
            activity_button.show()

            lesson_toolbar = gtk.Toolbar()
            lesson_toolbar_button = ToolbarButton(label=_('Select a lesson'),
                                                page=lesson_toolbar,
                                                icon_name='text-x-generic')
            record_toolbar = gtk.Toolbar()
            record_toolbar_button = ToolbarButton(label=_('Record a sound'),
                                                page=record_toolbar,
                                                icon_name='media-audio')

            self.set_toolbar_box(toolbox)
            toolbox.show()
            lesson_toolbar_button.show()
            toolbox.toolbar.insert(lesson_toolbar_button, -1)
            record_toolbar_button.show()
            toolbox.toolbar.insert(record_toolbar_button, -1)
            primary_toolbar = toolbox.toolbar

        else:
            # Use pre-0.86 toolbar design
            primary_toolbar = gtk.Toolbar()
            lesson_toolbar = gtk.Toolbar()
            record_toolbar = gtk.Toolbar()
            toolbox = activity.ActivityToolbox(self)
            self.set_toolbox(toolbox)
            toolbox.add_toolbar(_('Page'), primary_toolbar)
            toolbox.show()
            toolbox.add_toolbar(_('Lesson'), lesson_toolbar)
            toolbox.show()
            toolbox.add_toolbar(_('Record'), record_toolbar)
            toolbox.show()
            toolbox.set_current_toolbar(1)

            # no sharing
            if hasattr(toolbox, 'share'):
                toolbox.share.hide()
            elif hasattr(toolbox, 'props'):
                toolbox.props.visible = False

        _label_factory(_('Select a lesson') + ':', lesson_toolbar)
        self._levels = self._get_levels(self._lessons_path)
        self._levels_combo = _combo_factory(self._levels, _('Select a lesson'),
                                            lesson_toolbar, self._levels_cb)

        _separator_factory(lesson_toolbar)

        self._lesson_button = _button_factory(
            'load-from-journal', _('Load a new lesson from the Journal'),
            self._lesson_cb, lesson_toolbar)

        _separator_factory(lesson_toolbar)

        self._create_lesson_button = _button_factory(
            'view-source-insensitive', _('Create a new lesson'),
            self._create_lesson_cb, lesson_toolbar)

        self._save_lesson_button = _button_factory(
            'save-to-journal-insensitive', _('Nothing to save'),
            self._save_lesson_cb, lesson_toolbar)

        self._sounds = self._get_sounds()
        self.sounds_combo = _combo_factory(self._sounds, _('Record a sound'),
                                            record_toolbar, self._sounds_cb)

        _separator_factory(record_toolbar)

        _label_factory(_('Record a sound') + ':', record_toolbar)
        self._record_lesson_button = _button_factory(
            'media-record', _('Start recording'),
            self._record_lesson_cb, record_toolbar)

        _separator_factory(record_toolbar)

        self._playback_button = _button_factory(
            'media-playback-start-insensitive', _('Nothing to play'),
            self._playback_recording_cb, record_toolbar)

        self._save_recording_button = _button_factory(
            'sound-save-insensitive', _('Nothing to save'),
            self._save_recording_cb, record_toolbar)

        _separator_factory(primary_toolbar)

        self._list_button = _button_factory(
            'letter-list', _('Letter list'), self._list_cb,
            primary_toolbar)

        self._prev_page_button = _button_factory(
            'previous-letter-insensitive', _('Previous letter'),
            self._prev_page_cb, primary_toolbar)

        self._next_page_button = _button_factory(
            'next-letter', _('Next letter'), self._next_page_cb,
            primary_toolbar)

        _separator_factory(primary_toolbar)

        self._read_button = _button_factory(
            'read', _('Read the sounds one at a time'),
            self._read_cb, primary_toolbar)

        _separator_factory(primary_toolbar)

        self._test_button = _button_factory('go-right', _('Self test'),
            self._test_cb, primary_toolbar)

        self.status = _label_factory('', primary_toolbar)

        if _HAVE_TOOLBOX:
            _separator_factory(toolbox.toolbar, False, True)

            stop_button = StopButton(self)
            stop_button.props.accelerator = '<Ctrl>q'
            toolbox.toolbar.insert(stop_button, -1)
            stop_button.show()
        lesson_toolbar.show()
        record_toolbar.show()

    def _levels_cb(self, combobox=None):
        ''' The combo box has changed. '''
        if hasattr(self, '_levels_combo'):
            i = self._levels_combo.get_active()
            if i != -1 and i != self._level:
                self._level = i
                # TODO: levels stored in Journal have a different path
                try:
                    self._page.load_level(os.path.join(
                            self._lessons_path,
                            self._levels[self._level] + '.csv'))
                except IndexError:
                    print "couldn't restore level %s" % (self.metadata['level'])
                    self._levels_combo.set_active(0)
            self._page.page = 0
            self._page.new_page()
            print 'reloading sound combo box with level sounds'
            self._reload_sound_combo()
            self._selected_sound = self.sounds_combo.get_active()
        return

    def _lesson_cb(self, button=None):
        ''' Chose a lesson file from the Sugar Journal. '''
        chooser(self, '', self._load_lesson)
        return

    def _create_lesson_cb(self, button=None):
        ''' Chose a lesson file from the Sugar Journal. '''
        # Do something here:
        #    We need a place to add and edit text
        #    We need a place to select phonemes and assign colors
        return

    def _save_lesson_cb(self, button=None):
        ''' Save a lesson file to the Sugar Journal. '''
        if self._nothing_to_save:
            return
        # Do something here
        return

    def _sounds_cb(self, combobox=None):
        ''' The combo box has changed. '''
        if hasattr(self, 'sounds_combo'):
            self._selected_sound = self.sounds_combo.get_active()

    def _list_cb(self, button=None):
        ''' Letter list '''
        self._page.page_list()
        self.reading = False

    def _prev_page_cb(self, button=None):
        ''' Start a new letter. '''
        if self._page.page > 0:
            self._page.page -= 1
        if self._page.page == 0:
            self._prev_page_button.set_icon('previous-letter-insensitive')
        self._page.new_page()
        self.reading = False
        self.testing = False
        self._read_button.set_icon('read')
        self._read_button.set_tooltip(_('Show letter'))
        self._test_button.set_icon('go-right')
        self._test_button.set_tooltip(_('Self test'))

    def _next_page_cb(self, button=None):
        ''' Start a new letter. '''
        self._page.page += 1
        self._page.new_page()
        self.reading = False
        self.testing = False
        self._read_button.set_icon('read')
        self._read_button.set_tooltip(_('Show letter'))
        self._prev_page_button.set_icon('previous-letter')
        self._test_button.set_icon('go-right')
        self._test_button.set_tooltip(_('Self test'))

    def _read_cb(self, button=None):
        ''' Start a new page. '''
        if not self.reading:
            self.reading = True
            self.testing = False
            self._page.read()
            self._read_button.set_icon('listen')
            self._read_button.set_tooltip(_('Show letter'))
            self._test_button.set_icon('go-right')
            self._test_button.set_tooltip(_('Self test'))
        else:
            self.reading = False
            self.testing = False
            self._page.reload()
            self._read_button.set_icon('read')
            self._read_button.set_tooltip(_('Read the sounds one at a time'))
            self._test_button.set_icon('go-right')
            self._test_button.set_tooltip(_('Self test'))

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
            level = int(self.metadata['level'])
            self._level = level
            self._levels_combo.set_active(level)
            try:
                self._page.load_level(os.path.join(
                        self._lessons_path,
                        self._levels[self._level] + '.csv'))
            except IndexError:
                print "couldn't restore level %s" % (self.metadata['level'])
                self._levels_combo.set_active(0)
            self._page.page = 0
            self._page.new_page()
        if 'page' in self.metadata:
            page = int(self.metadata['page'])
            for _i in range(page):
                self._next_page_cb()

    def _get_levels(self, path):
        ''' Look for level files in lessons directory. '''
        level_files = []
        if path is not None:
            candidates = os.listdir(path)
            for filename in candidates:
                if not self._skip_this_file(filename):
                    level_files.append(filename.split('.')[0])
        level_files.reverse()
        return level_files

    def _get_sounds(self):
        ''' Look for sounds list. '''
        if hasattr(self, '_page'):
            sound_list = self._page.get_phrase_list()
            for i in range(len(sound_list)):
                sound_list[i] = sound_list[i].replace('(','')
                sound_list[i] = sound_list[i].replace(')','')
            return sound_list
        else:
            return([])

    def _reload_sound_combo(self):
        ''' Rebuild sounds combobox. '''
        self.sounds_combo.remove_all()  # Remove old list.
        self._sounds = self._get_sounds()
        for i, sound in enumerate(self._sounds):
            self.sounds_combo.append_item(i, sound.lower(), None)
        self.sounds_combo.set_active(self._page.page)

    def _record_lesson_cb(self, button=None):
        if self.grecord is None:
            self.grecord = Grecord(self)
        if self.recording:
            self.grecord.stop_recording_audio()
            self.recording = False
            self._record_lesson_button.set_icon('media-record')
            self._record_lesson_button.set_tooltip(_('Start recording'))
            self._playback_button.set_icon('media-playback-start')
            self._playback_button.set_tooltip(_('Play recording'))
            self._save_recording_button.set_icon('sound-save')
            self._save_recording_button.set_tooltip(_('Save recording'))
        else:
            self.grecord.record_audio()
            self.recording = True
            self._record_lesson_button.set_icon('media-recording')
            self._record_lesson_button.set_tooltip(_('Stop recording'))

    def _playback_recording_cb(self, button=None):
        play_audio_from_file(self._page, os.path.join(self.datapath,
                                                      'output.ogg'))
        return

    def _save_recording_cb(self, button=None):
        savename = self._sounds[self._selected_sound].lower() + '.ogg'
        if os.path.exists(os.path.join(self.datapath, 'output.ogg')):
            dsobject = datastore.create()
            dsobject.metadata['title'] = savename
            dsobject.metadata['icon-color'] = \
                profile.get_color().to_string()
            dsobject.metadata['mime_type'] = 'audio/ogg'
            dsobject.set_file_path(os.path.join(self.datapath, 'output.ogg'))
            datastore.write(dsobject)
            dsobject.destroy()
        return

    def _skip_this_file(self, filename):
        ''' Ignore tmp files '''
        if filename[0] in '#.' or filename[-1] == '~':
            return True
        return False

    def _load_lesson(self, dsobject):
        # TODO: load level and set combo to proper entry
        # save levels for latter restoring
        print dsobject.metadata['title']
        self._levels_combo.append_item(0, dsobject.metadata['title'], None)
        self._levels_combo.set_active(0)
        self._page.load_level(dsobject.file_path)
        self._page.page = 0
        self._page.new_page()
        # TO DO: reset sound combo


def get_path(activity, subpath):
    """ Find a Rainbow-approved place for temporary files. """
    try:
        return(os.path.join(activity.get_activity_root(), subpath))
    except:
        # Early versions of Sugar didn't support get_activity_root()
        return(os.path.join(
                os.environ['HOME'], ".sugar/default", SERVICE, subpath))
