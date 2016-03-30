#!/usr/bin/env python

import sys

def main():
    
    card_class = 'mage'
    
    # Open CSV file
    csv_file = open('/root/code/' + card_class + '.csv', 'rb')
    
    with csv_file:
        # List of cards and their scores (alternating)
        score_list = []
        
        for line in csv_file:
            # All rows with relevant data starts with ; or  -
            if line[0] in [';','-']:
                for content in line.split(';'):
                    content = content.strip()
                    # Leave out content that's not a card or a score
                    if content not in ['', '---lower half---', '---upper half---', '(empty)']:
                        score_list.append(content)
                        
        csv_file.close()
        
        # Boolean keeping track of the value (card name or score); first is always card name
        is_card_name = True
        # Card counter
        card_count = 0
        
        # This is an extra loop for clarity, the logic should probably be moved up to the other one
        for value in score_list:
            if is_card_name:
                print 'Card name: ' + value
                card_count+=1
            else:
                modifier = value.count('*')
                print 'Card score: ' + value.strip('\*')
                print 'Modifier: ' + str(modifier)
                print ''

            # Toggle is_card_name
            is_card_name = not is_card_name            
        
        print 'Number of cards processed: ' + str(card_count)
        
# Boilerplate python
if __name__ == '__main__':
    main()
