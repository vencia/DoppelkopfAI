#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import datetime
import os
import sys
import glob
import numpy as np
import argparse
import keras
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten
from keras.layers import Conv2D, MaxPooling2D
from keras import backend as K
from keras.callbacks import CSVLogger
from keras.callbacks import TensorBoard

NUM_CLASSES = 24

def load_dataset():
    def load_data(path):
        if not os.path.exists(path):
            print("Path not found: {}".format(path))
            sys.exit(0)
        tmp = []
        #files = glob.glob(path + "/*." + ext)
        files = sorted(glob.glob(path + "/*"),key=lambda x: int(x.rsplit('/',1)[1].rsplit('.')[0].replace("_","")))
        #print files[:20]
        #if dataset_size != 0 and len(files) > dataset_size:
        #    files = files[:dataset_size]
        for f in files:
            #tmp.append(pickle.load(open(f, 'rb')))
            tmp.append(np.load(open(f, 'rb')))
        return tmp
    
    x_data = load_data(net_data_path + 'input-data/')
    y_data = load_data(net_data_path + 'label-data/')
    
    # shuffle changes axes ordering??!!!
    #data = list(zip(x_data,y_data))
    #random.shuffle(data)
    #x_data[:], y_data[:] = zip(*data)
  
    num_val = int(len(x_data) * 0.2)
    x_train = x_data[:-num_val]
    x_val = x_data[-num_val:]
    y_train = y_data[:-num_val]
    y_val = y_data[-num_val:]

    return np.array(x_train), np.array(y_train), np.array(x_val), np.array(y_val)

def build_cnn():
    model = Sequential()
    model.add(Conv2D(32, kernel_size=(2, 4),
                     activation='relu',
                     input_shape=input_shape))
    model.add(Conv2D(64, (2, 4), activation='relu'))
    #model.add(MaxPooling2D(pool_size=(2, 2)))
    #model.add(Dropout(0.2))
    model.add(Flatten())
    model.add(Dense(128, activation='relu'))
    model.add(Dropout(0.2))
    model.add(Dense(NUM_CLASSES, activation='softmax'))
    
    model.compile(loss=keras.losses.categorical_crossentropy,
                  optimizer=keras.optimizers.Adam(lr=learning_rate),
                  metrics=['accuracy'])
    
    return model

def train(model):    
    history = model.fit(x_train, y_train,
              batch_size=batch_size,
              epochs=epochs,
              verbose=2,
              validation_data=(x_val, y_val), callbacks=callback_loggers)
    return history
    
def evaluate(model):
    score = model.evaluate(x_val, y_val, verbose=0)
    print('Test loss:', score[0])
    print('Test accuracy:', score[1])
    
def plot(history):
    # summarize history for accuracy
    plt.plot(history.history['acc'])
    plt.plot(history.history['val_acc'])
    plt.title('model accuracy')
    plt.ylabel('accuracy')
    plt.xlabel('epoch')
    plt.legend(['train', 'test'], loc='upper left')
    #plt.show()
    plt.savefig(model_path + 'accuracy.png')
    plt.clf()
    
    # summarize history for loss
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title('model loss')
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend(['train', 'test'], loc='upper left')
   # plt.show()
    plt.savefig(model_path + 'loss.png')
    
def get_execution_time_in_minutes(start_time):
    return int((datetime.datetime.now() - start_time).total_seconds()/60)
    
class Tee(object): # logging to console and file
    def __init__(self, *files):
        self.files = files
    def write(self, obj):
        for f in self.files:
            f.write(obj)
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    #parser.add_argument("-data_path", type=str, default='/media/vencia/Daten/DoppelkopfAI/data/')
    parser.add_argument("-net_data_path", type=str, default='../data/')
    parser.add_argument("-epochs", type=int, default=10)
    parser.add_argument("-batch_size", type=int, default=128)
    parser.add_argument("-lr", type=float, default=0.001)
    #parser.add_argument("-num_games", type=int)
    #parser.add_argument("--small", dest='small_dataset', action='store_true')


    args = parser.parse_args()
    #data_path = args.data_path
    net_data_path = args.net_data_path
    epochs = args.epochs
    batch_size = args.batch_size
    learning_rate = args.lr
        
    foldername = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
    model_path = net_data_path + foldername + '/'
    os.mkdir(model_path)
    infoFile = open(model_path + 'train_info.log', 'w')
    backup = sys.stdout
    sys.stdout = Tee(sys.stdout, infoFile)
    
    callback_loggers = []
    csv_logger = CSVLogger(model_path + 'training.csv')
    callback_loggers.append(csv_logger)
    if K.backend() == 'tensorflow':
        tensorboard_logger = TensorBoard(log_dir=model_path + 'tensorboard', histogram_freq=0, batch_size=batch_size, write_graph=True, write_grads=False, write_images=True, embeddings_freq=0, embeddings_layer_names=None, embeddings_metadata=None)
        callback_loggers.append(tensorboard_logger)
        #tensorboard --logdir=/full_path_to_your_logs

    print(args)
    print("Loading data...")
    start_loading_data = datetime.datetime.now()
    x_train, y_train, x_val, y_val = load_dataset()
    print 'Loading data took ' + str(get_execution_time_in_minutes(start_loading_data)) + ' minutes'
    
    K.set_image_dim_ordering('th')
    if K.backend() == 'theano':
        x_train = np.swapaxes(x_train,1,3)
        x_train = np.swapaxes(x_train,1,2)
        x_val = np.swapaxes(x_val,1,3)
        x_val = np.swapaxes(x_val,1,2)
        
    input_shape = x_train[0].shape
    print 'Input shape' + str(input_shape)

    model = build_cnn()

    print model.summary()
    print ''
    
    start_training = datetime.datetime.now()
    history = train(model)
    print 'Training took ' + str(get_execution_time_in_minutes(start_training)) + ' minutes'

    evaluate(model)
    
    # serialize model to JSON
    model_json = model.to_json()
    with open(model_path  + "model.json", "w") as json_file:
        json_file.write(model_json)
    # serialize weights to HDF5
    model.save_weights(model_path + "model_weights.h5")
    
    plot(history)
    