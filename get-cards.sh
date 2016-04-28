#!/usr/bin/env bash
rm cards.json
rm cards.collectible.json
rm cardtier.json
wget https://api.hearthstonejson.com/v1/latest/enUS/cards.json
wget https://api.hearthstonejson.com/v1/latest/enUS/cards.collectible.json
wget https://raw.githubusercontent.com/rembound/Arena-Helper/master/data/cardtier.json
