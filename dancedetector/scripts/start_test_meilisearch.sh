#!/usr/bin/env bash

docker run -d --rm -p 7701:7701 -e MEILI_HTTP_ADDR="0.0.0.0:7701" --name test-meilisearch getmeili/meilisearch

# SOURCE: https://github.com/meilisearch/MeiliSearch
echo "Let's create an index! If you need a sample dataset, use this movie database. You can also find it in the datasets/ directory."

curl -i -X POST "http://$(docker-machine ip dev):7701/indexes" --data '{ "name": "Memes", "uid": "memes" }'

# echo "Now that the server knows about your brand new index, you're ready to send it some data."
# curl -i -X POST 'http://127.0.0.1:7700/indexes/movies/documents' \
#   --header 'content-type: application/json' \
#   --data-binary @movies.json
