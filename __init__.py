'''
DatetimePicker
=============

:class:`DatetimePicker` is a roulette based datetime selector like in iOS
and android.

Dependencies
------------

The only immediate dependency is the garden package ``kivy.garden.roulette``.
However, if you have never installed garden packages before, and start with
only a default kivy python distribution, then the following is needed.

1. garden packages. Use ``garden install`` to install them.

    a. ``kivy.garden.tickline``
    b. ``kivy.garden.roulette``
    c. ``kivy.garden.roulettescroll``
    
'''

from calendar import monthrange
from datetime import datetime, timedelta
from functools import partial
from kivy.clock import Clock
from kivy.effects.scroll import ScrollEffect
from kivy.factory import Factory
from kivy.garden.roulette import TimeFormatCyclicRoulette, Roulette, \
    CyclicRoulette
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import ObjectProperty, NumericProperty, AliasProperty, \
    BooleanProperty
from kivy.uix.boxlayout import BoxLayout

Builder.load_string('''
<Symbol@Label>:
    size_hint_x: None
    width: '20dp'
    text: ''
    font_size: '30sp'
<Colon@Symbol>:
    text: ':'
<Dash@Symbol>:
    text: '-'
''')

Symbol = Factory.Symbol
Dash = Factory.Dash
Colon = Factory.Colon


Builder.load_string('''
<DatetimePicker>:
    canvas.after:
        Color:
            rgba: 0, 0, 1, .3
        Rectangle:
            pos: self.x, self.center_y - self.shield_width
            size: self.width, 2 * self.shield_width
        Line:
            points: self.x, self.center_y - self.shield_width + self._shade_width, \
            self.x + self.width, self.center_y - self.shield_width + self._shade_width
            width: self._shade_width
            cap: 'none'
    size_hint: None, 1
    padding: [dp(10), 0, dp(10), 0]
''')

class DatetimePicker(BoxLayout):
    '''a simple roulette datetime selector for *timezone-naive* datetime.'''
    
    _shade_width = NumericProperty('1.5dp')
    shield_width = NumericProperty('25dp')
    '''setting for graphics. May be changed or obsoleted in the future.'''

    year = ObjectProperty(None)
    month = ObjectProperty(None)
    day = ObjectProperty(None)
    hour = ObjectProperty(None)
    minute = ObjectProperty(None)
    second = ObjectProperty(None)
    
    selected_datetime = ObjectProperty(None)
    '''tracks the datetime selection.'''
    
    in_motion = BooleanProperty(False)
    '''indicates whether any of the member roulettes are in motion.'''
    
    datetime_fields = ('year', 'month', 'day', 'hour', 'minute', 'second')
    month_size = NumericProperty(None, allownone=True)

    def __init__(self, **kw):
        super(DatetimePicker, self).__init__(**kw)
        self.init_roulettes()
    def init_roulettes(self):
        self._calibrate_month_size_trigger = t = \
                    Clock.create_trigger(self.calibrate_month_size)
        self._adjust_day_cycle_trigger = \
                    Clock.create_trigger(self._adjust_day_cycle, -1)
        now = datetime.now()
        self.second = second = TimeFormatCyclicRoulette(cycle=60)
        second.select_and_center(now.second)
        self.minute = minute = TimeFormatCyclicRoulette(cycle=60)
        minute.select_and_center(now.minute)
        self.hour = hour = TimeFormatCyclicRoulette(cycle=24)
        hour.select_and_center(now.hour)
        self.year = year = Roulette()
        year.select_and_center(now.year)
        self.month = month = CyclicRoulette(cycle=12, zero_indexed=False)
        month.select_and_center(now.month)
        
        month_size = monthrange(now.year, now.month)[1]
        self.day = day = CyclicRoulette(cycle=month_size, zero_indexed=False,
                                        on_centered=self._adjust_day_cycle_trigger)
        day.select_and_center(now.day)
        
        self.month.bind(selected_value=t)
        self.year.bind(selected_value=t)
        
        self.set_selected_datetime()
        self._bind_updates()
        
        children = [
                    year, Dash(), month, Dash(), day, Symbol(),
                    hour, Colon(), minute, Colon(), second,
                    ]
        add = self.add_widget
        width = dp(20)
        for c in children:
            add(c)
            width += c.width
        self.width = width
    def update_width(self, *args):
        width = sum(c.width for c in self.children)
        self.width = width
    def get_datetime(self, *args):
        try:
            d = {field: getattr(self, field).selected_value
                 for field in self.datetime_fields}
            return datetime(**d)
        except:
            return None
    def _update_in_motion(self, *args):
        for field in self.datetime_fields:
            if getattr(self, field).in_motion:
                self.in_motion = True
                return
        self.in_motion = False
        return
    def set_datetime(self, val, *args, **kw):
        '''animatedly set the roulette's datetime to ``val``. 
        The keyword argument ``largest_delta`` can be set to True to specify
        that only the largest granularity of time that differs from 
        ``val`` to the time shown on the roulettes is to be changed.
        
        For example, if ``val = datetime(2013, 1, 2, 5, 55, 23)`` and
        current time shown is ``datetime(2013, 1, 2, 6, 02, 33)``, and
        ``largest_delta=True``, then only the hour roulette will be updated
        to center on ``5``, and no other changes are introduced.
        
        This option is useful for reducing graphical load when linking
        this roulette to changing values of time.'''
        largest_delta = kw.get('largest_delta')
        for field in self.datetime_fields:
            changed = getattr(self, field).select_and_center(getattr(val, field))
            if changed and largest_delta:
                return
    def set_selected_datetime(self, *args):
        new_dt = self.get_datetime()
        if new_dt:
            self.selected_datetime = new_dt
    def _bind_updates(self, *args):
        for field in self.datetime_fields:
            getattr(self, field).bind(selected_value=self.set_selected_datetime,
                                      in_motion=self._update_in_motion)
            
    def calibrate_month_size(self, *args):
        selected_year = self.year.selected_value
        selected_month = self.month.selected_value
        self.month_size = month_size = monthrange(selected_year, 
                                                  selected_month)[1]
        day = self.day
        if day.cycle == month_size:
            return
        if day.selected_value > month_size:
            day.select_and_center(month_size)
        else:
            self._adjust_day_cycle()
    def _adjust_day_cycle(self, *args, **kw):
        new_cycle = kw.get('new_cycle', self.month_size)
        if new_cycle is None or self.day.cycle == new_cycle:
            return
        current_day = self.day.selected_value
        self.day.cycle = new_cycle
        # unless month_size gets set again, guards against erroneous adjustment
        # and infinite loop
        self.month_size = None
        
        self.day.select_and_center(current_day, animate=False)
    
if __name__ == '__main__':
    from kivy.base import runTouchApp
    runTouchApp(DatetimePicker())