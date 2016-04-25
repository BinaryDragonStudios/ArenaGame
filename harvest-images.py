#!/usr/bin/env python

# Use the built in json and sqlite library
import sqlite3

def card_image_url(card_game_id):
    return "http://wow.zamimg.com/images/hearthstone/cards/enus/original/" + card_game_id + ".png"

def main():
    sql = "SELECT card_game_id, card_name_en  FROM cards ORDER BY card_name_en"
    db = sqlite3.connect('game.sqlite')
    c = db.cursor()
    f = open('harvest-images.sh', 'w')
    f.write("#!/usr/bin/env bash\n")
    for row in c.execute(sql):
        harvest_url = card_image_url(row[0])
        f.write('wget ' + harvest_url + "\n")
        # print harvest_url
    f.close()

# Boilerplate python
if __name__ == '__main__':
    main()
