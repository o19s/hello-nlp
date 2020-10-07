curl --header "Content-Type: application/json" \
  --request POST \
  --data @es-query.json \
  http://localhost:5055/elastic_enrich/osc-blog
