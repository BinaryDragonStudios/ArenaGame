#!/usr/bin/env python

# Use the built in json library
import json
import sqlite3

def main():
    # Running card counter
    card_count = 0

    # Load all json data into a collection
    card_data = json.load(open('cards.collectible.json'))
    
    # Connect to our database
    db = sqlite3.connect('game.sqlite')
    db.execute('DELETE FROM cards')
    
    # Cycle through all the objects in the collection
    for card in card_data:
        if "HERO" not in card['id']:
            card_count+=1
            # Determine if it's a neutral card or a class card
            if 'playerClass' not in card.keys():
                card_class = "NEUTRAL"
            else:
                card_class = card['playerClass']

            columns = '"' + card['id'] + '", "' + card['rarity'] + '", "' + card['set'] + '", "' + card_class + '", "' + card['name'] + '"'
            db.execute('INSERT INTO cards VALUES(' + columns + ' );')
            
    db.commit()        
    db.close()
    print card_count + " cards were written to the database."
    
# Boilerplate python
if __name__ == '__main__':
    main()
