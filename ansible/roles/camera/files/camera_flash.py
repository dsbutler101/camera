#!/usr/bin/python

import time
from blinkt import set_clear_on_exit, set_pixel, show

set_clear_on_exit()

def show_all(state):
    for i in range(8):
        val = state * 255
        set_pixel(i, val, val, val)
    show()


show_all(1)
time.sleep(0.05)
show_all(0)
time.sleep(0.1)
show_all(1)
time.sleep(0.05)
show_all(0)
