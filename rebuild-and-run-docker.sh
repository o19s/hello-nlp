#This will DELETE the existing hello_nlp docker container and images
docker stop hello_nlp
docker container rm hello_nlp
docker image rm hello_nlp
./build-and-run-docker.sh