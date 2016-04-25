#!/usr/bin/env python

import sqlite3

def main():
    
    # Connect to our database and create scores table if it doesn't exist
    db = sqlite3.connect('game.sqlite')
    db.text_factory = str
    c = db.cursor()
    query = "CREATE TABLE IF NOT EXISTS scores('card_game_id', 'draft_class', 'score', 'modifier', 'score_version','pick_counter','offer_counter', UNIQUE(card_game_id,draft_class))"
    c.execute(query)
    
    score_version = '20150703' # Maybe make this a parameter?
    class_list = ['druid', 'hunter', 'mage', 'paladin', 'priest', 'rogue', 'shaman', 'warlock', 'warrior']
    
    for draft_class in class_list:
    
        # Open CSV file
        csv_file = open('scores/' + draft_class + '.csv', 'rb')
        
        with csv_file:
            # Boolean keeping track of the value (card name or score); first value is always card name
            is_card_name = True
            
            # Keep track of the cards processed (by card_game_id) and cards not found (by name)
            processed = []
            cards_not_found = []
            
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
                                c.execute('SELECT card_game_id FROM cards WHERE card_name_en = ? LIMIT 1', (value,))
                                row = c.fetchone()
                                
                                # If the card name is mistyped in the score data, we need to handle it
                                if row is None:
                                    cards_not_found.append(value)
                                    card_game_id = 'not_found'
                                else:  
                                    card_game_id = row[0]                        
                                
                                processed.append(card_game_id)
                                  
                            # If the value is not the card name, it's the associated score
                            else:
                            
                                # The score may have a modifier, indicated by a *, we store them seperatly
                                modifier = value.count('*')
                                score = value.strip('\*')
                                
                                # Now that we have all available card data, insert them into the database
                                card_data = (card_game_id, draft_class, score, modifier, score_version, 0, 0)
                                c.execute('REPLACE INTO scores VALUES(?,?,?,?,?,?,?)', card_data)
                                
                            # Toggle is_card_name
                            is_card_name = not is_card_name            
                        
        # Discover duplicates
        dupes = set([x for x in processed if processed.count(x) > 1])
        
        # Print output
        print ''
        print draft_class.upper()
        print 'Cards processed: ' + str(len(processed) - len(dupes) - len(cards_not_found))

        # If we have duplicate entries, get the card name(s) from the cards table and print them
        if len(dupes) > 0:
            values = ','.join(dupes)
            c.execute("SELECT card_name_en from cards WHERE card_game_id IN (?)", (values,))
            print 'Duplicates     : ' + ', '.join([r[0] for r in c.fetchall()])
        
        # If we have misspelled cards in out data print them
        if len(cards_not_found) > 0:
            print 'Not found      : ' + ', '.join(cards_not_found)
            
        csv_file.close()                
    
    print ''
    
    # Delete cards that are misspelled and thus not connected to card table
    c.execute("DELETE from scores WHERE card_game_id = 'not_found'")
    c.execute("VACUUM")
    
    # Print number of scores recorded in table
    c.execute("SELECT count(*) from scores")
    row = c.fetchone()
    print 'Number of cards in scores table: ' + str(row[0])
    
    # Commit database executes
    try:
        db.commit()
    except sqlite3.Error as e:
        print "An error occurred: ", e.args[0]
        db.rollback()
        
    db.close()
       
# Boilerplate python
if __name__ == '__main__':
    main()
