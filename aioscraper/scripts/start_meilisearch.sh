#!/usr/bin/env bash

docker run -d -p 7700:7700 -v "$(pwd)/data.ms:/data.ms" getmeili/meilisearch

# SOURCE: https://github.com/meilisearch/MeiliSearch
echo "Let's create an index! If you need a sample dataset, use this movie database. You can also find it in the datasets/ directory."

curl -i -X POST "http://$(docker-machine ip dev):7700/indexes" --data '{ "name": "Memes", "uid": "memes" }'

# echo "Now that the server knows about your brand new index, you're ready to send it some data."
# curl -i -X POST 'http://127.0.0.1:7700/indexes/movies/documents' \
#   --header 'content-type: application/json' \
#   --data-binary @movies.json