#!/usr/bin/env python

import sys
import sqlite3

def main():
    
    # Connect to our database and create scores table if it doesn't exist
    db = sqlite3.connect('game.sqlite')
    c = db.cursor()
    query = "CREATE TABLE IF NOT EXISTS scores('card_game_id', 'draft_class', 'score', 'modifier', 'score_version','pick_counter','offer_counter', UNIQUE(card_game_id,draft_class))"
    c.execute(query)
    
    score_version = '20150703' # Maybe make this a parameter?

    select_card_id_query = 'SELECT card_game_id FROM cards WHERE card_name_en = ? LIMIT 1'
    
    class_list = ['druid', 'hunter', 'mage', 'paladin', 'priest', 'rogue', 'shaman', 'warlock', 'warrior']
    
    for draft_class in class_list:
    
        # Open CSV file
        csv_file = open('scores/' + draft_class + '.csv', 'rb')
        
        with csv_file:
            # Boolean keeping track of the value (card name or score); first value is always card name
            is_card_name = True
            
            # Keep track of the cards processed (by card_game_id)
            processed = []
            
            # Card counter
            card_count = 0
            
            for line in csv_file:
                # All rows with relevant data starts with ; or  -
                if line[0] in [';','-']:
                
                    # Split the comma seperated data into a list and cycle through it
                    for content in line.split(';'):
                        
                        # Trim white spaces
                        value = content.strip()
                        
                        # Skip content that is not a card or a score
                        if value not in ['', '---lower half---', '---upper half---', '(empty)']:
                        
                            # If the value is the card name: get the card ID from the cards table
                            if is_card_name:
                                c.execute(select_card_id_query, (value,))
                                row = c.fetchone()
                                card_game_id = row[0]                        
                                processed.append(card_game_id)

                                # If the value is not the card name, it's the associated score
                            else:
                            
                                # The score may have a modifier, indicated by a *, we store them seperatly
                                modifier = value.count('*')
                                score = value.strip('\*')
                                
                                # Now that we have all available card data, insert them into the database
                                card_data = (card_game_id, draft_class, score, modifier, score_version, None, None)
                                c.execute('REPLACE INTO scores VALUES(?,?,?,?,?,?,?)', card_data)
                                card_count+=1
                                
                            # Toggle is_card_name
                            is_card_name = not is_card_name            
                        
        # Discover duplicates
        dupes = set([x for x in processed if processed.count(x) > 1])
        print 'Number of cards processed for ' + draft_class + ': ' + str(card_count - len(dupes))

        if len(dupes) > 0:
            print 'Duplicates: ' + str(dupes)
       
        csv_file.close()                
    
    print ''
    c.execute('SELECT count(*) from scores')
    row = c.fetchone()
    print 'Number of cards in scores table: ' + str(row[0])
    
    try:
        db.commit()
    except sqlite3.Error as e:
        print "An error occurred: ", e.args[0]
        db.rollback()
        
    db.close()
       
# Boilerplate python
if __name__ == '__main__':
    main()
