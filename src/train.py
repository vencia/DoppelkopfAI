#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import sys
import pickle
import glob
import numpy as np
import argparse
import keras
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten
from keras.layers import Conv2D, MaxPooling2D
from keras import backend as K

INPUT_DATA_PATH = '../data/input-data/'
LABEL_DATA_PATH = '../data/label-data/'

NUM_CLASSES = 24

def load_dataset(input_path, label_path):
    def load_data(path, ext):
        if not os.path.exists(path):
            print("Path not found: {}".format(path))
            sys.exit(0)
        tmp = []
        for f in glob.glob(path + "/*." + ext):
            tmp.append(pickle.load(open(f, 'rb')))
        return tmp
    data = load_data(input_path, "tr")
    num_data = len(data)
    num_val = int(num_data * 0.3)
    x_train = data[:-num_val]
    x_val = data[-num_val:]
    data = load_data(label_path, "lb")
    y_train = data[:-num_val]
    y_val = data[-num_val:]

    return np.array(x_train), np.array(y_train), np.array(x_val), np.array(y_val)

def build_cnn():
    model = Sequential()
    model.add(Conv2D(32, kernel_size=(2, 4),
                     activation='relu',
                     input_shape=input_shape))
    model.add(Conv2D(64, (2, 4), activation='relu'))
    #model.add(MaxPooling2D(pool_size=(2, 2)))
    #model.add(Dropout(0.25))
    model.add(Flatten())
    model.add(Dense(128, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(NUM_CLASSES, activation='softmax'))
    
    model.compile(loss=keras.losses.categorical_crossentropy,
                  optimizer=keras.optimizers.Adadelta(),
                  metrics=['accuracy'])
    return model

def train(model):
    model.fit(x_train, y_train,
              batch_size=batch_size,
              epochs=epochs,
              verbose=2,
              validation_data=(x_val, y_val))
    
def evaluate(model):
    score = model.evaluate(x_val, y_val, verbose=0)
    print('Test loss:', score[0])
    print('Test accuracy:', score[1])
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-epochs", type=int, default=50)
    parser.add_argument("-batch_size", type=int, default=12)
    args = parser.parse_args()
    print(args)
    epochs = args.epochs
    batch_size = args.batch_size

    print("Loading data...")
    x_train, y_train, x_val, y_val = load_dataset(INPUT_DATA_PATH, LABEL_DATA_PATH)
    print x_train.shape
    K.set_image_dim_ordering('th') # channels first
    input_shape = x_train[0].shape
    #print input_shape
    #input_var = T.tensor4('inputs')
    #target_var = T.dmatrix('targets')
    model = build_cnn()
    train(model)
    evaluate(model)
    