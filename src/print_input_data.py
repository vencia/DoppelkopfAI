#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import sys
import glob
import numpy as np
import argparse

DATA_PATH = '../data/'

def load_dataset():
    def load_data(path):
        if not os.path.exists(path):
            print("Path not found: {}".format(path))
            sys.exit(0)
        tmp = []
        #files = glob.glob(path + "/*." + ext)

        files = sorted(glob.glob(path + str(game_id)  + '_*'),key=lambda x: int(x.rsplit('/',1)[1].rsplit('.')[0].replace("_","")))
        print files[:20]
        #if dataset_size != 0 and len(files) > dataset_size:
        #    files = files[:dataset_size]
        for f in files:
            #tmp.append(pickle.load(open(f, 'rb')))
            tmp.append(np.load(open(f, 'rb')))
        return tmp
    
    if prediction:
        x_data = load_data(DATA_PATH + 'input-data-' + game_type + '/')
    else:
        x_data = load_data(DATA_PATH + 'input-data/')

    for c,data in enumerate(x_data):  
        print c
        print data
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("game_id", type=int)
    #parser.add_argument("-num_games", type=int)
    parser.add_argument("--prediction", dest='prediction', action='store_true')
    parser.add_argument("--live", dest='live', action='store_true')



    args = parser.parse_args()
    game_id = args.game_id
    prediction = args.prediction
    if args.live:
        game_type = 'live'
    else:
        game_type = 'full'
    if prediction:
        DATA_PATH += 'prediction/'
    
    load_dataset()