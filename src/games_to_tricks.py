# -*- coding: utf-8 -*-

import argparse
import glob
import csv
import numpy as np

np.set_printoptions(threshold=500)

DATA_PATH = '../data/'

def main():
    parser = argparse.ArgumentParser()
    #parser.add_argument("-num", type=int)
    parser.add_argument("--prediction", dest='prediction', action='store_true')
    #parser.add_argument("--small", dest='small_dataset', action='store_true')
    args = parser.parse_args()
    print(args)
    prediction = args.prediction
    path = DATA_PATH
    if prediction:
        path += 'prediction/'        
    
    files = sorted(glob.glob(DATA_PATH + 'game-protocols/' + "/*.csv"),key=lambda x: int(x.rsplit('/',1)[1].rsplit('.')[0].replace("_","")))
    for f in files:
        greader = csv.reader(open(f),delimiter=' ')       
        generate_tricks(greader,path)

        
def generate_tricks(greader,path):
    game_info = next(greader)
    assert len(game_info) == 1
    game_num = int(game_info[0])
    
    player_names = next(greader)
    assert len(player_names) == 4
    #players = [Player(p,c) for c,p in enumerate(player_names)]
    
    trick_lines = []
    card_lines = []
    handcards = [[] for i in range(4)]
    for c,row in enumerate(greader): # parse game
        if  c % 2 == 0:
            assert len(row) == 2
            trick_lines.append(row)
            trick_num = row[0]
            starting_player_num = player_names.index(row[1])
        else:
            assert len(row) == 4
            card_lines.append(row)
            #print get_cards_sorted_by_player(starting_player_num,row)
            for i in range(4):
                handcards[i].append(get_cards_sorted_by_player(starting_player_num,row)[i])
    assert len(trick_lines) == 12
    assert len(card_lines) == 12
                
    for cp,p in enumerate(player_names):
        for t in range(12):       
            ref_num = str(game_num) + '_' + str(cp) + '_' + "%02d" % t
            with open(path + 'trick-protocols/' + ref_num + '.csv', 'w') as f:
                gwriter = csv.writer(f, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                gwriter.writerow([game_num,cp,t])
                gwriter.writerow(player_names)
                gwriter.writerow(handcards[cp])
                for c in range(t):
                    gwriter.writerow(trick_lines[c])
                    gwriter.writerow(card_lines[c])
                gwriter.writerow(trick_lines[t])
                starting_player_num = player_names.index(trick_lines[t][1])
                lying_cards_num = (cp-starting_player_num + 4) % 4
                gwriter.writerow(card_lines[t][:lying_cards_num])
                gwriter.writerow(['next',card_lines[t][lying_cards_num]])


    

    
def get_cards_sorted_by_player(starting_player_num,cards):
    return cards[-starting_player_num:] + cards[:-starting_player_num]

if __name__ == '__main__':
    main()         
        
        