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
    db = sqlite3.connect('game.sqlite');

    # Cycle through all the objects in the collection
    for card in card_data:
        # Check if an object is a card. default to it is for our purposes
        # then attempt to prove that it isn't a card.
        is_a_card = True
    
        # Look for the following properties to check if it is a card.
        # if 'rarity' not in card.keys(): is_a_card = False
        # if 'id' not in card.keys(): is_a_card = False
        # if 'set' not in card.keys(): is_a_card = False
        # if 'flavor' not in card.keys(): is_a_card = False
        if "HERO" in card['id']: is_a_card = False
        
        # If it is determined to be a card print out data about the card...
        if is_a_card:
            # Start off by incrementing our card counter
            card_count+=1
            # Print out it's info
            print "     Card Name: " + card['name']
            print "   Card Rarity: " + card['rarity']
            print "       Card ID: " + card['id']
            print "     Card Set : " + card['set']
            
            # Determine if it's a neutral card or a class card
            if 'playerClass' not in card.keys():
                print "   Card Class : NEUTRAL"
            else:
                print "   Card Class : " + card['playerClass']
                
            # Print a blank line for clarity
            print ""
    print "Cards found: " + str(card_count)
    db.close()

# Boilerplate python
if __name__ == '__main__':
    main()
