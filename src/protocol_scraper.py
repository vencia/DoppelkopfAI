# -*- encoding: utf-8 -*-
# scrapes all protocols of 'fuchstreff top normalspiele des jahres'

import requests
from bs4 import BeautifulSoup
import re
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import csv
import os

card_dict = {'Kreuz' : 'C', 'Pik' : 'S', 'Herz' : 'H', 'Karo' : 'D', 'Neun' : '9', 'Zehn' : '10', 'Bube' : 'J', 'Dame' : 'Q', u'König' : 'K', 'Ass' : 'A'}

def get_abbreviation(card_name):
    return card_dict[card_name.split('-')[0]] + card_dict[card_name.split('-')[1]] 
    
def find_special_rules(tag):
    return tag.name == 'img' and tag.get('title') in ['Ohne Neunen', 'Zweite Dulle sticht die erste', 'Schweinchen']


STARTING_ID = 500
NUMBER_OF_PROTOCOLS = 50
DOMAIN_URL = 'https://www.fuchstreff.de/login.html'
#GAMES_URL = 'https://www.fuchstreff.de/top-spiele/jahr.html'
GAMES_URL = 'https://www.fuchstreff.de/spiele/'
USER = 'vollzeitspieler'
PASSWORD = '123456'
DATA_PATH = os.path.dirname(os.getcwd()) + '/game-protocols/'

# start new session to persist data between requests
session = requests.Session()

# retrieve csrf token
r = session.get(DOMAIN_URL,verify = False)
matchme = 'meta name="csrf-token" content="(.*)"'
csrf = re.search(matchme,str(r.text))

payload = {
'authenticity_token': csrf.group(1),
'login': USER,
'password': PASSWORD,
}

# log in
r = session.post(DOMAIN_URL, data=payload, verify = False)

# go to game listing page 
#games = session.get(GAMES_URL)

# go to a game page
#matchme = 'a class="vote-widget__button" href="(.*)"'
#links = re.findall(matchme,str(games.text))

#for link in links:
#    linkname = link.rsplit('/',1)[1]
#    if linkname.split('-')[1] == 'normalspiel':
#        print(linkname)
#        game_id = linkname.split('-')[0]
game_id = STARTING_ID
end_id = STARTING_ID + NUMBER_OF_PROTOCOLS
while game_id < end_id:
    game_page = session.get(GAMES_URL + str(game_id))
    soup = BeautifulSoup(game_page.text, 'lxml')
    game_type = soup.find_all('div', 'header')[0].h1.text
    special_rules = soup.find_all(find_special_rules)
            
    if 'Normalspiel' in game_type and not special_rules: 
        #players = [p.a['data-username'] for p in soup.find_all('div', 'game-protocol__player')]
        protocol = soup.find_all('div', 'trick-protocol trick-container')
        with open(DATA_PATH + str(game_id) + '.csv', 'w') as csvfile:
            gwriter = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for c, zug in enumerate(protocol):
                if c == 0:
                    players = [x.get('data-username') for x in zug.find_all('a', 'profile-link')]
                    player_dict = dict([(p,'P'+str(i)) for i,p in enumerate(players)])
                trick_from = player_dict[zug.a['data-username']]
                gwriter.writerow([str(c+1), trick_from])
                cards = [get_abbreviation(k.get('title')) for k in zug.find_all('span', title=True)]
                gwriter.writerow(cards)
    else:
        print('skip ' + game_type + " " + str([t.get('title') for t in special_rules]))
        end_id += 1
    game_id += 1
