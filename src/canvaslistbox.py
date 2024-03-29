# -*- coding: cp1252 -*-
# (c) Marcelo Barros de Almeida
# marcelobarrosalmeida@gmail.com
from appuifw import *
import e32
import graphics
import key_codes
import os

class CanvasListBox(Canvas):
    """
    
    +----------------------------------+
    |     ^                       c    |
    |     | a                   <----->|
    |  b  v                       d    |
    |<--->+---------------------+---+  |
    |     |\--(XA,YA)           | s |  |
    |     |                     | c |  |
    |     |   List elements     | r |  |
    |     |                     | o |  |    
    |     |                     | l |  |
    |     |           (XB,YB)--\| l |  |
    |     +---------------------+---+  |
    +----------------------------------+
                             
                             
    a = TEXT_LEFT_MARGIN
    b = TEXT_LEFT_MARGIN
    c = TEXT_RIGHT_MARGIN
    d = SCROLL_BAR_W

    ----------------- ^
    Text              | e
    ----------------- v
    ----------------- |<-- f
    
     e = TEXT_H
     f = TEXT_LINE_SEP
    
    """
    BLACK = (0,0,0)
    WHITE = (255,255,255)
    DARK_GREEN = (0,102,0)
    BLUE1 = (51,204,255)
    YELLOW = (255,255,102)
    MED_LIGHT_BLUE = (124,104,238)
    
    XA = 0
    YA = 0
    XB = 0
    YB = 0

    XA_SCR = 0
    XB_SCR = 0
    YA_SCR = 0
    YB_SCR = 0
    
    SCROLL_BAR_W = 5
    SCROLL_BAR_COLOR = WHITE

    SELECTION_COLOR = MED_LIGHT_BLUE
    BACKGROUND = BLACK

    TEXT_LEFT_MARGIN = 2
    TEXT_RIGHT_MARGIN = SCROLL_BAR_W
    TEXT_H = 12
    TEXT_LINE_SEP = 3
    TEXT_COLOR = WHITE
    TEXT_FONT = 'dense'

    AVATAR_H = 50 
    
    def __init__(self,elements,avatars=None,cbk=lambda:None):
        Canvas.__init__(self,
                        redraw_callback = self.redraw_list,
                        event_callback = self.event_list)
        self._screen = graphics.Image.new(self.size)
        self.XA = self.TEXT_LEFT_MARGIN + self.AVATAR_H
        self.YA = self.TEXT_LEFT_MARGIN
        self.XB, self.YB = self.size
        self.XB -= self.TEXT_RIGHT_MARGIN
        self.XA_SCR = self.XB
        self.XB_SCR = self.size[0]
        self.YA_SCR = 0
        self.YB_SCR = self.size[1]
        
        self.cbk = cbk
        self.set_list(elements,avatars)
        self.bind(key_codes.EKeyUpArrow, self.up_key)
        self.bind(key_codes.EKeyDownArrow, self.down_key)
        self.bind(key_codes.EKeySelect, self.cbk)
        
    def redraw_list(self,rect=None):
        self.clear_list()
        self.draw_scroll_bar()
        self.draw_selection_box()
        self.redraw_elements()
        self.blit(self._screen)

    def draw_scroll_bar(self):
        self._screen.rectangle((self.XA_SCR, self.YA_SCR, self.XB_SCR, self.YB_SCR),
                               outline = self.SCROLL_BAR_COLOR)
        list_size = len(self._proc_elements)
        if list_size:
            sz = (self.YB_SCR - self.YA_SCR)/list_size + 1 # rounding up always
            pos = self._current_sel*sz
            self._screen.rectangle((self.XA_SCR, pos, self.XB_SCR, pos + sz),
                                   outline = self.SCROLL_BAR_COLOR, fill = self.SCROLL_BAR_COLOR)            

    def draw_selection_box(self):
        if len(self._proc_elements):
            xa = self.XA
            xb = self.XB
            ya = self.YA
            for m in range(self._current_sel_in_view):
                n = self._selection_view[0] + m
                ya += self._proc_elements[n]['height']
            yb = ya + self._proc_elements[self._selection_view[0] +
                                          self._current_sel_in_view]['height']
            ya -= self.TEXT_LINE_SEP/2
            yb -= self.TEXT_LINE_SEP/2
            self._screen.rectangle((xa,ya,xb,yb),
                                   outline = self.SELECTION_COLOR,
                                   fill = self.SELECTION_COLOR)

    def redraw_elements(self):
        x = self.XA
        y = self.YA + self.TEXT_H
        n = self._selection_view[0]
        while y < self.YB and n < len(self._proc_elements):
            ele = self._proc_elements[n]
            # text
            yt = 0
            for m in range(ele['num_lines']):
                self._screen.text((x,y+yt),ele['text'][m], fill = self.TEXT_COLOR, font = self.TEXT_FONT)
                yt += self.TEXT_H + self.TEXT_LINE_SEP
            if yt < self.AVATAR_H:
                yt = self.AVATAR_H
            ya = y + (yt - 48)/2 - self.TEXT_H
            y += yt
            # avatars
            #self._screen.text((x,y+15),u"%d,%d"%(0,y-self.TEXT_H),
            #                fill = self.YELLOW,
            #                font = 'normal')
            #self._screen.blit(ele['img'],(0,y-self.TEXT_H),((0,0),ele['img'].size))
            self._screen.blit(ele['img'],(0,0),((0,ya),ele['img'].size))            
            n += 1

    def calculate_sel_view(self):
        n = self._selection_view[0]
        y = self.YA
        while y < self.YB and n < len(self._proc_elements):
            y += self._proc_elements[n]['height']
            n += 1
        if y >= self.YB:
            # ensure all elements in view are visible
            n -= 1
        # base index is 0
        self._selection_view[1] = n - 1
            
    def up_key(self):
        if self._current_sel <= 0:
            return       
        n = self._current_sel - 1
        if n < self._selection_view[0]:
            self._selection_view[0] -= 1
            self.calculate_sel_view()
        else:
            self._current_sel_in_view -= 1
            
        self._current_sel = self._current_sel_in_view + self._selection_view[0]
        self.redraw_list()               

    def down_key(self):
        if self._current_sel >= (len(self._proc_elements) - 1):
            return
        n = self._current_sel + 1
        if n > self._selection_view[1]:
            # ensure that selected item in inside the view, increasing the begining until it fits
            while n > self._selection_view[1]:
                self._selection_view[0] += 1
                self.calculate_sel_view()
            self._current_sel_in_view = n - self._selection_view[0]
        else:
            self._current_sel_in_view += 1

        self._current_sel = n
        self.redraw_list()            

    def build_entries(self,elements):
        self._proc_elements = []
        n = 0
        for text in elements:
            # text: array with all lines for the current text, already splitted
            # num_line: len of array
            # height: how much height is necessary for displaying this text
            reg = {}
            reg['text'] = self.split_text(text)
            reg['num_lines'] = len(reg['text'])
            reg['height'] = reg['num_lines']*(self.TEXT_H + self.TEXT_LINE_SEP)
            if reg['height'] < self.AVATAR_H:
                reg['height'] = self.AVATAR_H
            img = graphics.Image.new((48,48))
            img.clear(self.BACKGROUND)
            #improve it ! make a cache, do not load the same image again
            if self.avatars:
                if os.path.exists(self.avatars[n]):
                    #print "loading", self.avatars[n]
                    img.load(self.avatars[n])
            reg['img'] = img
            self._proc_elements.append(reg)
            n += 1
            
    # modified version of TextRenderer.chop 
    # http://discussion.forum.nokia.com/forum/showthread.php?t=124666
    def split_text(self, text):
        lines = []
        text_left = text
        width = self.XB - self.XA 
        while len(text_left) > 0: 
            bounding, to_right, fits = self.measure_text(text_left,
                                                         font=self.TEXT_FONT,
                                                         maxwidth=width,
                                                         maxadvance=width)
            
            if fits <= 0:
                lines.append(text_left)
                break
                    

            slice = text_left[0:fits]
            adjust = 0 # (preserve or not whitespaces at the end of the row)
        
            if len(slice) < len(text_left):
                # find the separator character closest to the right
                rindex = -1
                for sep in u" .;:\\/-":
                    idx = slice.rfind(sep)
                    if idx > rindex:
                        rindex = idx
                if rindex > 0:
                    if slice[rindex] == u' ':
                        adjust = 1
                    slice = slice[0:rindex]
                                
            lines.append(slice)
            text_left = text_left[len(slice)+adjust:]
        
        return lines
    
    def event_list(self,ev):
        pass

    def clear_list(self):
        self._screen.clear(self.BACKGROUND)
        self.blit(self._screen)

    def current(self):
        return self._current_sel

    def set_list(self,elements,avatars=None):
        self.avatars = avatars
        self._current_sel = 0
        self._current_sel_in_view = 0
        self._selection_view = [0,0]
        self.build_entries(elements)        
        self.calculate_sel_view()
        self.redraw_list()
