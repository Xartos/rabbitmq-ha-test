#!/bin/bash

if [ -f running_hosts ]; then
  while read row; do
    sudo docker kill $row
  done <running_hosts

  rm running_hosts
fi

sudo docker ps -aq --no-trunc -f status=exited | xargs sudo docker rm
