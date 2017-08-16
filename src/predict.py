# -*- coding: utf-8 -*-

import sys
import os
import glob
import argparse
import pickle
import numpy as np
import keras
from keras.models import model_from_json
from keras import backend as K

DATA_PATH = '../data/'

def load_dataset():
    def load_data(path):
        if not os.path.exists(path):
            print("Path not found: {}".format(path))
            sys.exit(0)
        tmp_x = []
        tmp_b = []
        tmp_t = []
        files = sorted(glob.glob(path + game_id + '*'),key=lambda x: int(x.rsplit('/',1)[1].rsplit('.')[0].replace("_","")))
        for f in files:
            #tmp.append(pickle.load(open(f, 'rb')))
            trick_num = int(f.split('_')[2])
            bot_num = int(f.split('_')[1])
            tmp_x.append(np.load(open(f, 'rb')))
            tmp_b.append(bot_num)
            tmp_t.append(trick_num)
        return tmp_x, tmp_b, tmp_t

    x, b, t = load_data(DATA_PATH + 'prediction/input-data-' + game_type + '/')


    #y = load_data(DATA_PATH + 'prediction/label-data/')

    return np.array(x), b, t
    
def get_top_cards(pred,top_num):
    sortedValues = ["9","10","J","Q","K","A"]
    sortedSuits = ["D","H","S","C"]
    top_preds = list(reversed(sorted(range(len(pred)), key=lambda i: pred[i])))[:top_num]
    cards = []
    for idx in top_preds:
        cards.append(sortedSuits[idx / 6] + sortedValues[idx % 6])    
    return cards

class Tee(object): # logging to console and file
    def __init__(self, *files):
        self.files = files
    def write(self, obj):
        for f in self.files:
            f.write(obj)
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('model_folder', type=str)
    parser.add_argument('game_id', type=int)
    parser.add_argument('--live', dest='live', action='store_true')

    args = parser.parse_args()
    game_id = str(args.game_id)
    if args.live:
        game_type = 'live'
    else:
        game_type = 'full'
    
    MODEL_PATH = DATA_PATH + args.model_folder + '/'
    infoFile = open(MODEL_PATH + 'pred_info_' + game_id + '_' + game_type + '.log', 'w')
    backup = sys.stdout
    sys.stdout = Tee(sys.stdout, infoFile)
    
    print(args)
    
    # load json and create model
    json_file = open(MODEL_PATH + 'model.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    model = model_from_json(loaded_model_json)
    # load weights into new model
    model.load_weights(MODEL_PATH + "model_weights.h5")
    #print("Loaded model from disk")
     
    x, b, t = load_dataset()
    #print x.shape
    #print dataset
    
    K.set_image_dim_ordering('th')
    if K.backend() == 'theano':
        x = np.swapaxes(x,1,2)
        x = np.swapaxes(x,1,3)
        
    input_shape = x[0].shape
    print input_shape
    
    # evaluate loaded model on test data
    model.compile(loss=keras.losses.categorical_crossentropy,
                  optimizer=keras.optimizers.Adadelta(),
                  metrics=['accuracy'])
    
    #score = model.evaluate(x, y, verbose=0)

    predictions = model.predict(x)
    np.savetxt(MODEL_PATH + 'pred_' + game_id + '_' + game_type + '.csv',predictions)
    for c,pred in enumerate(predictions):
        formatted_predictions = ['%.2f' % p for p in pred]
        player = b[c]
        trick = t[c]
        #if player == 0 and trick == 4:
        #    print x[c]
        print 'player ' + str(player) + ' trick ' + str(trick+1)
        print get_top_cards(pred,3)
        print formatted_predictions
    

