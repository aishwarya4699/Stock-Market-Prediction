#!/bin/bash

RDBMS=${1:-MYSQL}
PW="${RDBMS}_PASSWORD"
PWD=${!PW}

if [[ -z $PWD ]]; then
	echo "export \$$PW=<password>"
	exit 1
fi

sudo apt install -y docker;

if [ $RDBMS = "MYSQL" ]; then
	sudo apt install -y mysql-client
	sudo docker run --name mysql -d -p 3306:3306 -e MYSQL_ROOT_PASSWORD=${MYSQL_PASSWORD} -e MYSQL_USER=root -e MYSQL_PASSWORD=${MYSQL_PASSWORD} mysql/mysql-server

	while ! sudo docker exec mysql mysqladmin -u=root -password=${MYSQL_PASSWORD} ping --silent &> /dev/null;
		do sleep 5
	done;
	sleep 5

	sudo docker exec -it mysql mysql -u root -p -e "GRANT ALL ON *.* TO 'root'@'%' WITH GRANT OPTION;"
	mysql -h 127.0.0.1 -P 3306 -u root -p -e "show databases"

elif [ $RDBMS = "POSTGRES" ]; then
    sudo apt install -y postgresql-client
	sudo docker run --name postgres -d -p 5432:5432 -e POSTGRES_PASSWORD=${POSTGRES_PASSWORD} -e POSTGRES_USER=root postgres

	while ! nc -z localhost 5432; do sleep 1; done;
	sleep 2

	sudo docker exec -it postgres psql -h localhost -p 5432 -U root -W -c "\l"
	psql -h localhost -p 5432 -U root -W -c "\l"

fi

sudo apt install -y mongodb-clients
sudo docker run --name mongo -d -p 27017:27017 mongo

python env_teardown.py
python env_setup.py
