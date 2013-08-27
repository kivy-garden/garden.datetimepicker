DatetimePicker
==============

`DatetimePicker` is a roulette based datetime selector like in iOS
and android.

Dependencies
------------

The only immediate dependency is the garden package ``kivy.garden.roulette``.
However, if you have never installed garden packages before, and start with
only a default kivy python distribution, then the following garden packages
are needed. Use ``garden install`` to install them.

a. ``kivy.garden.tickline``

b. ``kivy.garden.roulette``

c. ``kivy.garden.roulettescroll``

Usage
-----

Just instantiate ``DatetimePicker()``

    if __name__ == '__main__':
        from kivy.base import runTouchApp
        runTouchApp(DatetimePicker())
    
This will give you 6 vertical roulettes
that respectively represent year, month, day, hour, minute, and second. 

`DatetimePicker.selected_value` records the selection from the user.

`DatetimePicker.density` controls how many values are shown at a time.

NICER GRAPHICS!
---------------

I didn't focus much on the graphics, or to closely simulate the iOS or android
experience. You are encourage to contribute to improve the default appearance
of the datetimepicker!
