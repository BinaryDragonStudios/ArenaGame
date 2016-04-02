// basic script to check and see if express & swig are working

var express = require('express')
var app = express()
var swig = require('swig') 

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
 
app.listen(80)
debug_notice('app started on localhost:80')
