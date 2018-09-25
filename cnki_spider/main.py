#!/usr/bin/env python
# -*- coding: utf-8 -*-

import threading

def shadow(num):
    print('{}产生了第{}个分身...'.format(threading.currentThread().getName(), num))

for i in range(1, 6):
    t = threading.Thread(target=shadow, args=(i,))
    t.start()
    t.join(timeout=10)

print(threading.currentThread().getName())
