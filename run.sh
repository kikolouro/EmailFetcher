#!/bin/bash
if [[ "$(docker images -q emailfetcher:1.0 2> /dev/null)" == "" ]]; then
  cd $HOME/EmailFetcher
  docker build -t emailfetcher:1.0 .
  docker run emailfetcher:1.0
else
  docker run emailfetcher:1.0
fi

docker rmi -f emailfetcher:1.0