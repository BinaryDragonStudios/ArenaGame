#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-


################################################################################
# Imports
################################################################################
import sys
import sqlite3
import uuid
import math
import collections
import time
import logging
from time import gmtime, strftime
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify, json, render_template, request
from jinja2 import Environment 
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
    return "http://highwind.tv/static/" + card_game_id + ".png"

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

def get_card_scores (draft_class, c):

    # Define query
    scores_sql = """
        SELECT card_game_id, score, modifier 
        FROM scores 
        WHERE draft_class = ?;        
    """

    # Get the scores data
    try:
        c.execute(scores_sql, (draft_class, ))
        scores = c.fetchall()
    except sqlite3.Error as error:
        app.logger.error('An error occured: ' + error)
        return render_template('error.html', error = "Something went wrong while getting scores")   

    # Buffer card scores
    card_scores = {}
    for row in scores:
        card_scores[row[0]] = row[1]     # index is card_game_id, value is score
        
    return card_scores

def get_leaderboard (duration, difficulty, c):
    # Get tom ten scores within duration
    sql_query = """
        SELECT game_id, nickname, score, game_class 
        FROM games 
        WHERE datetime(date, 'unixepoch')  > datetime('now',?) 
        AND nickname > '' 
        AND score > 0 
        AND difficulty = ?
        ORDER BY score 
        LIMIT 10;
    """

    try:
        c.execute(sql_query,  (duration, int(difficulty)))
        rows = c.fetchall()
    except sqlite3.Error as error:
        app.logger.error(error)
        return render_template('error.html', error = "Couldn't load leaderboard");

    print rows

    i = 1
    leaderboard = {}
    for row in rows:
        entry = {}
        entry['game_id']    = row[0]
        entry['nickname']   = row[1]
        entry['score']      = row[2]
        entry['game_class'] = row[3]
        leaderboard[i] = entry
        i += 1

    return leaderboard

def init_database(db):
    # create the games database if it does not exist
    query = """
    CREATE TABLE IF NOT EXISTS 
        games(
            'game_id' CHAR(50) PRIMARY KEY, 
            'class', 
            'draft_json', 
            'picks_json', 
            'time_used', 
            'score', 
            'nickname', 
            'difficulty'
        )
    """
    db.execute(query)
    db.commit()

    #Make sure all the colums are in place
    columns = ['game_id', 'class', 'draft_json', 'picks_json', 'time_used', 'score', 'nickname', 'difficulty']
    c = db.cursor()
    query  = "PRAGMA table_info(games)"
    c.execute(query)
    rows = c.fetchall()
    query = "ALTER TABLE games ADD COLUMN ?;"
    db_columns = []
    for row in rows:
        db_columns.append(row[1])

    for column in columns:
        if column not in db_columns:
            c.execute("ALTER TABLE games ADD COLUMN " + column + ";")

    # Set default values
    query = "UPDATE games SET score = 0 WHERE score IS NULL;"
    c.execute(query)
    query = "UPDATE games SET time_used = 0 WHERE time_used IS NULL;"
    c.execute(query)
    query = "UPDATE games SET nickname = '' WHERE nickname IS NULL;"
    c.execute(query)
    query = "UPDATE games SET difficulty = 5 WHERE difficulty IS NULL;"
    c.execute(query)

    db.commit()


################################################################################
# Routes
################################################################################
@app.route("/")
def index():
    return render_template('index.html', head_title = "Arena Drating Game - Welcome")


@app.route("/tutorial")
def tutorial():
    return render_template('tutorial.html', head_title = "Arena Drating Game - Tutorial")


@app.route("/draft/<int:difficulty>")
def draft(difficulty):
    # Establish db connection
    db           = sqlite3.connect('game.sqlite')
    init_database(db)

    # Buffer page output
    random_class = choice(classes)
    packs        = []
    db_packs     = {}

    # Define base query
    c            = db.cursor()
    sql          = """
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
        pick_rarity     = select_rarity(i in [1,10,20,30])
        pick_rarity_2   = pick_rarity

        if pick_rarity == "COMMON": 
            pick_rarity_2 = "FREE"

        cards = {}
        db_cards = {}
        j = 1;

        try:
            c.execute(sql, (random_class, pick_rarity, pick_rarity_2))
            rows = c.fetchall()
        except sqlite3.Error as error:
            app.logger.error(error)
            return render_template('error.html', error = "Something went wrong while creating game");   

        for row in rows:
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

        # Make a seperate list of cards with just the card ids to store in the games table
        db_packs[i] = db_cards

    # Make an unique game id
    game_id = str(uuid.uuid4())

    # JSON string of draft to store in the games table
    draft_json = json.dumps(db_packs)

    # Insert game_id and drafte into games table
    sql_insert = """
        INSERT INTO games (game_id, game_class, draft_json, date, nickname, difficulty) 
        VALUES (?, ?, ?, ?, ?, ?);
    """

    try:
        db.execute(sql_insert, (game_id, random_class, draft_json, math.floor(time.time()), '', difficulty))
    except sqlite3.Error as error:
        app.logger.error(error)
        return render_template('error.html', error = "Something went wrong while creating game");   

    db.commit();            
    db.close()

    # Pass data to the template
    return render_template("draft.html", 
        hero_class = random_class.title(), 
        hero = get_url(random_class),
        game_id = game_id, 
        draft=packs,
        difficulty=difficulty,
        head_title = "Arena Drating Game - " + str(difficulty) + " seconds")


@app.route("/draftdone", methods=['POST'])
def draftdone():
    # Buffer data from POST
    data = request.form

    # Establish db connection
    db = sqlite3.connect('game.sqlite')
    c = db.cursor()

    # Get the picks JSON and make keys integer
    picks = {int(k):v for k,v in json.loads(data['picks']).items()}

    # ...and loop through then to make a dict with the turn number as index
    picks_dict = {}
    for pick in picks:
        turn             = int(picks[pick]['pick-number'])
        card_id          = picks[pick]['card-id']
        picks_dict[turn] = card_id

    # Get the draft JSON
    sql_draft = """
        SELECT draft_json, game_class, difficulty 
        FROM games 
        WHERE game_id = ?;        
    """
    try:
        c.execute(sql_draft, (data['game_id'], ))
        row = c.fetchone()
    except sqlite3.Error as error:
        app.logger.error(error)
        return render_template('error.html', error = "Something went wrong while getting game")

    # cast the keys in the draft to int, then sort the dictionary
    draft_unsorted  = {int(k):v for k,v in json.loads(row[0]).items()}
    draft           = collections.OrderedDict(sorted(draft_unsorted.items()))

    # Buffer the class and difficulty
    draft_class     = row[1]
    difficulty      = row[2]

    # Update pick counter in the scores table
    sql_update_pick_counter = """
        UPDATE scores 
        SET pick_counter = (SELECT pick_counter + 1) 
        WHERE card_game_id = ? 
        AND draft_class = ?;
        """

    # Update offer counter in the scores table
    sql_update_offer_counter = """
        UPDATE scores 
        SET offer_counter = (SELECT offer_counter + 1) 
        WHERE card_game_id = ? 
        AND draft_class = ?;
        """

    # Get the scores for the cards
    card_scores     = get_card_scores(draft_class, c)

    # Compute user score
    max_score         = 0
    pick_score        = 0
    missed_pick_score = 0
    total_penalty     = 0
    diff_penalty      = difficulty * 3
    
    for turn in draft:
        card_score_list = []
        card_picked = picks_dict[turn]
        pick_penalty = 0;
        
        # Make a list of the card scores
        for choice in draft[turn]:
            # make a list of the 3 scores from the pack oddered
            card = str(draft[turn][choice])
            card_score_list.append(int(card_scores[card]))
            
            # Update scores table offer counter
            c.execute(sql_update_offer_counter, (card, draft_class))

        # ...then get the highest and lowest score in the list
        best_card_score  = max(card_score_list)
        worst_card_score = min(card_score_list)

        # Test if user picked a card and add the value to the total scores
        if card_picked:
            # Calculate the penalty for picking that card
            pick_penalty = best_card_score - int(card_scores[card_picked])

            # If the score is > 0, add difficulty penalty
            if pick_penalty > 0:
                pick_penalty += diff_penalty
                
            total_penalty += pick_penalty
            
            # Update scores table pick counter
            c.execute(sql_update_pick_counter, (card_picked, draft_class))
            
        # If user neglected to pick a card, the penalty is severe
        else:
            missed_pick_score  += (( best_card_score - worst_card_score + diff_penalty) * 2)

    # Commit the updates to scores table
    try: 
        db.commit()
    except sqlite3.Error as error:
        app.logger.error(error)
        return render_template('error.html', error = "Something went wrong while updating some statistics")

    # Draft score is set to best possible score minus what the user drafted
    draft_score =  total_penalty + missed_pick_score

    # The users total score is the draft score + time used.
    seconds     = round(float(data['time_used']) / 1000, 2)
    user_score  = draft_score + seconds

    # If difficulty is less than 61 seconds, update the games table with the selected cards, time used, score and date
    if difficulty < 61:
        sql_update = """
            UPDATE games 
            SET picks_json = ?, time_used = ?, score = ? 
            WHERE game_id = ?;
        """
        try:
            c.execute(sql_update, (json.dumps(picks_dict), seconds, user_score, data['game_id']))
            db.commit()
        except sqlite3.Error as error:
            app.logger.error(error)
            return render_template('error.html', error = "Something went wrong while saving game")

    made_leaderboards   = "False"

    # if difficulty is 15 or less check if user earned a spot on the leaderboards
    if difficulty < 16:
        duration            = 'start of day';
        leaderboards_day    = get_leaderboard(duration, difficulty, c)

        #If there are less the 10 entries in the leaderboeard from today, the user made it
        if len(leaderboards_day) < 10:
            made_leaderboards = "True"
        # Or, if user's score is less than the highest score, the user made it
        elif user_score < leaderboards_day[10]['score']:
            made_leaderboards = "True"

    db.close()

    # Return the game id to front-end
    return made_leaderboards


@app.route("/nickname", methods=['POST'])
def nickname():
    # Buffer data from POST
    data = request.form
    game_id = data['game_id']
    nickname = data['nickname'].strip()

    if len(nickname) > 20:
        response = "Nickname too long"
    elif len(nickname) < 4:
        response = "Nickname too short"
    else:
        response = "OK"
        # Establish db connection
        db = sqlite3.connect('game.sqlite')
        sql_update_game = """
            UPDATE games 
            SET nickname = ?
            WHERE game_id = ?;
        """
        try: 
            db.execute(sql_update_game, (nickname, game_id))
            db.commit()
        except sqlite3.Error as error:
            app.logger.error(error)
            return render_template('error.html', error = "Something went wrong when saving nickname");   

        db.close()

    return response


@app.route("/result/<game_id>", methods=['POST', 'GET'])
def result(game_id):
    # Establish db connection
    db = sqlite3.connect('game.sqlite')
    db.text_factory = str
    c = db.cursor()
    
    # Database query to get game data
    game_sql = """
        SELECT draft_json, picks_json, game_class, score, time_used, nickname, difficulty
        FROM games 
        WHERE game_id = ?;
    """
    
    # Get the game data
    try:
        c.execute(game_sql, (game_id, ))
        row = c.fetchone()
        
    # Log if errors
    except sqlite3.Error as error:
        app.logger.error(error)
        return render_template('error.html', error = "No such game");
    
    # Check if game exists
    
    if(row == None):
        app.logger.debug('Trying to load non-exsisting game ( %s )' % str(game_id))
        return render_template('error.html', error = "No such game");
        
    # Declear dicts and vars
    game                = {}

    # Buffer game data
    draft               = {int(k):v for k,v in json.loads(row[0]).items()} # Making the indexes integer for sorting purposes
    picks               = {int(k):v for k,v in json.loads(row[1]).items()} # -
    game['hero_class']  = row[2]
    game['user_score']  = row[3]
    game['time_used']   = row[4]
    if(row[5] > ''):
        game['nickname']= row[5].decode('utf-8')
    else:
        game['nickname']= ''
    game['difficulty']  = row[6]
    game['picks']       = json.dumps(picks)
    game['draft']       = collections.OrderedDict(sorted(draft.items()))
    game['card_scores'] = get_card_scores(game['hero_class'], c)
    game['draft_json']  = json.dumps(game['draft'])
    game['scores_json'] = json.dumps(game['card_scores'])
    hero                = get_url(game['hero_class'])
    
    # Close database connection
    db.close()

    # Pass data to template
    return render_template('result.html', 
        error   = str(False), 
        game    = game,  
        hero    = hero, 
        head_title = "Arena Drating Game - Result"
    )


@app.route("/leaderboards/<difficulty>")
def leaderboards(difficulty):
    # Establish db connection
    db = sqlite3.connect('game.sqlite')
    db.text_factory = str
    c = db.cursor()
        
    # Get top ten scores within last day
    duration_day = 'start of day';
    leaderboard_day = get_leaderboard(duration_day, difficulty, c)

    # Get top ten scores within last 7 days
    duration_week = '-7 days';
    leaderboard_week = get_leaderboard(duration_week, difficulty, c)
            
    # Get top ten scores within last 30 days
    duration_month = '-30 days';
    leaderboard_month = get_leaderboard(duration_month, difficulty, c)
            
    # Get top ten scores from all time
    duration_alltime = '-100 years';
    leaderboard_alltime = get_leaderboard(duration_alltime, difficulty, c)
    
    # Close the database connection
    db.close()
    
    # Pass the scores to the template
    return render_template('leaderboards.html', 
        leaderboard_day     = json.dumps(leaderboard_day), 
        leaderboard_week    = json.dumps(leaderboard_week), 
        leaderboard_month   = json.dumps(leaderboard_month),
        difficulty          = difficulty, 
        head_title = "Arena Drating Game - Leaderboards (" + str(difficulty) + " seconds)"
    )


@app.route("/shoutouts")
def shoutouts():
    return render_template('shoutouts.html', head_title = "Arena Drating Game - Shoutouts")


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


@app.route("/set")
def set():
    db = sqlite3.connect('game.sqlite')
    c = db.cursor()
    sql = """
        SELECT card_game_id, card_name_en  
        FROM cards 
        ORDER BY card_name_en
    """
    output = "<h1>Current Set</h1>"
    for row in c.execute(sql):
        output += '<img src="' + card_image_url('cards/' + row[0])  + '"title="' + row[1]  + '">'
    return output


################################################################################
# Start if __main__
################################################################################
if __name__ == "__main__":

    flask_port = 5000
    flask_host = "127.0.0.1"

    # Set up logging
    
    fh = logging.handlers.RotatingFileHandler('game.log', mode='a', maxBytes=10000, backupCount=1)    
    fh.setLevel(logging.DEBUG)    
    logging.Formatter.converter = time.gmtime
    formatter = logging.Formatter("%(asctime)s %(pathname)s: %(lineno)d, %(funcName)s, %(levelname)s \n %(message)s \n", "%d.%m.%y %H:%M:%S")
    fh.setFormatter(formatter)
    
    app.logger.addHandler(fh)
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