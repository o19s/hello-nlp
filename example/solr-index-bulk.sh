#Solr
echo "Testing bulk enrichment and indexing..."
curl --header "Content-Type: application/json" \
  --request POST \
  --data @blog-posts-one.json \
  http://localhost:5050/bulk/osc-blog