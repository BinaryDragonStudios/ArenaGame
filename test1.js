// basic script to check and see if express is working

var express = require('express')
var app = express()
 

function debug_notice(message){
  console.log('NOTICE ' + message);

}

app.get('/', function (req, res) {
  debug_notice('request: /')
  res.send('Hello World')
})
 
app.listen(80)
