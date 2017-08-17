# -*- coding: utf-8 -*-

import argparse
import glob
import csv
import numpy as np

np.set_printoptions(threshold=500)

DATA_PATH = '../data/'

class Player:
    def __init__(self,name,number):
        self.name = name
        self.number = number # equals index in players
        self.handcards = [] # all (known) handcards -> full for bot
        self.played_cards = [] # sorted: played_cards[:trick_num] for already played cards for current trick
        #self.isRe = len([card for card in self.handcards if card.shortcut == "CQ"]) > 0
        
    def set_handcards(self,cards):
        assert len(cards) == 12
        self.handcards = sorted(cards,key=Card.sorted_cards.index)

    def __str__(self):
        return self.name + " " + str(self.number)
    
    def __repr__(self):
        return self.__str__()
        
class Card:
    sorted_trump = ["D9","DK","D10","DA","DJ","HJ","SJ","CJ","DQ","HQ","SQ","CQ","H10","pig"]
    sorted_non_trump_values = ["9","K","10","A"]
    sorted_values = ["9","10","J","Q","K","A"]
    sorted_suits = ["D","H","S","C"]
    sorted_cards = ["H9","HK","HA","S9","SK","S10","SA","C9","CK","C10","CA"] + sorted_trump
    card_point_values = {"9":0,"J":2,"Q":3,"K":4,"10":10,"A":11}
    
    def __init__(self, shortcut): 
        assert shortcut in self.sorted_cards
        self.shortcut = shortcut
        self.suit = shortcut[0]
        self.value = shortcut[1:]
        
    def is_trump(self):
        return self.shortcut in Card.sorted_trump
    
    def is_higher_than(self,card):
        if card is None:
            return True
        if self.is_trump():
            if not card.is_trump():
                return True
            return Card.sorted_trump.index(self.shortcut) > Card.sorted_trump.index(card.shortcut)
        if card.is_trump():
            return False
        if self.suit != card.suit:
            return False
        return Card.sorted_non_trump_values.index(self.value) > Card.sorted_non_trump_values.index(card.value)
    
    def get_point_value(self):
        return Card.card_point_values[self.value]
    
    def __str__(self):
        s = self.suit + self.value
        if self.is_trump():
            s += " (T)"
        return s
    
    def __repr__(self):
        return self.__str__()
    
    def __eq__(self, other):
        if isinstance(other, Card):
            return self.shortcut == other.shortcut
        return NotImplemented
    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result
        
class Trick:
    def __init__(self, starting_player, cards, number):
        self.starting_player = starting_player
        self.cards = cards
        self.number = number # equals index in tricks
        
    def get_cards_sorted_by_player(self):
        return self.cards[-self.starting_player.number:] + self.cards[:-self.starting_player.number]
        
class Game:
    def __init__(self,game_num,bot_num,current_trick_num,players):   
        self.game_num = game_num
        self.bot_num
        self.current_trick_num
        self.players = players
        self.tricks = []
    
    def add_trick(self,trick):
        assert len(self.tricks) <= self.current_trick_num
        
        # fill up trick with Nones
        for i in range(4-len(trick.cards)):
            trick.cards.append(None)
        self.tricks.append(trick)
        
        # add cards to played cards of players
        for p in self.players:
            played_card = trick.get_cards_sorted_by_player()[p.number]
            if played_card is not None:
                p.played_cards.append(played_card)
             
    def get_current_handcards(self,player_num,trick_num):
        handcards_copy = self.players[player_num].handcards[:]
        for card in self.players[player_num].played_cards[:trick_num]:
            handcards_copy.remove(card)
        return handcards_copy   
        
    def get_valid_handcards(self,player_num,trick_num):
        cards = self.get_current_handcards(player_num,trick_num)
        if self.tricks[trick_num].starting_player.number == player_num:
            return cards

        first_card = self.tricks[trick_num].cards[0]
        if first_card.is_trump():
            trumps = [c for c in cards if c.is_trump()]
            if not trumps:
                return cards
            return trumps
        same_suit = [c for c in cards if (c.suit == first_card.suit and not c.is_trump())]
        if not same_suit:
            return cards
        return same_suit
        


    def __str__(self):
        s = ""
        for c,t in enumerate(self.tricks):
            s += "trick " + str(c) +  ", starting player " + str(t.starting_player) + "\n" + str(t.cards) + "\n"
        return s

    def __repr__(self):
        return self.__str__()        

def main():
    parser = argparse.ArgumentParser()
    #parser.add_argument("-num", type=int)
    parser.add_argument("--prediction", dest='prediction', action='store_true')
    #parser.add_argument("--small", dest='small_dataset', action='store_true')
    args = parser.parse_args()
    print(args)
    prediction = args.prediction
    
    files = sorted(glob.glob(DATA_PATH + 'game-protocols/' + "/*.csv"),key=lambda x: int(x.rsplit('/',1)[1].rsplit('.')[0].replace("_","")))
    for f in files:
        greader = csv.reader(open(f))       
        game = parse_game(greader)
        input_data = generate_input_data(game)
        
        path = DATA_PATH
        if prediction:
            path += 'prediction/'        
        ref_num = str(game.game_num) + '_' + str(game.bot.number) + '_' + "%02d" % game.current_trick.number
        np.save(open(path + 'input-data/' + ref_num, 'wb'),input_data)   
            
def generate_input_data(game):
    b = game.bot.number
    t = game.current_trick.number
    handcards_layer = get_card_matrix(game.get_current_handcards(b,t)) 
    
    valid_handcards_layer = get_card_matrix(game.get_valid_handcards(b,t))
    
    valid_higher_handcards_layer = get_card_matrix(game.get_valid_higher_handcards(b,t))

    lying_cards = game.get_currently_lying_cards(b,t)
    lying_cards_layer = get_card_matrix(lying_cards)
    
    lying_cards_sum = 0
    for card in lying_cards:
        lying_cards_sum += card.get_point_value()
    entryIdx = 0
    if lying_cards_sum >= 5:
        entryIdx += 1
    if lying_cards_sum >= 10:
        entryIdx += 1
    if lying_cards_sum >= 20:
        entryIdx += 1
    if lying_cards_sum > 30:
        entryIdx += 1        
    entries = [0]*5
    entries[entryIdx] = 1
    lying_cards_sum_units = get_entry_matrix(entries)
        
    trick_in_team = game.is_trick_in_team(b,t)
    entries = [0]
    if trick_in_team:
        entries = [1]
    trick_in_team_units = get_entry_matrix(entries)
    
    probs_teamplayer_units = get_entry_matrix(game.get_probs_teamplayer(b,t))
    
    entry_idx = game.tricks[t].starting_player.number
    entries = [0]*4
    entries[entry_idx] = 1
    starting_player_units = get_entry_matrix(entries)
    
    more_infos_layer = np.hstack((lying_cards_sum_units,trick_in_team_units,probs_teamplayer_units,starting_player_units))
        
    input_data = np.stack((handcards_layer,valid_handcards_layer,valid_higher_handcards_layer,lying_cards_layer,more_infos_layer),axis = 0)
    
    return input_data    
    
        
def parse_game(greader):
    game_info = next(greader)
    assert len(game_info) == 3
    game_num = int(game_info[0])
    bot_num = int(game_info[1])
    current_trick_num = int(game_info[2])
    
    player_names = next(greader)
    assert len(player_names) == 4
    players = [Player(p,c) for c,p in enumerate(player_names)]
    
    handcards_bot = next(greader)
    assert len(handcards_bot) == 12
    players[bot_num].set_handcards([Card(h) for h in handcards_bot])
    
    game = Game(game_num,bot_num,current_trick_num,players)
    
    tricks = []
    for c,row in enumerate(greader): # parse game
        if  c % 2 == 0:
            assert len(row) == 2
            trick_num = row[0]
            starting_player = [p for p in players if p.name == row[1]][0]
        else:
            assert len(row) <= 4
            lying_cards =[Card(card_shortcut) for card_shortcut in row]
            if len(row) < 4:
                assert current_trick_num == trick_num
            game.add_trick(Trick(starting_player,lying_cards,trick_num))
    
    if bot_num == starting_player.number:
        assert len(tricks[len(tricks)-1].cards) == 4
        trick_num += 1
        game.add_trick(Trick(starting_player,[],trick_num))
        
    return game
    
def get_card_matrix(cards):
    matrix = np.zeros(shape=(4,14))
    for card in cards:
        row = Card.sortedSuits.index(card.suit)
        if card.value in Card.sortedNonTrumpValues:
            if card.shortcut == "H10":
                column = 12
            else:
                column = Card.sortedNonTrumpValues.index(card.value)
        else:
            column = Card.sortedTrump.index(card.shortcut)
        matrix[row][column] += 1
    return matrix

def get_entry_matrix(entries):
    matrix = np.zeros(shape=(4,len(entries)))
    for e,entry in enumerate(entries):
        matrix[0][e] = entry
    return matrix
            
if __name__ == '__main__':
    main()         
        
        
        

        
        
    
    