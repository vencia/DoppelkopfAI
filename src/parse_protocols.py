#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import argparse
import sys
import glob
import csv
import numpy as np
import pickle

np.set_printoptions(threshold=500)

DATA_PATH = '../data/'

class Card:
    sortedTrump = ["D9","DK","D10","DA","DJ","HJ","SJ","CJ","DQ","HQ","SQ","CQ","H10","pig"]
    sortedNonTrumpValues = ["9","K","10","A"]
    sortedValues = ["9","10","J","Q","K","A"]
    sortedSuits = ["D","H","S","C"]
    #sortedCards = ["H9","HK","HA","S9","SK","S10","SA","C9","CK","C10","CA"] + sortedTrump
    cardPointValues = {"9":0,"J":2,"Q":3,"K":4,"10":10,"A":11}
    
    def __init__(self, shortcut): 
        self.shortcut = shortcut
        self.suit = shortcut[0]
        self.value = shortcut[1:]
        
    def is_trump(self):
        return self.shortcut in Card.sortedTrump
    
    def is_higher_than(self,card):
        if card is None:
            return True
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
    def __init__(self, cards, startingPlayer, winningPlayer):
        self.cards = cards
        self.startingPlayer = startingPlayer
        self.winningPlayer = winningPlayer
        

class Player:
    def __init__(self,name,number,handcards):
        self.name = name
        self.number = number
        self.handcards = handcards # not sorted
        self.played_cards = [] # sorted: played_cards[:trick_num] for already played cards for current trick
        self.isRe = len([card for card in self.handcards if card.shortcut == "CQ"]) > 0

    def __str__(self):
        return self.name + " " + str(self.number)
    
    def __repr__(self):
        return self.__str__()

class Game(object):
    def __init__(self,gameID,players,tricks):     
        self.players = players
        self.gameID = gameID
        self.tricks = tricks
        self.game_type = 'full'
        
        sortedTricks = Game.get_tricks_sorted_by_player(self.tricks)
        for p,player in enumerate(self.players):
            #print player
            player.handcards = []
            for trick in sortedTricks:
                if p < len(trick.cards) and trick.cards[p]:
                    player.handcards.append(trick.cards[p])
                    player.played_cards.append(trick.cards[p])
                    #print player.played_cards
              
        reQueens = []
        for t,trick in enumerate(self.tricks):
            for p,card in enumerate(trick.cards):
                if card and card.shortcut == "CQ":
                    reQueens.append((t,p))
                    
        self.reQueens = reQueens # list with entries (trick_num,player_pos) for re-queens
        
    def get_handcards(self,player_num,trick_num):
        return [c for c in self.players[player_num].handcards if c not in (self.players[player_num].played_cards[:trick_num])]
                    
    def get_valid_handcards(self,player_num,trick_num): # handcards that are valid to play in current trick
        cards = self.get_handcards(player_num,trick_num)
        if self.tricks[trick_num].startingPlayer.number == player_num:
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
    
    def get_valid_higher_handcards(self,player_num,trick_num): # valid handcards that are higher than currently lying cards
        currentHighestCardPos = self.get_current_highest_card_pos(player_num,trick_num)
        currentHighestCard = None
        if currentHighestCardPos:
            currentHighestCard = self.tricks[trick_num].cards[currentHighestCardPos]
        return [card for card in self.get_valid_handcards(player_num,trick_num) if card.is_higher_than(currentHighestCard)] 
                
        
    def get_current_highest_card_pos(self,player_num,trick_num): # returns -1 if no currently lying card
        currentlyLyingCards = self.get_currently_lying_cards(player_num,trick_num)
        if currentlyLyingCards is None:
            return None
        highestCardPos = 0
        for c,card in enumerate(currentlyLyingCards):
            if card.is_higher_than(self.tricks[trick_num].cards[highestCardPos]):
                highestCardPos = c
        return highestCardPos
            
    
    def get_player_position(self,player_num,trick_num):
        return (player_num - self.tricks[trick_num].startingPlayer.number + 4) % 4
    
    def get_player_at_position(self,position,trick_num):
        return (position + self.tricks[trick_num].startingPlayer.number) % 4

    def get_currently_lying_cards(self,player_num,trick_num):
        return self.tricks[trick_num].cards[:self.get_player_position(player_num,trick_num)]
    
    def get_probs_teamplayer(self,player_num,trick_num):
        outedRePlayers = []
        for (re_t,re_p) in self.reQueens:
            if re_t < trick_num or (re_t == trick_num and re_p < self.get_player_position(player_num,trick_num)):
                outedRePlayers.append(self.get_player_at_position(re_p,re_t))
                
        #print outedRePlayers
                
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

    def is_trick_in_team(self,player_num,trick_num):
        probs = self.get_probs_teamplayer(player_num,trick_num)
        teamplayer = None
        for p,prob in enumerate(probs):
            if prob == 1.0 and p != player_num:
                teamplayer = p
        if teamplayer is None:
            return False
        highestCardPos = self.get_current_highest_card_pos(player_num,trick_num)
        if game.get_player_position(teamplayer,trick_num) == highestCardPos:
            return True
        return False
    
    @staticmethod
    def rotate(lst, pos):
        return lst[-pos:] + lst[:-pos]
    
    @staticmethod    
    def get_tricks_sorted_by_player(tricks):
        firstPlayer = 0
        sortedTricks = []
        for trick in tricks:
            sortedTricks.append(Trick(Game.rotate(trick.cards,firstPlayer),trick.startingPlayer,trick.winningPlayer))
            if trick.winningPlayer:
                firstPlayer = trick.winningPlayer.number
        return sortedTricks
      
    def __str__(self):
        s = ""
        for t,trick in enumerate(self.tricks):
            s += "trick " + str(t) +  ", starting player " + str(trick.startingPlayer) + ", winning player " + str(trick.winningPlayer) + "\n" + str(trick.cards) + "\n"
        return s
        
class LiveGame(Game):
    def __init__(self,gameID,players,tricks,bot,bot_handcards):     
        super(LiveGame, self ).__init__(gameID,players,tricks)
        self.bot = bot
        self.bot.handcards = bot_handcards
        self.current_trick_num = len(tricks)-1
        self.game_type = 'live'
 
    
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
            
    
def generate_input_data(game,bot_num,trick_num):
    handcardsLayer = get_card_matrix(game.get_handcards(bot_num,trick_num))
    
    validHandCardsLayer = get_card_matrix(game.get_valid_handcards(bot_num,trick_num))
    
    validHigherHandCardsLayer = get_card_matrix(game.get_valid_higher_handcards(bot_num,trick_num))

    lyingCards = game.get_currently_lying_cards(bot_num,trick_num)
    lyingCardsLayer = get_card_matrix(lyingCards)
    
    lyingCardsSum = 0
    for card in lyingCards:
        lyingCardsSum += card.get_point_value()
    entryIdx = 0
    if lyingCardsSum >= 5:
        entryIdx += 1
    if lyingCardsSum >= 10:
        entryIdx += 1
    if lyingCardsSum >= 20:
        entryIdx += 1
    if lyingCardsSum > 30:
        entryIdx += 1        
    entries = [0]*5
    entries[entryIdx] = 1
    lyingCardsSumUnits = get_entry_matrix(entries)
        
    trickInTeam = game.is_trick_in_team(bot_num,trick_num)
    entries = [0]
    if trickInTeam:
        entries = [1]
    trickInTeamUnits = get_entry_matrix(entries)
    
    probsTeamPlayerUnits = get_entry_matrix(game.get_probs_teamplayer(bot_num,trick_num))
    
    entryIdx = game.tricks[trick_num].startingPlayer.number
    entries = [0]*4
    entries[entryIdx] = 1
    firstPlayerUnits = get_entry_matrix(entries)
    
    moreInfosLayer = np.hstack((lyingCardsSumUnits,trickInTeamUnits,probsTeamPlayerUnits,firstPlayerUnits))
        
    inputData = np.stack((handcardsLayer,validHandCardsLayer,validHigherHandCardsLayer,lyingCardsLayer,moreInfosLayer),axis = 0)
    
    #if bot_num == 2 and trick_num == 9:
    #    print inputData
        
    return inputData
    
def generate_label_data(game,bot_num,trick_num):
    vector = np.zeros(24)
    playedCard = game.tricks[trick_num].cards[game.get_player_position(bot_num,trick_num)]
    playedCardIdx = Card.sortedValues.index(playedCard.value) + Card.sortedSuits.index(playedCard.suit)*6
    vector[playedCardIdx] = 1
    #if bot_num == 1 and trick_num == 9:
    #    print vector
    
    return vector
    
def parse_full_protocol(gameID,rows):
    tricks = []
    players = []
    for row_count,row in enumerate(rows):
        if row_count == 0:
            players = [Player(r,c,[]) for (c,r) in enumerate(row)]
            startingPlayer = players[0]
        elif row_count % 2 == 1:
            winningPlayer = [p for p in players if p.name == row[1]][0]
        else:
            cards = []
            for r in row:
                cards.append(Card(r))
            tricks.append(Trick(cards,startingPlayer,winningPlayer))
            startingPlayer = winningPlayer
    return Game(gameID,players,tricks)
        
def parse_live_protocol(gameID,rows):
    tricks = []
    players = []
    for row_count,row in enumerate(rows):
        if row_count == 0:
            players = [Player(r,c,[]) for (c,r) in enumerate(row)]
            startingPlayer = players[0]
        elif row_count == 1:
            bot = [p for p in players if p.name == row[0]][0]
            bot_handcards = []
            for r in row[1:]:
                bot_handcards.append(Card(r))
        elif row_count % 2 != 1:
            assert int(row[0]) == len(tricks) + 1
            if len(row) > 1:
                winningPlayer = [p for p in players if p.name == row[1]][0]
            else:
                winningPlayer = None
        else:
            cards = []
            for r in row:
                cards.append(Card(r))
            tricks.append(Trick(cards,startingPlayer,winningPlayer))
            startingPlayer = winningPlayer
    if len(tricks) == 0 or len(tricks[len(tricks)-1].cards) == 4: # bot is first -> no cards lying
        assert startingPlayer == bot
        assert winningPlayer == None
        tricks.append(Trick([],startingPlayer,winningPlayer))
    for i in range(4-len(tricks[len(tricks)-1].cards)):
        tricks[len(tricks)-1].cards.append(None)
    return LiveGame(gameID,players,tricks,bot,bot_handcards)
    
def write_data(game,bot_num,trick_num,protocol_type):
    inputData = generate_input_data(game,bot_num,trick_num)
    if not prediction:
        labelData = generate_label_data(game,bot_num,trick_num)
          
    refNum = game.gameID + '_' + str(bot_num) + '_' + "%02d" % trick_num

 
    INPUT_PATH = DATA_PATH + 'input-data'
    LABEL_PATH = DATA_PATH + 'label-data'
    if small_dataset:
        INPUT_PATH += '-small'
        LABEL_PATH += '-small'
    if prediction:
        INPUT_PATH += '-' + protocol_type
    INPUT_PATH += '/'
    LABEL_PATH += '/'
      
    #pickle.dump(inputData, open(INPUT_PATH + refNum + '.tr', 'wb'))
    #if not prediction:
    #    pickle.dump(labelData, open(LABEL_PATH + refNum + '.lb', 'wb')) 
    np.save(open(INPUT_PATH + refNum, 'wb'),inputData)
    if not prediction:
        np.save(open(LABEL_PATH + refNum, 'wb'),labelData)
    
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    #parser.add_argument("-num", type=int)
    parser.add_argument("--prediction", dest='prediction', action='store_true')
    parser.add_argument("--small", dest='small_dataset', action='store_true')
    args = parser.parse_args()
    print(args)
    #number_of_protocols = args.num  
    prediction = args.prediction
    small_dataset = args.small_dataset
    if small_dataset and prediction:
        print 'either small trainingset or prediction, not both'
        sys.exit(0)
    number_of_protocols = None
    if small_dataset:
        number_of_protocols = 100

    if prediction:
        DATA_PATH += 'prediction/'
    
    #files = sorted(glob.glob(DATA_PATH + 'game-protocols/' + "/*." + 'csv'),key=lambda x: int(x.rsplit('/',1)[1].rsplit('.')[0]))
    files = sorted(glob.glob(DATA_PATH + 'game-protocols/' + "/*.csv"),key=lambda x: int(x.rsplit('/',1)[1].rsplit('.')[0].replace("_","")))
    if number_of_protocols and len(files) > number_of_protocols:
        files = files[:number_of_protocols]
    for csvfile in files:
        greader = csv.reader(open(csvfile), delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        gameID = csvfile.rsplit('/',1)[1].split('_')[0].split('.')[0]
        firstRow = next(greader)
        if firstRow[0] == 'live-protocol':
            if prediction:
                t = int(csvfile.split('_')[2].split('.')[0])
                b = int(csvfile.split('_')[1].split('.')[0])
                game = parse_live_protocol(gameID,greader)
                if b == game.bot.number and t == game.current_trick_num:
                    write_data(game,b,t,'live')
                    print game.game_type + " game " + game.gameID + '_' + str(b) + '_' + "%02d" % t
                else:
                    print 'skip ' + game.game_type + " game " + game.gameID + '_' + str(b) + '_' + "%02d" % t + ', live protocol name differs from content'
                    print b
                    print game.bot.number
                    print t
                    print game.current_trick_num
            else:
                print 'skip, no live protocols as training data supported'
        elif firstRow[0] == 'full-protocol':
            game = parse_full_protocol(gameID,greader)             
            for bot_num in range(4):
                for trick_num in range(12):
                    write_data(game,bot_num,trick_num,'full')
            print game.game_type + " game " + game.gameID           
        else:
            print 'skip ' + game.gameID + ', invalid first line of protocol: ' + str(firstRow)
        
            
            
            