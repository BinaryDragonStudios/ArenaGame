#!/usr/bin/env python2.7

################################################################################
# Imports
################################################################################
import sys
import sqlite3
from flask import Flask, jsonify, render_template
from random import randint, choice

################################################################################
# Objects
################################################################################
app = Flask(__name__)

################################################################################
# Global Variables
################################################################################
classes = [
    'druid',
    'hunter',
    'mage',
    'paladin',
    'priest',
    'rogue',
    'shaman',
    'warrior',
    'warlock'
]

################################################################################
# Helper Functions
################################################################################
def card_image_url(card_game_id):
    return "http://wow.zamimg.com/images/hearthstone/cards/enus/original/" + card_game_id + ".png"

def select_rarity(rare_gauranteed):
    roll = randint(1,100)
    if (roll == 100): return "LEGENDARY"
    if (roll >= 95): return "EPIC"
    if (roll >= 85 or rare_gauranteed == True): return "RARE"
    return "COMMON"

def get_url(hero):
    url = 'http://wow.zamimg.com/images/hearthstone/cards/enus/original/HERO_'
    x_offset = 0
    y_offset = 0
    if hero == 'warrior':
        index = '01'
        x_offset = -2
    elif hero == 'shaman':
        index = '02'
        x_offset = -15
    elif hero == 'rogue':
        index = '03'
        y_offset = -5
    elif hero == 'paladin':
        index = '04'
        x_offset = -5
        y_offset = 7
    elif hero == 'hunter':
        index = '05'
        y_offset = 5
    elif hero == 'druid':
        index = '06'
        x_offset = -13
        y_offset = -5
    elif hero == 'warlock':
        index = '07'
        x_offset = 2
    elif hero == 'mage':
        index = '08'
    elif hero == 'priest':
        index = '09'
        x_offset = 8;
    
    return [url+index+'.png', x_offset, y_offset]
        
################################################################################
# Routes
################################################################################
@app.route("/")
def hello():
    return render_template('index.html')

@app.route("/set")
def set():
    db = sqlite3.connect('game.sqlite')
    c = db.cursor()
    sql = "SELECT card_game_id, card_name_en  FROM cards ORDER BY card_name_en"
    output = "<h1>Current Set</h1>"
    for row in c.execute(sql):
        output += '<img src="' + card_image_url(row[0])  + '"title="' + row[1]  + '">'
    return output

@app.route("/draft")
def draft():
    # Establish db connection
    db = sqlite3.connect('game.sqlite')
    c = db.cursor()

    # Buffer page output
    random_class = choice(classes)
    hero = get_url(random_class)
    packs = []

    # Define base query
    sql  = """
        SELECT scores.card_game_id
        FROM cards, scores
        WHERE scores.card_game_id = cards.card_game_id
        AND scores.draft_class = ?
        AND ((cards.rarity = ?) OR (cards.rarity = ?))
        ORDER BY RANDOM()
        LIMIT 3
    """
    # Draft 30 sets of 3 cards
    for i in range(1,31):
        pick_rarity = select_rarity(i in [1,10,20,30])
        rarity_2 = pick_rarity
        if pick_rarity == "COMMON": rarity_2 = "FREE"
        cards = []
        for row in c.execute(sql, [random_class, pick_rarity, rarity_2]):
            cards.append(row[0])
        packs.append(cards)
    return render_template("draft.html", head_title ='Draft Game', hero_class=random_class.title(), hero_url=hero[0], x_offset=hero[1], y_offset=hero[2], draft=packs)

@app.route("/leaderboards")
def leaderboards():
    return render_template('leaderboards.html')


@app.route("/classrank/<class_lookup>")
def classrank(class_lookup):
    db = sqlite3.connect('game.sqlite')
    c = db.cursor()
    # Check if class_lookup provided is valid
    if class_lookup not in classes:
        return "Invalid class specified"

    sql = """
SELECT 
    cards.card_game_id,
    cards.card_name_en,
    cards.rarity,
    scores.draft_class,
    scores.score
FROM
    cards,
    scores
WHERE
    draft_class = ? AND
    cards.card_game_id = scores.card_game_id
ORDER BY
    cast(scores.score as integer) DESC;
"""

    class_power = 0
    card_images = ""
    card_count = 0
    for row in c.execute(sql, [class_lookup, ]):
        card_images += '<img src="' + card_image_url(row[0])  + '"title="' + row[1]  + ': ' + row[4]  + '">'
        class_power += int(row[4])
        card_count += 1

    output = "<h1>Card Rankings for: " + class_lookup + "</h1>"
    output += "<h2>Cards: " + str(card_count) + "</h2>"
    output += "<h2>Sum Value: " + str(class_power)  + "</h2>"
    output += "<h2>Mouse over for score</h2>"

    return output + card_images

# Dump JSON data
@app.route('/data')
def names():
    data = {"names": ["John", "Jacob", "Julie", "Jennifer"]}
    return jsonify(data)

################################################################################
# Start if __main__
################################################################################
if __name__ == "__main__":

    flask_port = 5000
    flask_host = "127.0.0.1"

    # Check if debug mode was specified
    if "--debug" in sys.argv:
        print "Starting in debug mode."
        app.debug = True
    # Run public & directly on port 80 with no proxy/middleware
    if "--direct" in sys.argv:
        flask_port = 80         # Listen on port 80
        flask_host = "0.0.0.0"  # Listen on all IPs

    # Start the server on default port (5000)
    app.run(host = flask_host, port = flask_port)


