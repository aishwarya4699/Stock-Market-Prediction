#!/bin/bash

RDBMS=${1:-MYSQL}
if [ $RDBMS = "MYSQL" ]; then
    sudo docker stop mysql
elif [ $RDBMS = "POSTGRES" ]; then
    sudo docker stop postgres
fi

sudo docker stop mongo

yes | sudo docker system prune
yes | sudo docker volume prune
