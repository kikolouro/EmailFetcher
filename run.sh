#!/bin/bash
source .env
#(docker images -q emailfetcher:$APPVERSION 2> /dev/null)
if [[ "$(docker images -q emailfetcher:$APPVERSION 2> /dev/null)" == "" ]]; then
  cd $HOME/EmailFetcher
  docker build -t emailfetcher:$APPVERSION .
  docker run emailfetcher:$APPVERSION
else
  docker run emailfetcher:$APPVERSION
fi

./delete.sh