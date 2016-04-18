to do

make function / query to pick 3 cards given a rarity & class
have draft fucntion call this 30 times and build a draft
render this set of picks to the user

---------------------------

fixed nodejs/npm install.
sqlite3 isntalled properly
alli's node sqlite app worked

made set export 			
http://hs.jwd.me/set

made draft rarity generator
http://hs.jwd.me/draft

useful query

select
	cards.card_name_en, 
	cards.rarity, 
	scores.draft_class, 
	scores.score 
from 
	cards, 
	scores
where 
	draft_class = 'hunter' and 
	cards.card_game_id = scores.card_game_id and 
	CAST(scores.score as integer) > 80 
order by 
	cast(scores.score as integer) DESC;

