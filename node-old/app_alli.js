// required libs

var sqlite3 = require('sqlite3').verbose()
var express = require('express')
var swig = require('swig')
var asynk = require('async')
var fs = require('fs')

// main objects

var db = new sqlite3.Database('game.sqlite')
var app = express()

app.engine('html', swig.renderFile)
app.set('view engine', 'html')
app.set('views', __dirname + '/views')
app.set('view cache', false);
swig.setDefaults({ cache: false });


function debug_notice(message){
    console.log('NOTICE ' + message)
}

function card_image_url(card_game_id) {
    return "http://wow.zamimg.com/images/hearthstone/cards/enus/original/" + card_game_id + ".png";
}

function pick_rarity(gauranteed_not_common) {
    roll = Math.random()
    if(gauranteed_not_common) {
        if (roll > 0.99) return "LEGEND"
        if (roll > 0.955) return "EPIC"
        return "RARE"
    } else {
        if (roll > 0.99) return "LEGEND"
        if (roll > 0.955) return "EPIC"
        if (roll > 0.8) return "RARE"
        return "COMMON"
    }
}

app.get('/', function (req, res) {
    debug_notice('get: /')
    res.render('index.html')
})

app.get('/new', function (req, res) {
    debug_notice('get: /new')
    language = {
        head_title: 'Title Test',
        h1_title: 'h1 test'
    }
    res.render(
        'basic.html',
        language
    )
})

app.get('/about', function (req, res) {
    debug_notice('get: /about')
    res.send('developed by allikin75 &amp; jared0x90')
})

app.get('/set', function(req, res) {
    debug_notice("get: /set")
    output = "<title>Current Working Set</title><h1>Current Working Set</h1>"
    db.serialize(function() {
        db.each("SELECT card_game_id, card_name_en  FROM cards ORDER BY card_name_en", function(err, row) {
            output = output + '<img src="' + card_image_url(row.card_game_id)  + '">';
        }, function() {
            res.send(output);
        })
    })
})

app.get('/draft', function(req, res) {
    debug_notice("get: /draft")
    var draft_class = "mage"
    var output = "<h1>draft pick rarity</h1>"
    var rarities = []
    
    for(i=1;i<=30;i++) {
        db.serialize(function() {
            // picks 1, 10, 20 and 30 are gauranteed to be rare, epic or legendary
            not_common = false;
            if([1, 10, 20, 30].indexOf(i) > -1) {
                not_common = true;
            }
            card_rarity = pick_rarity(not_common)
        }, function() {
            query = 'SELECT scores.card_game_id FROM cards, scores WHERE scores.draft_class = "' + draft_class + '" AND (cards.rarity = "' + card_rarity + '"';
            // If rarity is COMMON, we also haveot pick from cards that are FREE
            if(card_rarity == 'COMMON') {
                query += ' OR cards.rarity = "FREE"'
            }
            query += ') ORDER BY RANDOM() LIMIT 3;'
            j = 0;
            db.each(query, function(err, row) {
                if (!err) {
                    output[i][j] = '<img src="' + card_image_url(row.card_game_id)  + '" />';
                    j += 1;
                }
            })
        }, function() {
            rarities.push(card_rarity)
        })
    }
    var counts = {}
    rarities.forEach(function (x) { counts[x] = (counts[x] || 0) +1})
    output += "<h1>counts</h1><ul>"
    output += "<li>Commons: " + (counts['COMMON'] || 0)
    output += "<li>Rares: " + (counts['RARE'] || 0)
    output += "<li>Epics: " + (counts['EPIC'] || 0)
    output += "<li>Legends: " + (counts['LEGEND'] || 0)
    output += "</ul>"
    res.write(output)
})

app.listen(80)
debug_notice('app started on localhost:80')
