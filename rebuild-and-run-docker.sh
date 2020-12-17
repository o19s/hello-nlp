docker-compose -f $1 down
docker-compose -f $1 build
docker-compose -f $1 up