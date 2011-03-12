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
         ['i', _('it')],
         ['e', _('pet')],
         ['o', _('pot')],
         ['y', _('tummy')],
         ['p', _('pat')],
         ['n', _('not, tennis')],
         ['t', _('tap')],
         ['d', _('dad')],
         ['s', _('is, as, was, says')],
         ['m', _('mom')],
         ['s', _("sam, stop, it's")],
         ['A', _('read a book')]]

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
          ['#FFFF00', _('bright yellow')]]


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
         'a i u a i a i a i i i i a a i u i a a u a i i u a i a u a i a a i a',
         'a i u a i a i e a i i e i i a a i u i a a u a i i u a a i e a e a a',
         'a i u a i o a i e a i o a i e o o i i a e i u e a o e i i o a o a o',
         'a i u a i o a i e a i o u i e o e i i a a i u i o a a o u y a i i u y o y a a y i o a a o i u y u y a i u o a e a o u u a a i i a e o',  # i o e a o i a i o o a o a o',
         'pa i up a i o pa i e a i o u i e o e  i a a i up i op a a o u y a i i u y o y a a y ip pop a a po  u y puppy a i up o a e a op up u',  # a a i i a e po i o pe a o i a i o op a op a op',
         'pa i up a i no pa i en an i on u i en o en i in an a i up i op an an on u y a i i unny o y an a y ip pop a an po i nu y puppy an i up on an en a op up',  # u an an i i a e po i o pe an o i a i o op an op an op',
         'pat i up a i not pa i ten an it on tu i tent o en ti in an a it up ti top an tan on u ty at it i unny o y an a y ip pop at tan pot i nutty puppy an i up on an tent a',  # op up u an an it i a e pot i to pet an to i a i to op an op an op',
         'pat i up a i not pa i ten and it on tu i tent o end ti in and a it up ti top and tand on du ty at it i unny o y and daddy ip pop at tand pot i nutty puppy ad i up on an tent dad op up',  # ud and and it i ad e pot i to pet and to i dad i to op and op and op',
         "pat is up a is not pa is ten and it on tu i tent o ends ti in and a it up ti top and tands on du ty at it is unny o y and daddy ip pop op up ud and and it is ad e pot",  # is to pet and to is dad's i to op and op and op",
         "pat is up am is not pam is ten and it on tump in tent mom ends tim in and am it up tim top and tands on du ty mat it is unny mommy and daddy ip pop at tand pot is nutty puppy",  # and is up on man's tent dad mop up mud and and it is ad ttempt pot is tom's pet and tom is dad's i tom mop and mop and mop",
         "pat-is-up sam-is-not pam-is-ten-and-sits-on-stump-in-tent mom-sends-tim-in-and-sam-sits-up tim-stops-and-stands-on-dusty-mat it-is-sunny mommy-and-daddy-sip-pop-at-stand spot-is-nutty-puppy-and-is-up-on-man's-tent dad-mops-up-mund-and-sand it-is-sad ttempt spot-is-tom's-pet-and-tom-is-dad's-ssist tom-mops-and-mops-and-mops",
         "pat-is-up sam-is-not pam-is-ten-and-sits-on-A-stump-in-A-tent mom-sends-tim-in-and-sam-sits-up tim-stops-and-stands-on-A-dusty-mat it-is-sunny mommy-and-daddy-sip-pop-at-A-stand spot-is-A-nutty-puppy-and-is-up-on-A-man's-tent dad-mops-up-mud-and-sand it-is-A-sad-Attempt spot-is-tom's-pet-and-tom-is-dad's-AssistAnt] # tom-mops-and-mops-and-mops"]

STROKES = [1, 4, 13]

# TRANS: e.g., This yellow sign is said u as in up.
MSGS = [_('This %s sign is said\n%s like %s.'),
        _('This %s sign is said\ntogether with other sounds\nas in: %s'),
        _('This %s sign is\nlightly said\n%s like %s.'),
        _('When it looks like this,\nwe read it the same way.')]

MSG_INDEX = [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 2]

KERN = {'i':0.6, 't':0.8, 'm':1.6, "'":0.4}

ALIGN = 11

# TODO: add color to a like pat
#       finish sound stuff


class Page():

    def __init__(self, canvas, parent=None, colors=['#A0FFA0', '#FF8080']):
        self.activity = parent
        self.colors = colors

        # Starting from command line
        if parent is None:
            self.sugar = False
            self.canvas = canvas
        else:
            self.sugar = True
            self.canvas = canvas
            parent.show_all()

        self.canvas.set_flags(gtk.CAN_FOCUS)
        self.canvas.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.canvas.add_events(gtk.gdk.BUTTON_RELEASE_MASK)
        self.canvas.connect("expose-event", self._expose_cb)
        self.canvas.connect("button-press-event", self._button_press_cb)
        self.canvas.connect("button-release-event", self._button_release_cb)
        self.canvas.connect("key_press_event", self._keypress_cb)
        self.width = gtk.gdk.screen_width()
        self.height = gtk.gdk.screen_height() - GRID_CELL_SIZE
        self.scale = self.width / 240.
        self.left = int((self.width - self.scale * 60) / 2.)
        self.sprites = Sprites(self.canvas)
        self.page_index = 0
        self.background = Sprite(self.sprites, 0, 0, svg_str_to_pixbuf(
                generate_card(string='', colors=['#FFFFFF', '#FFFFFF'],
                              scale=self.scale*4)))
        self.background.set_layer(1)
        self.background.set_label_attributes(40)
        self.cards = []
        self.letters = []
        self.colored_letters = []
        self.press = None
        self.release = None
        self.gplay = None

        self.my_canvas = Sprite(self.sprites, 0, 0,
                gtk.gdk.Pixmap(self.canvas.window, self.width,
                               self.height, -1))
        self.my_canvas.set_layer(0)
        self.gc = self.my_canvas.images[0].new_gc()
        self.cm = self.gc.get_colormap()
        self.bgcolor = self.cm.alloc_color('#FFFFFF')
        self.gc.set_foreground(self.bgcolor)

        self.punctuation = Sprite(self.sprites, 0, 0,
                                  svg_str_to_pixbuf(generate_card(
                    string="'", colors=['#000000', '#000000'],
                    background=False)))

        self.new_page()

    def new_page(self, saved_state=None, deck_index=0):
        ''' Load a new page. '''
        if self.page_index == len(CARDS):
            self.page_index = 0
            self.activity.status.set_label('')
        if self.page_index == len(self.cards):
            self.cards.append(Sprite(self.sprites, self.left, GRID_CELL_SIZE,
                                     svg_str_to_pixbuf(generate_card(
                            string=CARDS[self.page_index][0].lower(),
                            colors=[COLORS[self.page_index][0], '#000000'],
                            scale=self.scale,
                            center=True))))
            self.activity.status.set_label('')
            if self.page_index in STROKES:
                stroke = True
            else:
                stroke = False
            self.letters.append(Sprite(self.sprites, 0, 0,
                                     svg_str_to_pixbuf(generate_card(
                                string=CARDS[self.page_index][0].lower(),
                                colors=['#000000', '#000000'],
                                background=False))))
            self.colored_letters.append(Sprite(self.sprites, 0, 0,
                    svg_str_to_pixbuf(generate_card(
                                string=CARDS[self.page_index][0].lower(),
                                colors=[COLORS[self.page_index][0], '#000000'],
                                background=False, stroke=stroke))))

        for c in self.cards:
            c.set_layer(0)
        self._load_card()

    def _load_card(self):
        self.cards[self.page_index].set_layer(2)
        if MSG_INDEX[self.page_index] == 1:
            self.background.set_label(MSGS[1] % (COLORS[self.page_index][1],
                                                 CARDS[self.page_index][1]))
        else:
            self.background.set_label(MSGS[MSG_INDEX[self.page_index]] % \
                                          (COLORS[self.page_index][1],
                                           CARDS[self.page_index][0].lower(),
                                           CARDS[self.page_index][1]))

        self.background.set_layer(1)
        for l in self.letters:
            l.set_layer(0)
        for l in self.colored_letters:
            l.set_layer(0)
        self.punctuation.set_layer(0)
        self.my_canvas.set_layer(0)

    def reload(self):
        self._load_card()

    def read(self):
        for c in self.cards:
            c.set_layer(0)
        self.background.set_label('')
        self.background.set_layer(0)
        self.activity.status.set_label(_('Read the sounds one at a time.'))
        rect = gtk.gdk.Rectangle(0, 0, self.width, self.height)
        self.my_canvas.images[0].draw_rectangle(self.gc, True, *rect)
        self.invalt(0, 0, self.width, self.height)
        self.my_canvas.set_layer(1)
        p = 0
        offset = self.width/30
        my_list = WORDS[self.page_index].split(' ')

        # Some pages are aligned left
        if self.page_index > ALIGN:
            x, y = 10, 10
        else:
            x, y = self._xy(0)

        # Each list is a collection of phrases, separated by spaces
        for phrase in my_list:
            # The words in the list are separated by dashes
            words = phrase.split('-')
            for word in words:
                # Will word run off the right edge?
                if x + len(word) * offset > self.width:
                    x, y = self._xy(y)

                # Process each character in the word
                for c in range(len(word)):
                    if word[c] == CARDS[self.page_index][0]:
                        self._draw_pixbuf(
                            self.colored_letters[self.page_index].images[0],
                            x, y)
                    elif word[c] == "'":
                        self._draw_pixbuf(self.punctuation.images[0], x, y)
                    else:
                        for j in range(self.page_index):
                            if CARDS[j][0] == word[c]:
                                self._draw_pixbuf(self.letters[j].images[0],
                                                  x, y)
                    if word[c] in KERN:
                        x += offset * KERN[word[c]]
                    else:
                        x += offset

                # Put a space after each word
                if x > 10:
                    x += int(offset / 1.6)

            # Put a long space between each phrase
            if self.page_index > ALIGN:
                x += offset
            else:
                x += int(uniform(30, self.width/8))
            if x > self.width * 7 / 8.0:
                x, y = self._xy(y)

    def _draw_pixbuf(self, pixbuf, x, y):
        w = pixbuf.get_width()
        h = pixbuf.get_height()
        self.my_canvas.images[0].draw_pixbuf(self.gc, pixbuf, 0, 0,
                                             int(x), int(y))
        self.invalt(x, y, w, h)

    def _xy(self, y):
        if self.page_index > ALIGN:
            return 10, int(self.height / 10.0) + y
        else:
            return int(uniform(40, self.width / 8.0)), \
                   int(uniform(40, self.height / 10.0)) + y

    def _button_press_cb(self, win, event):
        win.grab_focus()
        x, y = map(int, event.get_coords())
        self.start_drag = [x, y]

        spr = self.sprites.find_sprite((x, y))
        self.press = spr
        self.release = None

        return True

    def _button_release_cb(self, win, event):
        win.grab_focus()

        x, y = map(int, event.get_coords())
        spr = self.sprites.find_sprite((x, y))
        if spr == self.cards[self.page_index]:
            play_audio_from_file(self, 'sounds/a-as-in-pat.ogg')
            ''' os.system('espeak "%s" --stdout | aplay' % \
                          (SOUNDS[self.page_index][1])) '''

    def _game_over(self, msg=_('Game over')):
        if self.sugar:
            self.activity.status.set_label(msg)

    def _keypress_cb(self, area, event):
        return True

    def _expose_cb(self, win, event):
        self.sprites.redraw_sprites()
        return True

    def _destroy_cb(self, win, event):
        gtk.main_quit()

    def invalt(self, x, y, w, h):
        """ Mark a region for refresh """
        self.canvas.window.invalidate_rect(
            gtk.gdk.Rectangle(int(x), int(y), int(w), int(h)), False)

#
# Load pixbuf from SVG string
#
def svg_str_to_pixbuf(svg_string):
    pl = gtk.gdk.PixbufLoader('svg')
    pl.write(svg_string)
    pl.close()
    pixbuf = pl.get_pixbuf()
    return pixbuf
