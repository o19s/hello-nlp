#Solr
curl --header "Content-Type: application/json" \
  --request POST \
  --data @blog-posts-one.json \
  http://localhost:5050/enrich/osc-blog

curl --header "Content-Type: application/json" \
  --request POST \
  --data @blog-posts-one.json \
  http://localhost:5050/index/osc-blog

#Elastic
curl --header "Content-Type: application/json" \
  --request POST \
  --data @blog-posts-one.json \
  http://localhost:5055/enrich/osc-blog

curl --header "Content-Type: application/json" \
  --request POST \
  --data @blog-posts-one.json \
  http://localhost:5055/index/osc-blog