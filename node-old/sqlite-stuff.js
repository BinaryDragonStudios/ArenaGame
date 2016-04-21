var sqlite3 = require('sqlite3').verbose(); 
var db = new sqlite3.Database('game.sqlite');

db.all("SELECT card_game_id FROM cards", function(err, rows) {
        rows.forEach(function (row) {
            console.log(row.card_game_id);
        })
    });
db.close();
