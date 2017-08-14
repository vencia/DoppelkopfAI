# -*- coding: utf-8 -*-

import glob

DATA_PATH = '../data/'

files = glob.glob(DATA_PATH + 'game-protocols-test/' + "/*." + 'csv')
for f in files:
    with open(f, 'r') as original: data = original.read()
    with open(f, 'w') as modified: modified.write("full-protocol\n" + data)