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

#
# These tables and dictionaries represent a level (Level 1 in English)
# CARDS, COLORS, SOUNDS, and WORDS
#
CARDS = [['A', _('pAt')],  # Use CAPS for highlight.
         ['U', _('Up')],
         ['I', _('It')],
         ['E', _('pEt')],
         ['O', _('pOt')],
         ['Y', _('tummY')],
         ['P', _('Pat')],
         ['N', _('Not,-teNNis')],
         ['T', _('Tap')],
         ['D', _('DaD')],
         ['S', _('iS,-aS,-waS,-sayS')],
         ['M', _('MoM')],
         ['S', _("Sam,-Stop,-it'S")],
         ['A', _('read-A-book')],
         ['', ''],
         ['', '']]

# [RGB color, color name, outline stroke]
COLORS = [['#BA6C71', _('light pink'), False],
          ['#FFFCC0', _('yellow'), True],
          ['#EF2891', _('pink'), False],
          ['#70A9CE', _('blue'), False],
          ['#FFFFFF', _('white'), True],
          ['#DE1C23', _('red'), False],
          ['#A4221E', _('brown'), False],
          ['#7A6BBD', _('purple'), False],
          ['#C72098', _('dark pink'), False],
          ['#2EA539', _('green'), False],
          ['#B139A2', _('purple'), False],
          ['#EE3C1E', _('dark pink'), False],
          ['#7EC93C', _('curly green'), False],
          ['#FFF200', _('bright yellow'), True]]

# [sound file, sound string for espeak]
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

WORDS = ['A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A',
         'a U a a a a a U a a U a a U a U a a a U U a U a a a a a U a a a a a',
         'a I u a I a I a I I I I a a I u I a a u a I I u a I a u a I a a I a',
         'a i u a i a i E a i i E i i a a i u i a a u a i i u a a i E a E a a',
         'a i u a i O a i e a i O a i e O O i i a e i u e a O e i i O a O a O',
         'a i u a i o a i e a i o u i e o e i i a a i u i o a a o u Y a i i u \
Y o Y a a Y i o a a o i u Y u Y a i u o a e a o u u a a i i a e o i o e a o i \
a i o o a o a o',
         'Pa i uP a i o Pa i e a i o u i e o e  i a a i uP i oP a a o u y a i \
i u y o y a a y iP PoP a a Po  u y PuPPy a i uP o a e a oP uP u a a i i a e \
Po i o Pe a o i a i o oP a oP a oP',
         'pa i up a i No pa i eN aN i oN u i eN o eN i iN aN a i up i op aN \
aN oN u y a i i uNNy o y aN a y ip pop a aN po i Nu y puppy aN i up on aN eN \
a op up u aN aN i i a e po i o pe aN o i a i o op aN op aN op',
         'paT i up a i noT pa i Ten an iT on Tu i TenT o en Ti in an a iT up \
Ti Top an Tan on u Ty aT iT i unny o y an a y ip pop aT Tan poT i nuTTy puppy \
an i up on an TenT a op up u an an iT i a e poT i To peT an To i a i To op an \
op an op',
         'pat i up a i not pa i ten anD it on tu i tent o enD ti in anD a it \
up ti top anD tanD on Du ty at it i unny o y anD DaDDy ip pop at tand pot i \
nutty puppy ad i up on an tent DaD op up uD anD anD it i aD e pot i to pet \
anD to i DaD i to op anD op anD op',
         "pat iS up a iS not pa iS ten and it on tu i tent o endS ti in and a \
it up ti top and tandS on du ty at it iS unny o y and daddy ip pop op up ud \
and and it iS ad e pot iS to pet and to iS dad'S i to op and op and op",
         "pat is up aM is not paM is ten and it on tuMp in tent MoM ends tiM \
in and aM it up tiM top and tands on du ty Mat it is unny MoMMy and daddy ip \
pop at tand pot is nutty puppy and is up on Man's tent dad Mop up Mud and and \
it is ad ttempt pot is toM's pet and toM is dad's i toM Mop and Mop and Mop",
         "pat-is-up Sam-is-not pam-is-ten-and-SitS-on-Stump-in-tent mom-Sends-\
tim-in-and-Sam-SitS-up tim-StopS-and-StandS-on-duSty-mat it-is-Sunny mommy-and\
-daddy-Sip-pop-at-Stand Spot-is-nutty-puppy-and-is-up-on-man's-tent dad-mopS-\
up-mund-and-Sand it-is-Sad ttempt Spot-is-tom's-pet-and-tom-is-dad's-SSiSt tom\
-mopS-and-mopS-and-mopS",
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

KERN = {'i': 0.6, 'I': 0.6, 'l': 0.6, 't': 0.8, 'T': 0.8, 'r': 0.8, 'm': 1.6,
        'w': 1.3, "'": 0.4, 'M': 1.6}
ALPHABET = "abcdefghijklmnopqrstuvwxyz.,'!"


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
        self.new_page()

    def page_list(self):
        ''' Index into all the cards in the form of a list of phrases '''
        # Already here? Then jump back to current page.
        if self._looking_at_word_list:
            self.new_page()
            return

        save_page = self.page
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
                _('Select a page.'))
        rect = gtk.gdk.Rectangle(0, 0, self._width, self._height * 2)
        self._my_canvas.images[0].draw_rectangle(self._my_gc, True, *rect)
        self.invalt(0, 0, self._width, self._height)
        self._my_canvas.set_layer(1)
        p = 0

        self._x, self._y = 10, 10

        # Each list is a collection of phrases, separated by spaces
        for i, card in enumerate(CARDS):
            if card[0] == '':
                break
            if card[0] in 'AEIOUY':
                connector = '-' + _('like') + '-'
            else:
                connector = '-' + _('as-in') + '-'
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
                if COLORS[self.page][2]:
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
        self._looking_at_word_list = False

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

        self._looking_at_word_list = False

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
