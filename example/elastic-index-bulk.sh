#Elastic
echo "Testing bulk enrichment and indexing..."
curl --header "Content-Type: application/json" \
  --request POST \
  --data @blog-posts.json \
  http://localhost:5055/bulk/osc-blog