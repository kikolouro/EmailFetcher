#!/bin/bash
source .env
docker image rm -f emailfetcher:$APPVERSION 