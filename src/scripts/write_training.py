import pickle
import numpy as np

trump = [(0,0),(3,0),(4,0),(5,0),(1,0),(1,1),(1,2),(1,3),(2,0),(2,1),(2,2),(2,3),(4,1)]

def card_to_vector(card):
    vec = np.zeros((4,13))
    if card[0] < 3 and card[0] > 0:
        vec[3][4 + 4*(card[0]-1) + card[1]] = 1
    else:
        if card[1] == 0:
            if card[0] == 0:
                vec[3][0] = 1
            else:
                vec[3][card[0] - 3] = 1
        else:
            if card[0] == 4 and card[1] == 1:
                vec[3][12] == 1
            else:
                if card[0] == 0:
                    vec[card[1] - 1][0] = 1
                else:
                    vec[card[1] - 1][card[0] - 2] = 1
    return vec

def is_higher(card1,card2):
    if not card2 in trump:
        if card1 in trump:
            return True
        else:
            return card1[0] > card2[0]
    else:
        if card1 not in trump:
            return False
        else:
            return trump.index(card1) > trump.index(card2)
    
def get_highest_card_index(cards):
    highest_card_index = 0
    for i,card in enumerate(cards):
        if is_higher(card,cards[highest_card_index]):
            highest_card_index = i
    return highest_card_index        
    


def write_game(hand, tricks, current_trick, partner, ref_num, data_path):
    valid_hand_cards = np.array([np.zeros((4,13))])
    for c in hand:
        valid_hand_cards = np.add(valid_hand_cards, card_to_vector(c))

    valid_higher_hand_cards = np.array([np.zeros((4,13))])
    current_highest = current_trick[get_highest_card_index(current_trick)]
    for c in hand:
        if is_higher(c,current_highest):
            valid_higher_hand_cards = np.add(valid_higher_hand_cards, card_to_vector(c))

    lying_cards = np.array()
    for i in range(3):
        if i < len(current_trick):
            lying_cards = np.append(lying_cards, [card_to_vector(current_trick[i])], axis=0)
        else:
            lying_cards = np.append(lying_cards, [np.zeros((4,13))], axis=0)
    
    
    sum_of_card_values = np.array([np.zeros((4,5))])
    value_sum = 0
    for c in current_trick:
        value_sum += get_card_value(c)
    if value_sum > 30:
        sum_of_card_values[0][4] = 1
    elif value_sum > 20:
        sum_of_card_values[0][3] = 1
    elif value_sum > 15:
        sum_of_card_values[0][2] = 1
    elif value_sum > 10:
        sum_of_card_values[0][1] = 1
    elif value_sum > 5:
        sum_of_card_values[0][0] = 1
        
    prop_teamplayer = np.array([np.zeros((4,3))])
    if partner != 0:
        prop_teamplayer[0][partner] = 1
        
    trick_already_in_team = np.array([np.zeros((4,1))])
    if get_highest_card_index(current_trick) == partner:
        trick_already_in_team[0][0] = 1

    first_player = np.array([np.zeros((4,4))])
    first_player[0][current_trick.size] = 1
    
    
            
    #trick_cards = [np.zeros((4,13))]*4
    #for t in tricks:
    #    for i in range(len(t)):
    #        trick_cards[i] = np.add(trick_cards[i], card_to_vector(t[i]))
    #for t in trick_cards:
     #   data = np.append(data, [t], axis=0)

    data = valid_hand_cards + valid_higher_hand_cards + lying_cards + sum_of_card_values + prop_teamplayer + trick_already_in_team + first_player 
    
    pickle.dump(data, open(data_path  + 'train_{}.tr'.format(ref_num), 'wb'))

    np.savetxt(data_path  + 'data_{}.tr'.format(ref_num), data, delimiter=",")


def write_label(cards, ref_num, data_path):
    #print(cards)
    output = np.zeros((24))
    for (c,l) in cards:
        output[c[0]*4+c[1]] = l
        
    pickle.dump(output, open(data_path + 'label_{}.l'.format(ref_num), 'wb'))
