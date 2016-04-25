#!/usr/bin/env bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ln -s $DIR/nginx-game-config /etc/nginx/sites-enabled/nginx-game-config
