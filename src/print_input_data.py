#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import sys
import glob
import numpy as np
import argparse

def load_dataset():
    def load_data(path):
        if not os.path.exists(path):
            print("Path not found: {}".format(path))
            sys.exit(0)
        tmp = []

        files = sorted(glob.glob(path + ref_num),key=lambda x: int(x.rsplit('/',1)[1].rsplit('.')[0].replace("_","")))

        for f in files:
            tmp.append(np.load(open(f, 'rb')))
        return tmp
    
    x_data = load_data(data_path + 'input-data/')
    print x_data[0]
    #for c,data in enumerate(x_data):  
    #    print c
    #    print data
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("game_num", type=int)
    parser.add_argument("bot_num", type=int)
    parser.add_argument("trick_num", type=int)
    parser.add_argument("-data_path", type=str, default='/media/vencia/Daten/DoppelkopfAI/data/')
    #parser.add_argument("-num_games", type=int)
    #parser.add_argument("--prediction", dest='prediction', action='store_true')

    args = parser.parse_args()
    game_num = args.game_num
    bot_num = args.bot_num
    trick_num = args.trick_num
    data_path = args.data_path   
    ref_num = str(game_num) + '_' + str(bot_num) + '_' + "%02d" % trick_num

    
    load_dataset()