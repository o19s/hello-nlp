docker stop hello_nlp
docker container rm hello_nlp
docker image rm hello_nlp
docker build -t hello_nlp .
docker run --name hello_nlp -p 5055:5055 hello_nlp