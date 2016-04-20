#!/usr/bin/env python2.7

################################################################################
# Imports
################################################################################
import sys
import sqlite3
from flask import Flask, jsonify

################################################################################
# Objects
################################################################################
app = Flask(__name__)

################################################################################
# Helper Functions
################################################################################
def card_image_url(card_game_id):
    return "http://wow.zamimg.com/images/hearthstone/cards/enus/original/" + card_game_id + ".png"

################################################################################
# Routes
################################################################################
@app.route("/")
def hello():
    output = "<h1>Arena Game</h1>"
    output += "<ul><li>Draft Sim</li><li>Current Card Set</li></ul>"
    return output

@app.route("/set")
def set():
    db = sqlite3.connect('game.sqlite')
    c = db.cursor()
    sql = "SELECT card_game_id, card_name_en  FROM cards ORDER BY card_name_en"
    output = "<h1>Current Set</h1>"
    for row in c.execute(sql):
        output += '<img src="' + card_image_url(row[0])  + '"title="' + row[1]  + '">'
    return output

@app.route("/classrank/<class_lookup>")
def classrank(class_lookup):
    db = sqlite3.connect('game.sqlite')
    c = db.cursor()

    # define acceptable classes
    classes = [
        'druid',
        'mage',
        'paladin',
        'priest',
        'rogue',
        'shaman',
        'warrior',
        'warlock'
    ]

    # Check if class_lookup provided is valid
    if class_lookup not in classes:
        return "Invalid class specified"

    output = "<h1>Card Rankings for: " + class_lookup + "</h1><h2>Mouse over for score</h2>"
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

    for row in c.execute(sql, [class_lookup, ]):
        output += '<img src="' + card_image_url(row[0])  + '"title="' + row[1]  + ': ' + row[4]  + '">'

    return output 

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


