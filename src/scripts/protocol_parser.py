#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import csv

PROTOCOLS_PATH = '../../data/game-protocols-test/'
INPUT_DATA_PATH = '../../data/input-data/'
LABEL_DATA_PATH = '../../data/label-data/'

class Card:
    sortedTrump = ["D9","DK","D10","DA","DJ","HJ","SJ","CJ","DQ","HQ","SQ","CQ","H10","pig"]
    sortedNonTrumpValues = ["9","K","10","A"]
    cardPointValues = {"9":0,"J":2,"Q":3,"K":4,"10":10,"A":11}
    
    def __init__(self, shortcut): 
        self.shortcut = shortcut
        self.suit = shortcut[0]
        self.value = shortcut[1:]
        
    def is_trump(self):
        return self.shortcut in Card.sortedTrump
    
    def is_higher_than(self,card):
        if self.is_trump():
            if not card.is_trump():
                return True
            return Card.sortedTrump.index(self.shortcut) > Card.sortedTrump.index(card.shortcut)
        if card.is_trump():
            return False
        if self.suit != card.suit:
            return False
        return Card.sortedNonTrumpValues.index(self.value) > Card.sortedNonTrumpValues.index(card.value)
    
    def get_point_value(self):
        return Card.cardPointValues[self.value]
    
    def __str__(self):
        s = self.suit + self.value
        if self.is_trump():
            s += " (T)"
        return s
    
    def __repr__(self):
        return self.__str__()
        
class Trick:
    def __init__(self, cards, startingPlayer, winningPlayer):
        self.cards = cards
        self.startingPlayer = startingPlayer
        self.winningPlayer = winningPlayer
        

class Player:
    def __init__(self,number,handCards):
        self.number = number
        self.handCards = handCards # handCards for trick x: handCards[x:]
        self.isRe = len([card for card in handCards if card.shortcut == "CQ"]) > 0

class Game:
    def __init__(self,tricks):
        players = []
        sortedTricks = Game.get_tricks_sorted_by_player(tricks)
        for i in range(4):
            players.append(Player(i,[trick.cards[i] for trick in sortedTricks])) 
            
        self.players = players
        self.tricks = tricks
        
        reQueens = []
        for t,trick in enumerate(self.tricks):
            for p,card in enumerate(trick.cards):
                if card.shortcut == "CQ":
                    reQueens.append((t,p))
                    
        self.reQueens = reQueens # list with entries (trick_num,player_pos) for re-queens
                    
            
    
    def get_cards_valid_to_play(self,player_num,trick_num):
        cards = self.players[player_num].handCards[trick_num:]
        if self.tricks[trick_num].startingPlayer == player_num:
            firstCard = None
        else:
            firstCard = self.tricks[trick_num].cards[0]
        if firstCard is None:
            return cards
        if firstCard.is_trump():
            trumps = [c for c in cards if c.is_trump()]
            if not trumps:
                return cards
            return trumps
        sameSuit = [c for c in cards if (c.suit == firstCard.suit and not c.is_trump())]
        if not sameSuit:
            return cards
        return sameSuit   
    
    def get_player_position(self,player_num,trick_num):
        return (player_num - self.tricks[trick_num].startingPlayer + 4) % 4
    
    def get_player_at_position(self,position,trick_num):
        return (position + self.tricks[trick_num].startingPlayer) % 4

    def get_currently_lying_cards(self,player_num,trick_num):
        return self.tricks[trick_num].cards[:self.get_player_position(player_num,trick_num)]
    
    def get_probs_teamplayer(self,player_num,trick_num):
        outedRePlayers = []
        for (re_t,re_p) in self.reQueens:
            if re_t < trick_num or (re_t == trick_num and re_p < self.get_player_position(player_num,trick_num)):
                outedRePlayers.append(self.get_player_at_position(re_p,re_t))
                
        print outedRePlayers
                
        probs = [0.0]*4          
        if self.players[player_num].isRe:
            if len(outedRePlayers) > 0:
                probs[outedRePlayers[0]] = 1.0
            else:
                probs = [0.3]*4
        else:
            if len(outedRePlayers) > 1:
                probs = [1.0]*4
                probs[outedRePlayers[0]] = 0.0
                probs[outedRePlayers[1]] = 0.0
            elif len(outedRePlayers) > 0:
                probs = [0.5]*4
                probs[outedRePlayers[0]] = 0.0
            else:
                probs = [0.3]*4 
        probs[player_num] = 1.0       
        return probs    
    
    @staticmethod
    def rotate(lst, pos):
        return lst[-pos:] + lst[:-pos]
    
    @staticmethod    
    def get_tricks_sorted_by_player(tricks):
        firstPlayer = 0
        sortedTricks = []
        for trick in tricks:
            sortedTricks.append(Trick(Game.rotate(trick.cards,firstPlayer),trick.startingPlayer,trick.winningPlayer))
            firstPlayer = trick.winningPlayer
        return sortedTricks
      
    def __str__(self):
        s = ""
        for t,trick in enumerate(self.tricks):
            s += "trick " + str(t) +  ", starting player " + str(trick.startingPlayer) + ", winning player " + str(trick.winningPlayer) + "\n" + str(trick.cards) + "\n"
        return s
    
    

for csvfile in os.listdir(PROTOCOLS_PATH):
    if csvfile.endswith('.csv'):
        f = open(PROTOCOLS_PATH + csvfile)
        greader = csv.reader(f, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        tricks = []
        startingPlayer = 0
        for row_count,row in enumerate(greader):
            if row_count % 2 == 0:
                winningPlayer = int(row[1][1])
            else:
                cards = []
                for r in row:
                    cards.append(Card(r))
                tricks.append(Trick(cards,startingPlayer,winningPlayer))
                startingPlayer = winningPlayer
        game = Game(tricks)
        
        
        
        