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

from gplay import play_audio_from_file

from gettext import gettext as _
import logging
_logger = logging.getLogger('infused-activity')

try:
    from sugar.graphics import style
    GRID_CELL_SIZE = style.GRID_CELL_SIZE
except ImportError:
    GRID_CELL_SIZE = 0

from genpieces import generate_card
from sprites import Sprites, Sprite

CARDS = [['a', _('pat')],
         ['u', _('up')],
         ['I', _('It')],
         ['E', _('pEt')],
         ['o', _('pot')],
         ['y', _('tummy')],
         ['p', _('pat')],
         ['n', _('not, tennis')],
         ['t', _('tap')],
         ['d', _('dad')],
         ['s', _('is, as, was, says')],
         ['m', _('mom')],
         ['s', _("sam, stop, it's")],
         ['A', _('read A book')],
         ['.', ''],
         ['.', '']]


COLORS = [['#FFB0B0', _('light pink')],
          ['#FFFF80', _('yellow')],
          ['#FF6060', _('pink')],
          ['#8080FF', _('blue')],
          ['#FFFFFF', _('white')],
          ['#FF0000', _('red')],
          ['#A00000', _('brown')],
          ['#A000A0', _('purple')],
          ['#A08080', _('dark pink')],
          ['#00A000', _('green')],
          ['#A000A0', _('purple')],
          ['#A08080', _('dark pink')],
          ['#00A000', _('curly green')],
          ['#FFFF00', _('bright yellow')],
          ['#000000', ''],
          ['#000000', '']]

SOUNDS = [['a-as-in-pat.ogg', 'ah'],
          ['u-as-in-up.ogg', 'uh'],
          ['i-as-in-it.ogg', 'ih'],
          ['e-as-in-pet.ogg', 'eh'],
          ['o-as-in-pot.ogg', 'ah'],
          ['y-as-in-tummy.ogg', 'e'],
          ['p-as-in-pat.ogg', 'p'],
          ['n-as-in-tennis.ogg', 'n'],
          ['t-as-in-tap.ogg', 't'],
          ['d-as-in-dog.ogg', 'd'],
          ['s-as-in-is.ogg', 's'],
          ['m-as-in-mom.ogg', 'm'],
          ['s-as-in-stop.ogg', 's'],
          ['a-as-in-read-a-book.ogg', 'a']]


WORDS = ['a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a',
         'a u a a a a a u a a u a a u a u a a a u u a u a a a a a u a a a a a',
         'a I u a I a I a I I I I a a I u I a a u a I I u a I a u a I a a I a',
         'a i u a i a i E a i i E i i a a i u i a a u a i i u a a i E a E a a',
         'a i u a i o a i e a i o a i e o o i i a e i u e a o e i i o a o a o',
         'a i u a i o a i e a i o u i e o e i i a a i u i o a a o u y a i i u \
y o y a a y i o a a o i u y u y a i u o a e a o u u a a i i a e o i o e a o i \
a i o o a o a o',
         'pa i up a i o pa i e a i o u i e o e  i a a i up i op a a o u y a i \
i u y o y a a y ip pop a a po  u y puppy a i up o a e a op up u a a i i a e \
po i o pe a o i a i o op a op a op',
         'pa i up a i no pa i en an i on u i en o en i in an a i up i op an \
an on u y a i i unny o y an a y ip pop a an po i nu y puppy an i up on an en \
a op up u an an i i a e po i o pe an o i a i o op an op an op',
         'pat i up a i not pa i ten an it on tu i tent o en ti in an a it up \
ti top an tan on u ty at it i unny o y an a y ip pop at tan pot i nutty puppy \
an i up on an tent a op up u an an it i a e pot i to pet an to i a i to op an \
op an op',
         'pat i up a i not pa i ten and it on tu i tent o end ti in and a it \
up ti top and tand on du ty at it i unny o y and daddy ip pop at tand pot i \
nutty puppy ad i up on an tent dad op up ud and and it i ad e pot i to pet \
and to i dad i to op and op and op',
         "pat is up a is not pa is ten and it on tu i tent o ends ti in and a \
it up ti top and tands on du ty at it is unny o y and daddy ip pop op up ud \
and and it is ad e pot is to pet and to is dad's i to op and op and op",
         "pat is up am is not pam is ten and it on tump in tent mom ends tim \
in and am it up tim top and tands on du ty mat it is unny mommy and daddy ip \
pop at tand pot is nutty puppy and is up on man's tent dad mop up mud and and \
it is ad ttempt pot is tom's pet and tom is dad's i tom mop and mop and mop",
         "pat-is-up sam-is-not pam-is-ten-and-sits-on-stump-in-tent mom-sends-\
tim-in-and-sam-sits-up tim-stops-and-stands-on-dusty-mat it-is-sunny mommy-and\
-daddy-sip-pop-at-stand spot-is-nutty-puppy-and-is-up-on-man's-tent dad-mops-\
up-mund-and-sand it-is-sad ttempt spot-is-tom's-pet-and-tom-is-dad's-ssist tom\
-mops-and-mops-and-mops",
         "pat-is-up sam-is-not pam-is-ten-and-sits-on-A-stump-in-A-tent mom-\
sends-tim-in-and-sam-sits-up tim-stops-and-stands-on-A-dusty-mat it-is-sunny \
mommy-and-daddy-sip-pop-at-A-stand spot-is-A-nutty-puppy-and-is-up-on-A-man's-\
tent dad-mops-up-mud-and-sand it-is-A-sad-Attempt spot-is-tom's-pet-and-tom-is\
-dad's-AssistAnt tom-mops-and-mops-and-mops",
         "pat-is-up,-sam-is-not. pam-is-ten-and-sits-on-a-stump-in-a-tent. mom-\
sends-tim-in-and-sam-sits-on-a-dusty-mat. it-is-sunny. mommy-and-daddy-sip-pop\
-at-a-stand. spot-is-a-nutty-puppy-and-is-up-on-a-man's-tent. dad-mops-up-mud-\
and-sand. it-is-a-sad-attempt. spot-is-tom's-pet-and-tom-is-dad's-assistant. \
tom-mops-and-mops-and-mops.",
         "mom-insists-sam-must-study-and-pass-a-test. sam-did-not-pass-a-past-\
test. a-pup-steps-past-and-tempts-sam. sam-is-a-pest-and-sits-in-a-muddy-spot.\
mom-is-mad-at-sam's-messy-pants-and-sends-pam-and-a-pen. pam's-study-tip-\
assists-sam. pam-is-an-asset!"]

STROKES = [1, 4, 13]

# TRANS: e.g., This yellow sign is said u as in up.
MSGS = [[_('This %s sign is said\n'), _('%s like %s.')],
        [_('This %s sign is said\ntogether with other sounds\nas in:\n'),
         _('%s')],
        [_('This %s sign is\nlightly said\n'), _('%s like %s.')],
        [_('When it looks like this\n\n\n\n\n\nwe read it the same way.'), ''],
        [_('This %s sign is said\n\nReading from left to right, read the\n\
sounds one at a time. You can\nuse your finger to follow along.'),
         _('%s like %s.')]]

MSG_INDEX = [4, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 2, -1, -1]
SHOW_MSG2 = [False, False, False, False, False, False, True, True, True,
              True, True, True, True, False, False, False]

KERN = {'i': 0.6, 'I': 0.6, 'l': 0.6, 't': 0.8, 'r': 0.8, 'm': 1.6, 'w': 1.3,
        "'": 0.4}
ALPHABET = "abcdefghijklmnopqrstuvwxyz.,'!"
ALIGN = 11

# TODO: finish sound stuff


class Page():

    def __init__(self, canvas, parent=None):
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
        self.new_page()

    def new_page(self, saved_state=None, deck_index=0):
        ''' Load a new page. '''
        if self.page == len(CARDS):
            self.page = 0
            if self._sugar:
                self._activity.status.set_label('')
        if self.page == len(self._cards):
            if MSG_INDEX[self.page] >= 0:
                self._cards.append(Sprite(self._sprites, self._left,
                                          GRID_CELL_SIZE,
                                          svg_str_to_pixbuf(generate_card(
                                string=CARDS[self.page][0].lower(),
                                colors=[COLORS[self.page][0], '#000000'],
                                scale=self._scale,
                                center=True))))
                self._double_cards.append(Sprite(self._sprites, self._left,
                    self._height + GRID_CELL_SIZE * 2,
                    svg_str_to_pixbuf(generate_card(
                                string=CARDS[self.page][0].lower() + \
                                    CARDS[self.page][0].lower(),
                                colors=[COLORS[self.page][0], '#000000'],
                                scale=self._scale,
                                font_size=32,
                                center=True))))
                if self.page in STROKES:
                    stroke = True
                else:
                    stroke = False
                self._colored_letters.append(Sprite(self._sprites, 0, 0,
                    svg_str_to_pixbuf(generate_card(
                                string=CARDS[self.page][0].lower(),
                                colors=[COLORS[self.page][0], '#000000'],
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

    def _load_card(self):
        self._cards[self.page].set_layer(2)

        if MSG_INDEX[self.page] == 1:
            self._background.set_label(MSGS[1][0] % (COLORS[self.page][1]))
        else:
            self._background.set_label(MSGS[MSG_INDEX[self.page]][0] % \
                                     (COLORS[self.page][1]))
        self._background.set_layer(1)
        self._page_2.set_layer(1)

        rect = gtk.gdk.Rectangle(0, 0, self._width, int(self._height / 10.0))
        self._like_card.images[0].draw_rectangle(self._my_gc, True, *rect)
        self.invalt(0, 0, self._width, int(self._height / 10.0))
        self._x = 0
        self._y = 0
        if MSG_INDEX[self.page] == 1:
            self._render_phrase(MSGS[1][1] % (CARDS[self.page][1]),
                                self._like_card, self._like_gc)
            self._like_card.move((int((self._width - self._final_x) / 2.0),
                                 int(4 * self._height / 5.0)))
        else:
            self._render_phrase(MSGS[MSG_INDEX[self.page]][1] % \
                                    (CARDS[self.page][0],
                                     CARDS[self.page][1]),
                                self._like_card, self._like_gc)
            self._like_card.move((int((self._width - self._final_x) / 2.0),
                                 int(3 * self._height / 5.0)))
        self._like_card.set_layer(1)

        if SHOW_MSG2[self.page]:
            self._page_2.set_label(MSGS[3][0])
            self._double_cards[self.page].set_layer(2)
        else:
            self._page_2.set_label('')

        # Hide all the letter sprites
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
            self._activity.status.set_label(_(''))

    def read(self):
        for c in self._cards:
            c.set_layer(0)
        for c in self._double_cards:
            c.set_layer(0)
        self._background.set_label('')
        self._background.set_layer(0)
        self._like_card.set_layer(0)
        self._page_2.set_layer(0)

        if self._sugar:
            self._activity.status.set_label(
                _('Read the sounds one at a time.'))
        rect = gtk.gdk.Rectangle(0, 0, self._width, self._height * 2)
        self._my_canvas.images[0].draw_rectangle(self._my_gc, True, *rect)
        self.invalt(0, 0, self._width, self._height)
        self._my_canvas.set_layer(1)
        p = 0
        my_list = WORDS[self.page].split(' ')

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

    def _render_phrase(self, phrase, canvas, gc):
        # The words in the list are separated by dashes
        words = phrase.split('-')
        for word in words:
            # Will word run off the right edge?
            if self._x + len(word) * self._offset > self._width - 20:
                self._x, self._y = self._xy(self._y)

            # Process each character in the word
            for c in range(len(word)):
                if MSG_INDEX[self.page] >= 0 and word[c] == CARDS[self.page][0]:
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
        self.start_drag = [x, y]

        spr = self._sprites.find_sprite((x, y))
        self._press = spr
        self._release = None

        return True

    def _button_release_cb(self, win, event):
        win.grab_focus()

        x, y = map(int, event.get_coords())
        spr = self._sprites.find_sprite((x, y))
        if spr == self._cards[self.page]:
            if MSG_INDEX[self.page] >= 0:
                if os.path.exists(os.path.join(os.path.abspath('.'), 'sounds',
                                               SOUNDS[self.page][0])):
                    play_audio_from_file(self, os.path.join(
                            os.path.abspath('.'), 'sounds',
                            SOUNDS[self.page][0]))
                else:
                    os.system('espeak "%s" --stdout | aplay' % \
                                  (SOUNDS[self.page][1]))

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


def svg_str_to_pixbuf(svg_string):
    ''' Load pixbuf from SVG string '''
    pl = gtk.gdk.PixbufLoader('svg')
    pl.write(svg_string)
    pl.close()
    pixbuf = pl.get_pixbuf()
    return pixbuf
