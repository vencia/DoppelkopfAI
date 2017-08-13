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

INPUT_DATA_PATH = '../data/input-data/'
LABEL_DATA_PATH = '../data/label-data/'
DATA_PATH = '../data/'

def load_dataset():
    def load_data(path, ext):
        if not os.path.exists(path):
            print("Path not found: {}".format(path))
            sys.exit(0)
        tmp = []
        files = sorted(glob.glob(path + game_id + "_*." + ext),key=lambda x: int(x.rsplit('/',1)[1].rsplit('.')[0].replace("_","")))
        for f in files:
            tmp.append(pickle.load(open(f, 'rb')))
        return tmp
        
    x = load_data(INPUT_DATA_PATH, "tr")
    y = load_data(LABEL_DATA_PATH, "lb")

    return np.array(x), np.array(y)
    
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
    parser.add_argument("model_folder", type=str)
    parser.add_argument("-game_id", type=int, default=501)

    args = parser.parse_args()
    game_id = str(args.game_id)
    DATA_PATH += args.model_folder + '/'
    infoFile = open(DATA_PATH + 'pred_info.log', 'w')
    backup = sys.stdout
    sys.stdout = Tee(sys.stdout, infoFile)
    
    print(args)
    
    # load json and create model
    json_file = open(DATA_PATH + 'model.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    model = model_from_json(loaded_model_json)
    # load weights into new model
    model.load_weights(DATA_PATH + "model_weights.h5")
    print("Loaded model from disk")
     
    x, y = load_dataset()
    
    if K.backend() == 'tensorflow':
        K.set_image_dim_ordering('tf') # channels last
        x = np.swapaxes(x,1,3)
        x = np.swapaxes(x,1,2)
    else:
        K.set_image_dim_ordering('th') # channels first
        
    input_shape = x[0].shape
    print input_shape
    
    # evaluate loaded model on test data
    model.compile(loss=keras.losses.categorical_crossentropy,
                  optimizer=keras.optimizers.Adadelta(),
                  metrics=['accuracy'])
    

    score = model.evaluate(x, y, verbose=0)
    print score
    predictions = model.predict(x)
    np.savetxt(DATA_PATH + 'predictions.csv',predictions,delimiter=',')
    for c,pred in enumerate(predictions):
        formatted_predictions = ['%.2f' % p for p in pred]
        player = c / 12
        trick = c % 12
        print 'player ' + str(player) + ' trick ' + str(trick)
        print get_top_cards(pred,3)
        print formatted_predictions
    

