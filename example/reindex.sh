#Solr
curl --header "Content-Type: application/json" \
  --request POST \
  http://localhost:5050/reindex/osc-blog

#Elastic
curl --header "Content-Type: application/json" \
  --request POST \
  http://localhost:5055/reindex/osc-blog