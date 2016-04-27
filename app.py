#!/usr/bin/env python2.7

################################################################################
# Imports
################################################################################
import sys
import sqlite3
import uuid
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify, json, render_template, request
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
    return "http://hs.jwd.me/static/" + card_game_id + ".png"

def select_rarity(rare_gauranteed):
    roll = randint(1,100)
    if (roll == 100): return "LEGENDARY"
    if (roll >= 95): return "EPIC"
    if (roll >= 85 or rare_gauranteed == True): return "RARE"
    return "COMMON"

def get_url(hero):
    card_game_id = 'HERO_'
    x_offset = -115
    y_offset = -85
    
    if hero == 'warrior':
        index = '01'
        x_offset -= 2
    elif hero == 'shaman':
        index = '02'
        x_offset -= 15
    elif hero == 'rogue':
        index = '03'
        y_offset -= 5
    elif hero == 'paladin':
        index = '04'
        x_offset -= 5
        y_offset += 7
    elif hero == 'hunter':
        index = '05'
        y_offset += 5
    elif hero == 'druid':
        index = '06'
        x_offset -= 13
        y_offset -= 5
    elif hero == 'warlock':
        index = '07'
        x_offset += 2
    elif hero == 'mage':
        index = '08'
    elif hero == 'priest':
        index = '09'
        x_offset += 8;
    
    return {'url': card_image_url(card_game_id + index), 'x-offset': x_offset, 'y-offset': y_offset}

def store_draft(draft, hero_class, db):
    game_id = str(uuid.uuid4())
    draft_json = json.dumps(draft)
    sql = "INSERT INTO games (game_id, game_class, draft_json) VALUES (?, ?, ?);";
    db.execute(sql, (game_id, hero_class, draft_json))

    sql = "UPDATE scores SET offer_counter = (SELECT offer_counter + 1) WHERE card_game_id = ? AND draft_class = ?;"
    for pack in draft:
        for card in draft[pack]:
            db.execute(sql, (draft[pack][card],hero_class))
    db.commit();
    return game_id
    
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
        output += '<img src="' + card_image_url('cards/' + row[0])  + '"title="' + row[1]  + '">'
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
    db_packs = {}

    # Define base query
    sql  = """
SELECT 
    cards.card_game_id,
    cards.card_name_en,
    cards.cost,
    cards.class,
    cards.rarity,
    scores.score
FROM 
    cards, scores
WHERE 
    scores.card_game_id = cards.card_game_id AND 
    scores.draft_class = ? AND 
    (cards.rarity = ? OR cards.rarity = ?)
ORDER BY 
    RANDOM()
LIMIT 3
"""
    # Draft 30 sets of 3 cards
    for i in range(1,31):
        pick_rarity = select_rarity(i in [1,10,20,30])
        rarity_2 = pick_rarity
        if pick_rarity == "COMMON": rarity_2 = "FREE"
        cards = {}
        db_cards = {}
        j = 1;
        for row in c.execute(sql, [random_class, pick_rarity, rarity_2]):
            card  = {}
            card['card-id']     = row[0]
            card['card-name']   = row[1]
            card['card-cost']   = row[2]
            card['card-class']  = row[3]
            card['card-rarity'] = row[4]
            card['card-score']  = row[5]
            db_cards[j]         = row[0] # card-id
            cards[j]            = card
            j += 1
        packs.append(cards)
        db_packs[i] = db_cards
    game_id = store_draft(db_packs, random_class, db)
    return render_template("draft.html", 
        head_title ='Draft Game', 
        hero_class=random_class.title(), 
        hero_url=hero['url'], 
        x_offset=hero['x-offset'], 
        y_offset=hero['y-offset'], 
        game_id=game_id, 
        draft=packs)

@app.route("/draftdone", methods=['POST'])
def draftdone():
    # Establish db connection
    db = sqlite3.connect('game.sqlite')
    data = request.form
    picks = json.loads(data['picks'])

    array_picks = {}
    for pick in picks:
        pick_number = picks[pick]['pick-number']
        card_id     = picks[pick]['card-id']
        array_picks[int(pick_number)] = card_id
        sql = "UPDATE scores SET pick_counter = (SELECT pick_counter + 1) WHERE card_game_id = ? AND draft_class = ?;"
        db.execute(sql, (card_id, data['draft_class'].lower()))
     
    sql = "UPDATE games SET picks_json = ?, time_used = ? WHERE game_id = ?;"
    db.execute(sql, (json.dumps(array_picks), data['time_used'], data['game_id']))
    db.commit()
    return data['game_id']
        
@app.route("/result/<game_id>")
def result(game_id):
    game  = {}
    score = 0
    db = sqlite3.connect('game.sqlite')
    db.text_factory = str
    c = db.cursor()
    game_sql = """
        SELECT game_class, draft_json, picks_json, time_used 
        FROM games 
        WHERE game_id = ?;
    """
    app.logger.info(game_id)
    try:
        c.execute(game_sql, (game_id.strip(), ))
        row = c.fetchone()
    except sqlite3.Error as error:
        app.logger.error(error)
        return render_template('result.html', error = "No such game");
        
    game['class']       = row[0]
    game['draft']       = row[1]
    game['picks']       = row[2]
    game['time_used']   = row[3]           

    scores_sql = "SELECT card_game_id, score, modifier FROM scores WHERE draft_class = ?"
    
    try:
        c.execute(scores_sql, (game['class'], ))
        scores = c.fetchall()
    except sqlite3.Error as error:
        app.logger.error('An error occured: ' + error)
        return render_template('result.html', error = "Something went wrong");   
    
    db.commit()
    app.logger.info(scores)
    return render_template('result.html', error = False, draft = game['draft'], picks = game['picks'], scores = scores, time_used = game['time_used'], user_score = score)
        
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
        card_images += '<img src="' + card_image_url('cards/' + row[0])  + '"title="' + row[1]  + ': ' + row[4]  + '">'
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

    # Set up logging
    formatter = logging.Formatter("%(asctime)s | %(pathname)s:%(lineno)d | %(funcName)s | %(levelname)s | %(message)s ")
    handler = RotatingFileHandler('game.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.DEBUG)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.DEBUG)

    # Check if debug mode was specified
    if "--debug" in sys.argv:
        print "Starting in debug mode."
        app.debug = True
    # Run public & directly on port 80 with no proxy/middleware
    if "--direct" in sys.argv:
        flask_port = 8080       # Listen on port 80
        flask_host = "0.0.0.0"  # Listen on all IPs

    # Start the server on default port (5000)
    app.run(host = flask_host, port = flask_port)

