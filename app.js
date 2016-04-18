// required libs

var sqlite3 = require('sqlite3').verbose()
var express = require('express')
var swig = require('swig')

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
        if (roll > 0.9) return "LEGEND"
        if (roll > 0.6) return "EPIC"
        return "RARE"
    } else {
        if (roll > 0.9) return "LEGEND"
        if (roll > 0.75) return "EPIC"
        if (roll > 0.55) return "RARE"
        return "COMMON"
    }
}


app.get('/', function (req, res) {
    debug_notice('request: /')
    res.send('Hello World')
})

app.get('/new', function (req, res) {
    debug_notice('request: /new')
    language = {
        head_title: 'Title Test',
        h1_title: 'h1 test'
    }
    res.render(
        'basic.html',
        language
    )
})

app.get('/set', function(req, res) {
    debug_notice("request: /set")
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
    debug_notice("request: /draft")
    output = "pick rarity<ol>"
    for(i=1;i<=30;i++) {
        // picks 1, 10, 20 and 30 are gauranteed to be rare, epic or legendary
        not_common = false;
        if([1, 10, 20, 30].indexOf(i) > -1) {
            not_common = true;
        }
        output = output + "<li>" + pick_rarity(not_common)
    }
    res.send(output)
})

app.listen(80)
debug_notice('app started on localhost:80')
