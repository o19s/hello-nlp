#Solr
echo "Testing enrichment without indexing..."
curl --header "Content-Type: application/json" \
  --request POST \
  --data @blog-posts-one.json \
  http://localhost:5050/enrich/osc-blog

echo "Testing enrichment and indexing..."
curl --header "Content-Type: application/json" \
  --request POST \
  --data @blog-posts-one.json \
  http://localhost:5050/index/osc-blog