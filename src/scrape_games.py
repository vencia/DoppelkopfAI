# scrapes protocols of 'fuchstreff top normalspiele des jahres'

import argparse
import requests
from bs4 import BeautifulSoup
import re
import os
import csv
from pathlib import Path
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

card_dict = {'Kreuz': 'C', 'Pik': 'S', 'Herz': 'H', 'Karo': 'D', 'Neun': '9', 'Zehn': '10', 'Bube': 'J', 'Dame': 'Q',
             u'König': 'K', 'Ass': 'A'}


def get_abbreviation(card_name):
    return card_dict[card_name.split('-')[0]] + card_dict[card_name.split('-')[1]]


def find_special_rules(tag):
    return tag.name == 'img' and tag.get('title') in ['Ohne Neunen', 'Zweite Dulle sticht die erste', 'Schweinchen']


starting_id = 1294
number_of_protocols = 1
DOMAIN_URL = 'https://www.fuchstreff.de/login.html'
# GAMES_URL = 'https://www.fuchstreff.de/top-spiele/jahr.html'
GAMES_URL = 'https://www.fuchstreff.de/spiele/'

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_path", type=str, default='../data/game_protocols')
    parser.add_argument("--num", type=int, default=10)
    parser.add_argument("--start", type=int, default=501)
    parser.add_argument("--username", type=str)
    parser.add_argument("--password", type=str)

    args = parser.parse_args()
    print(args)
    number_of_protocols = args.num
    starting_id = args.start
    username = args.username
    password = args.password
    data_path = Path(args.data_path)
    os.makedirs(data_path, exist_ok=True)

    # start new session to persist data between requests
    session = requests.Session()

    # retrieve csrf token
    r = session.get(DOMAIN_URL, verify=False)
    matchme = 'meta name="csrf-token" content="(.*)"'
    csrf = re.search(matchme, str(r.text))

    payload = {
        'authenticity_token': csrf.group(1),
        'login': username,
        'password': password,
    }

    # log in
    r = session.post(DOMAIN_URL, data=payload, verify=False)

    game_id = starting_id
    end_id = starting_id + number_of_protocols
    while game_id < end_id:
        game_page = session.get(GAMES_URL + str(game_id))
        soup = BeautifulSoup(game_page.text, 'lxml')
        # game_type = soup.find_all('div', 'header')[0].h1.text
        game_type = soup.find('span', 'game-info').parent.parent.h1.text
        special_rules = soup.find_all(find_special_rules)
        # print soup.find('div',"card clearfix")
        if 'Normalspiel' in game_type and not special_rules:
            # players = [p.a['data-username'] for p in soup.find_all('div', 'game-protocol__player')]
            protocol = soup.find_all('div', 'card clearfix')

            with open(data_path / (str(game_id) + '.csv'), 'w') as csvfile:
                gwriter = csv.writer(csvfile, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                for c, zug in enumerate(protocol):
                    if c == 0:
                        players = [x.get('data-username') for x in zug.find_all('a', 'profile-link')][:4]
                        player_dict = dict([(p, p) for i, p in enumerate(players)])
                        starting_player = player_dict[players[0]]
                        gwriter.writerow([game_id])
                        gwriter.writerow([player_dict[p] for p in players])
                        # player_dict = dict([(p,'P'+str(i)) for i,p in enumerate(players)])
                    trick_from = player_dict[zug.a['data-username']]
                    gwriter.writerow([str(c), starting_player])
                    starting_player = trick_from
                    cards = [get_abbreviation(k.get('title')) for k in zug.find_all('span', title=True)]
                    gwriter.writerow(cards)
        else:
            print('skip ' + game_type + " " + str([t.get('title') for t in special_rules]))
            end_id += 1
        game_id += 1
