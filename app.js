// basic script to check and see if express & swig are working

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

app.get('/query', function(req, res) {
    var output = "<table>";
    db.serialize(function() {
        db.each("SELECT card_game_id, card_name_en  FROM cards", function(err, row) {
            output = output + "<tr><td>" + row.card_game_id + "<td>" + row.card_name_en;
        }, function() {
            res.send(output);
        })
    })
})

app.listen(80)
debug_notice('app started on localhost:80')
