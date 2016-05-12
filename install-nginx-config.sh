#!/usr/bin/env bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
rm /etc/nginx/sites-enabled/default
rm /etc/nginx/sites-enabled/nginx-game-config
ln -s $DIR/nginx-game-config /etc/nginx/sites-enabled/nginx-game-config
