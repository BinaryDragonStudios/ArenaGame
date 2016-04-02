#!/usr/bin/env python

# Use the built in json and sqlite library
import json
import sqlite3

def main():
    # Running card counter
    card_count = 0

    # Load all json data into a collection
    card_data = json.load(open('cards.collectible.json'))
    
    # Connect to our database and creat table if it doesn't exist
    db = sqlite3.connect('game.sqlite')
    c = db.cursor()
    query = "CREATE TABLE IF NOT EXISTS cards('card_game_id', 'rarity', 'set', 'class', 'card_name_en',UNIQUE(card_game_id));"
    c.execute(query)
    
    # Cycle through all the objects in the collection
    for card in card_data:
        if "HERO" not in card['id']:
            card_count+=1
            
            # Determine if it's a neutral card or a class card
            if 'playerClass' not in card.keys():
                card_class = "NEUTRAL"
            else:
                card_class = card['playerClass']
            
            # Insert into database
            new_card = ( card['id'], card['rarity'],  card['set'], card_class, card['name'])
            c.execute('REPLACE INTO cards VALUES(?,?,?,?,?)', new_card)
            
    db.commit()        
    db.close()
    print str(card_count) + ' cards were written to the database.'
    
# Boilerplate python
if __name__ == '__main__':
    main()
