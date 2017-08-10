#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import csv

PROTOCOLS_PATH = '../../data/game-protocols-test/'
INPUT_DATA_PATH = '../../data/input-data/'
LABEL_DATA_PATH = '../../data/label-data/'

class Card:
    sortedTrump = ["D9","DK","D10","DA","DJ","HJ","SJ","CJ","DQ","HQ","SQ","CQ","H10","pig"]
    sortedNonTrumpValue = ["9","K","10","A"]
    
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
        return Card.sortedNonTrumpValue.index(self.value) > Card.sortedNonTrumpValue.index(card.value)
    
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
    def __init__(self,position,handCards):
        self.position = position
        self.handCards = handCards # handCards for trick x: handCards[x:]

class Game:
    def __init__(self,tricks):
        players = []
        sortedTricks = Game.get_tricks_sorted_by_player(tricks)
        for i in range(4):
            players.append(Player(i,[trick.cards[i] for trick in sortedTricks]))
            
        self.players = players
        self.tricks = tricks
    
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
        print game
        print "----------"
        #sortedGame = Game(game.players,game.get_tricks_sorted_by_player())
        #print sortedGame
        print game.get_cards_valid_to_play(1,0)
        
        