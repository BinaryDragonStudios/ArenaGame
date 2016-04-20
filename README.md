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


http://us.battle.net/hearthstone/en/forum/topic/12090628955

I built Arena Mastery, which has about ~12,000 decks tracked 
(when I checked these numbers last week). I don't have the 
data published to the site yet, but in those 12k arena drafts 
the chance of getting a legendary on a given pick is just under 
1% (~.86%). And ~22% of arenas have at least one legendary.

The numbers for epics are about a 3.5% chance per pick with 
about 63% of arenas having at least one.

Obviously this data is all manually entered, so it's not scientific 
fact and should be taken with a grain of salt. But nonetheless it is 
probably a pretty solid data point about the frequency of legendaries.



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


