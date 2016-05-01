#!/usr/bin/env python

# Use the built in json and sqlite library
import json
import sqlite3

def get_class(i):
    classes = {
        1: 'warrior',
        2: 'shaman',
        3: 'rogue',
        4: 'paladin',
        5: 'hunter',
        6: 'druid',
        7: 'warlock',
        8: 'mage',
        9: 'priest'
    }
    return classes[i]
    
def main():
    # Running card counter
    card_count = 0

    # Load all json data into a collection
    card_data = json.load(open('cardtier.json'))
    
    # Connect to our database and creat table if it doesn't exist
    db = sqlite3.connect('game.sqlite')
    c = db.cursor()
    query = """
        CREATE TABLE IF NOT EXISTS 
            scores(
                'card_game_id', 
                'draft_class', 
                'score', 
                'modifier', 
                'score_version',
                'pick_counter',
                'offer_counter', 
                UNIQUE(card_game_id,draft_class))
    """
    c.execute(query)
    
    sql_insert = "REPLACE INTO scores VALUES(?,?,?,?,?,?,?);"
    sql_exclude = "REPLACE INTO exclude VALUES(?);"
    exclude = []
    
    # Cycle through all the objects in the collection
    for card in card_data:
        i = 1
        has_score = False
        for value in card['value']:
            if value > "":
                has_score     = True
                card_id       = card['id']
                draft_class   = get_class(i)
                modifier      = value.count('*')
                score         = value.strip('\*')
                score_version = '0.1.11'
                
                c.execute(sql_insert,(card_id, draft_class, score, modifier, score_version, 0, 0))
                card_count+=1

            i += 1
        if has_score == False:
            exclude.append(card['id'])
    
    for card_id in exclude:
        c.execute(sql_exclude,(card_id, ))
        
    db.commit()        
    db.close()
    print str(card_count) + ' cards were written to the database.'
    
# Boilerplate python
if __name__ == '__main__':
    main()
