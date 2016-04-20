// required libs

var sqlite3 = require('sqlite3').verbose(),
    express = require('express'),
    swig = require('swig'),
    async = require('async');

// main objects

var db = new sqlite3.Database('game.sqlite'),
    app = express();

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
        if (roll > 0.99) return "LEGENDARY"
        if (roll > 0.955) return "EPIC"
        return "RARE"
    } else {
        if (roll > 0.99) return "LEGENDARY"
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
    var draft_class = "priest"
    var output = "<h1>draft pick rarity</h1><ol>"
    var j = 0;
    res.writeHead(200, "OK", {'Content-Type': 'text/html'});
    res.write('<html><head><title>Hello Noder!</title></head><body>');

    async.waterfall([
        function(callback) {
            var rarities = [];
            for(i=1;i<=30;i++) {
                not_common = false;
                if([1, 10, 20, 30].indexOf(i) > -1) {
                    not_common = true;
                }
                rarities.push(pick_rarity(not_common));
            }
            callback(null, rarities);
        },
        function(rarities, callback) {
            draftpicks = [];
            async.forEachOf(rarities, function(value, key, callback) {
                var pack = [],
                    free = '';

                // If rarity is COMMON, we also haveot pick from cards that are FREE
                if(value == 'COMMON') {
                    free = ' OR cards.rarity = "FREE"';
                }
                query = 'SELECT scores.card_game_id '
                      + 'FROM cards, scores '
                      + 'WHERE scores.card_game_id = cards.card_game_id '
                      + 'AND scores.draft_class = ? '
                      + 'AND (cards.rarity = ?' + free + ') '
                      + 'ORDER BY RANDOM() '
                      + 'LIMIT 3;';

                async.waterfall([ 
                    function(callback) {
                        db.each(query, [draft_class, value], function(err, row) {
                            if (row.card_game_id == '') {
                                console.log('Empty: ' + row.card_game_id);
                                process.exit(1);
                            }
                            if (!err) {
                                pack.push(row.card_game_id);
                            } else {
                                console.log('error: ' + err.message);
                            }
                        }, function() {
                            callback(null, pack);
                        })
                    },
                    function(pack, callback) {
                        draftpicks.push(pack); 
                        callback(null, draftpicks);
                    }
                ], function(err, draftpicks) {
                   if(err)
                   {
                       console.log(err.message);
                   }
                   callback(null, draftpicks);
                })
            }, function(){
                callback(null,draftpicks,rarities);
            });
        },
        function(draftpicks, rarities, callback) {
            async.forEachOf(draftpicks, function(values, key, callback) {
                values.forEach(function(val, key, callback) {
                    res.write('<img src="' + card_image_url(val)  + '" />');
                });
                res.write('<br />');
            });
            callback(null, rarities);
        },
        function(rarities) {
            var counts = {}
            rarities.forEach(function (x) { counts[x] = (counts[x] || 0) +1})
            res.write('<h1>counts</h1><ul>');
            res.write("<li>Commons: " + (counts['COMMON'] || 0));
            res.write("<li>Rares: " + (counts['RARE'] || 0));
            res.write("<li>Epics: " + (counts['EPIC'] || 0));
            res.write("<li>Legendaries: " + (counts['LEGENDARY'] || 0));
        }
    ]);
});

app.listen(80)
debug_notice('app started on localhost:80')
