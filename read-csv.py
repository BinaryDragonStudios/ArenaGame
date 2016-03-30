#!/usr/bin/env python

def main():

    # Open CSV file
    csv_file = open('/root/code/mage.csv', 'rb')
    
    with csv_file:
        #list of cards and their scores (alternating)
        score_list = []
        
        for line in csv_file:
            # all rows with relevant data starts with ; or  -
            if line[0] in [';','-']:
                for content in line.split(';'):
                    #leave out content that's not a card or a score
                    if content not in ['', '---lower half---', '---upper half---', '(empty)']:
                        score_list.append(content)
                        
        print score_list
        csv_file.close()
        
        #boolean keeping track of the value (card name or score); first is always card name
        card_score = false
        
        #this is an extra loop for clarity, the logic should probably be moved up to the other one (drop score_list)
        for value in score_list:
            if not card_score:
                print 'Card name: ' + value
            else:
                asterisks = value.count('*')
                value.strip('*')
                print 'Card score: ' + value
                
                if asterisks != 0:
                    print 'Score modifier:' + ('*' * asterisks)

                print ''

            #toggle card_score
            card_score = not card_score            
        
# Boilerplate python
if __name__ == '__main__':
    main()