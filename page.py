# -*- coding: utf-8 -*-
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
import os

from random import uniform

from utils.gplay import play_audio_from_file

from gettext import gettext as _
import logging
_logger = logging.getLogger('infused-activity')

try:
    from sugar.graphics import style
    GRID_CELL_SIZE = style.GRID_CELL_SIZE
except ImportError:
    GRID_CELL_SIZE = 0

from genpieces import generate_card
from utils.sprites import Sprites, Sprite

# TODO: Generalize all these special cases across levels
# TRANS: e.g., This yellow sign is said u like up.
MSGS = [[_('This %s sign is said\n'), '%s ' + _('like') + ' %s.'],
        [_('This %s sign is said\ntogether with other sounds\nas in:\n'),
         '%s'],
        [_('This %s sign is\nlightly said\n'), '%s ' + _('like') + ' %s.'],
        [_('When it looks like this\n\n\n\n\n\nwe read it the same way.'), ''],
        [_('This %s sign is said\n\nReading from left to right, read the\n\
sounds one at a time. You can\nuse your finger to follow along.'),
         '%s ' + _('like') + ' %s.']]
MSG_INDEX = [4, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 2, -1, -1]
SHOW_MSG2 = [False, False, False, False, False, False, True, True, True,
              True, True, True, True, False, False, False]
ALIGN = 11  # Beginning with Card 11, start left-justifying the text

# Rendering-related constants
KERN = {'i': 0.6, 'I': 0.6, 'l': 0.6, 't': 0.8, 'T': 0.8, 'r': 0.8, 'm': 1.6,
        'w': 1.3, "'": 0.4, 'M': 1.6}
ALPHABET = "abcdefghijklmnopqrstuvwxyz.,'!"


class Page():

    def __init__(self, canvas, path, level, parent=None):
        self._activity = parent

        # Starting from command line
        if self._activity is None:
            self._sugar = False
            self._canvas = canvas
        else:
            self._sugar = True
            self._canvas = canvas
            self._activity.show_all()

        self._canvas.set_flags(gtk.CAN_FOCUS)
        self._canvas.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self._canvas.add_events(gtk.gdk.BUTTON_RELEASE_MASK)
        self._canvas.connect("expose-event", self._expose_cb)
        self._canvas.connect("button-press-event", self._button_press_cb)
        self._canvas.connect("button-release-event", self._button_release_cb)
        self._canvas.connect("key_press_event", self._keypress_cb)
        self._width = gtk.gdk.screen_width()
        self._height = gtk.gdk.screen_height() - GRID_CELL_SIZE
        self._scale = self._width / 240.
        self._left = int((self._width - self._scale * 60) / 2.)
        self._sprites = Sprites(self._canvas)
        self.page = 0
        self._cards = []
        self._double_cards = []
        self._letters = []
        self._colored_letters = []
        self._press = None
        self._release = None
        self.gplay = None
        self._x = 10
        self._y = 10
        self._final_x = 0
        self._offset = int(self._width / 30.)
        self._looking_at_word_list = False

        self._background = Sprite(self._sprites, 0, 0, svg_str_to_pixbuf(
                generate_card(string='', colors=['#FFFFFF', '#FFFFFF'],
                              scale=self._scale * 4)))
        self._background.set_layer(1)
        self._background.set_label_attributes(32)
        self._page_2 = Sprite(self._sprites, 0, self._height,
                                  svg_str_to_pixbuf(
                generate_card(string='', colors=['#FFFFFF', '#FFFFFF'],
                              scale=self._scale * 4)))
        self._page_2.set_layer(1)
        self._page_2.set_label_attributes(32, vert_align='top')
        self._like_card = Sprite(self._sprites, 0, int(self._height * 4 / 5.0),
                                gtk.gdk.Pixmap(self._canvas.window,
                                               self._width,
                                               int(self._height / 10.0), -1))
        self._like_card.set_layer(2)
        self._like_gc = self._like_card.images[0].new_gc()
        self._my_canvas = Sprite(self._sprites, 0, 0,
                                gtk.gdk.Pixmap(self._canvas.window,
                                               self._width,
                                               self._height * 2, -1))
        self._my_canvas.set_layer(0)
        self._my_gc = self._my_canvas.images[0].new_gc()
        self._my_gc.set_foreground(
            self._my_gc.get_colormap().alloc_color('#FFFFFF'))

        for c in ALPHABET:
            self._letters.append(Sprite(self._sprites, 0, 0,
                svg_str_to_pixbuf(generate_card(string=c,
                                                colors=['#000000', '#000000'],
                                                background=False))))

        self.load_level(path, level)
        self.new_page()

    def page_list(self):
        ''' Index into all the cards in the form of a list of phrases '''
        # Already here? Then jump back to current page.
        if self._looking_at_word_list:
            self.new_page()
            return

        save_page = self.page
        self._clear_all()

        if self._sugar:
            self._activity.status.set_label(
                _('Select a page.'))
        rect = gtk.gdk.Rectangle(0, 0, self._width, self._height * 2)
        self._my_canvas.images[0].draw_rectangle(self._my_gc, True, *rect)
        self.invalt(0, 0, self._width, self._height)
        self._my_canvas.set_layer(1)
        p = 0

        self._x, self._y = 10, 10

        # Each list is a collection of phrases, separated by spaces
        for i, card in enumerate(self._card_level_data):
            if card[0] == '':
                break
            if card[0] in 'AEIOUY':
                connector = ' ' + _('like') + ' '
            else:
                connector = ' ' + _('as-in') + ' '
            if i < len(self._colored_letters):
                self.page = i
                self._render_phrase(card[0] + connector +card[1],
                                    self._my_canvas, self._my_gc)
            else:
                self._render_phrase(
                    card[0].lower() + connector + card[1].lower(),
                    self._my_canvas, self._my_gc)

            self._x = 10
            self._y += 40

        self.page = save_page
        self._looking_at_word_list = True

    def new_page(self, saved_state=None, deck_index=0):
        ''' Load a new page. '''
        if self.page == len(self._word_level_data):
            self.page = 0
            if self._sugar:
                self._activity.status.set_label('')
        if self.page == len(self._cards) and \
           self.page < len(self._card_level_data):
            self._cards.append(Sprite(self._sprites, self._left,
                                      GRID_CELL_SIZE,
                                      svg_str_to_pixbuf(generate_card(
                            string=self._card_level_data[self.page][0].lower(),
                            colors=[self._color_level_data[self.page][0],
                                    '#000000'],
                            scale=self._scale,
                            center=True))))
            self._double_cards.append(Sprite(self._sprites, self._left,
                                             self._height + GRID_CELL_SIZE * 2,
                                             svg_str_to_pixbuf(generate_card(
                            string=self._card_level_data[self.page][0].lower()\
                                + self._card_level_data[self.page][0].lower(),
                            colors=[self._color_level_data[self.page][0],
                                    '#000000'],
                            scale=self._scale,
                            font_size=32,
                            center=True))))
            if self._color_level_data[self.page][2]:
                stroke = True
            else:
                stroke = False
            self._colored_letters.append(Sprite(self._sprites, 0, 0,
                                                svg_str_to_pixbuf(generate_card(
                            string=self._card_level_data[self.page][0].lower(),
                            colors=[self._color_level_data[self.page][0],
                                    '#000000'],
                            background=False, stroke=stroke))))

            if self._sugar:
                self._activity.status.set_label('')

        for c in self._cards:
            c.set_layer(0)
        for c in self._double_cards:
            c.set_layer(0)
        if MSG_INDEX[self.page] < 0:
            self._background.set_label('')
            self._like_card.set_layer(0)
            self.read()
        else:
            self._load_card()
        self._looking_at_word_list = False

    def _load_card(self):
        self._cards[self.page].set_layer(2)

        if MSG_INDEX[self.page] == 1:
            self._background.set_label(MSGS[1][0] % (
                    self._color_level_data[self.page][1]))
        else:
            self._background.set_label(MSGS[MSG_INDEX[self.page]][0] % \
                                     (self._color_level_data[self.page][1]))
        self._background.set_layer(1)
        self._page_2.set_layer(1)

        rect = gtk.gdk.Rectangle(0, 0, self._width, int(self._height / 10.0))
        self._like_card.images[0].draw_rectangle(self._my_gc, True, *rect)
        self.invalt(0, 0, self._width, int(self._height / 10.0))
        self._x = 0
        self._y = 0
        if MSG_INDEX[self.page] == 1:
            self._render_phrase(MSGS[1][1] % (
                    self._card_level_data[self.page][1]),
                                self._like_card, self._like_gc)
            self._like_card.move((int((self._width - self._final_x) / 2.0),
                                 int(4 * self._height / 5.0)))
        else:
            self._render_phrase(MSGS[MSG_INDEX[self.page]][1] % \
                                    (self._card_level_data[self.page][0],
                                     self._card_level_data[self.page][1]),
                                self._like_card, self._like_gc)
            self._like_card.move((int((self._width - self._final_x) / 2.0),
                                 int(3 * self._height / 5.0)))
        self._like_card.set_layer(1)

        if SHOW_MSG2[self.page]:
            self._page_2.set_label(MSGS[3][0])
            self._double_cards[self.page].set_layer(2)
        else:
            self._page_2.set_label('')

        # Hide all the letter sprites.
        for l in self._letters:
            l.set_layer(0)
        for l in self._colored_letters:
            l.set_layer(0)
        self._my_canvas.set_layer(0)

    def reload(self):
        if MSG_INDEX[self.page] >= 0:
            self._load_card()
        else:
            self.read()
        if self._sugar:
            self._activity.status.set_label('')

    def read(self):
        for c in self._cards:
            c.set_layer(0)
        for c in self._double_cards:
            c.set_layer(0)
        self._background.set_label('')
        self._background.set_layer(0)
        self._like_card.set_layer(0)
        self._page_2.set_layer(0)

        '''
        if self._sugar:
            self._activity.status.set_label(
                _('Read the sounds one at a time.'))
        '''
        rect = gtk.gdk.Rectangle(0, 0, self._width, self._height * 2)
        self._my_canvas.images[0].draw_rectangle(self._my_gc, True, *rect)
        self.invalt(0, 0, self._width, self._height)
        self._my_canvas.set_layer(1)
        p = 0
        my_list = self._word_level_data[self.page].split('/')

        # Some pages are aligned left
        if self.page > ALIGN:
            self._x, self._y = 10, 10
        else:
            self._x, self._y = self._xy(0)

        # Each list is a collection of phrases, separated by spaces
        for phrase in my_list:
            self._render_phrase(phrase, self._my_canvas, self._my_gc)

            # Put a long space between each phrase
            if self.page > ALIGN:
                self._x += self._offset
            else:
                self._x += int(uniform(30, self._width / 8))
            if self._x > self._width * 7 / 8.0:
                self._x, self._y = self._xy(self._y)

        self._looking_at_word_list = False

    def _render_phrase(self, phrase, canvas, gc):
        # The words in the list are separated by dashes
        words = phrase.split()
        for word in words:
            # Will word run off the right edge?
            if self._x + len(word) * self._offset > self._width - 20:
                self._x, self._y = self._xy(self._y)

            # Process each character in the word
            for c in range(len(word)):
                if MSG_INDEX[self.page] >= 0 and \
                   word[c] == self._card_level_data[self.page][0]:
                    self._draw_pixbuf(
                        self._colored_letters[self.page].images[0],
                        self._x, self._y, canvas, gc)
                else:
                    if word[c] in ALPHABET:
                        i = ALPHABET.index(word[c])
                        self._draw_pixbuf(self._letters[i].images[0],
                                          self._x, self._y, canvas, gc)
                if word[c] in KERN:
                    self._x += self._offset * KERN[word[c]]
                else:
                    self._x += self._offset

            self._final_x = self._x
            # Put a space after each word
            if self._x > 10:
                self._x += int(self._offset / 1.6)

    def _draw_pixbuf(self, pixbuf, x, y, canvas, gc):
        w = pixbuf.get_width()
        h = pixbuf.get_height()
        canvas.images[0].draw_pixbuf(gc, pixbuf, 0, 0,
                                             int(x), int(y))
        self.invalt(x, y, w, h)

    def _xy(self, y):
        if self.page > ALIGN:
            return 10, int(self._height / 10.0) + y
        else:
            return int(uniform(40, self._width / 8.0)), \
                   int(uniform(40, self._height / 10.0)) + y

    def _button_press_cb(self, win, event):
        win.grab_focus()
        x, y = map(int, event.get_coords())

        if self._looking_at_word_list:
            self._goto_page = int(y / 40.)
        else:
            spr = self._sprites.find_sprite((x, y))
            self._press = spr
            self._release = None
        return True

    def _button_release_cb(self, win, event):
        win.grab_focus()

        if self._looking_at_word_list:
            self._looking_at_word_list = False
            if self._goto_page > self.page:
                for _i in range(self._goto_page - self.page):
                    self.page += 1
                    self.new_page()
            else:
                self.page = self._goto_page
                self.new_page()
            if self._sugar:
                self._activity.status.set_label(_(''))
        else:
            x, y = map(int, event.get_coords())
            spr = self._sprites.find_sprite((x, y))
            if spr == self._cards[self.page]:
                if MSG_INDEX[self.page] >= 0:
                    if os.path.exists(os.path.join(
                            os.path.abspath('.'), 'sounds',
                            self._sound_level_data[self.page][0])):
                        play_audio_from_file(self, os.path.join(
                                os.path.abspath('.'), 'sounds',
                                self._sound_level_data[self.page][0]))
                    else:
                        os.system('espeak "%s" --stdout | aplay' % \
                                      (self._sound_level_data[self.page][1]))

    def _game_over(self, msg=_('Game over')):
        if self._sugar:
            self._activity.status.set_label(msg)

    def _keypress_cb(self, area, event):
        return True

    def _expose_cb(self, win, event):
        self._sprites.redraw_sprites()
        return True

    def _destroy_cb(self, win, event):
        gtk.main_quit()

    def invalt(self, x, y, w, h):
        """ Mark a region for refresh """
        self._canvas.window.invalidate_rect(
            gtk.gdk.Rectangle(int(x), int(y), int(w), int(h)), False)

    def load_level(self, path, level):
        ''' Load a level from the lessons subdirectory '''
        self._card_level_data = []
        self._color_level_data = []
        self._sound_level_data = []
        f = file(os.path.join(path, 'cards' + '.' + level), 'r')
        for line in f:
            if len(line) > 0 and line[0] != '#':
                word = line.split()
                self._card_level_data.append([word[0], word[1]])
                if word[4] == 'False':
                    self._color_level_data.append([word[2], word[3], False])
                else:
                    self._color_level_data.append([word[2], word[3], True])
                self._sound_level_data.append([word[5], word[6]])
        f.close()

        self._word_level_data = []
        f = file(os.path.join(path, 'words' + '.' + level), 'r')
        for line in f:
            if len(line) > 0 and line[0] != '#':
                self._word_level_data.append(line)
        f.close()

        self._clear_all()
        self._cards = []
        self._double_cards = []
        self._colored_letters = []

    def _clear_all(self):
        for c in self._cards:
            c.set_layer(0)
        for c in self._double_cards:
            c.set_layer(0)
        self._background.set_label('')
        self._background.set_layer(0)
        self._like_card.set_layer(0)
        self._page_2.set_layer(0)

def svg_str_to_pixbuf(svg_string):
    ''' Load pixbuf from SVG string '''
    pl = gtk.gdk.PixbufLoader('svg')
    pl.write(svg_string)
    pl.close()
    pixbuf = pl.get_pixbuf()
    return pixbuf
