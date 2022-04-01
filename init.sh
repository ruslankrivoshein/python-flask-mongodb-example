#!/usr/bin/sh

export "$(cat .env.d/app.env | xargs)"

docker cp ./songs.json music_mongo:/tmp/songs.json
docker exec music_mongo mongoimport --uri "$MONGO_CONNECTION_URI" --file /tmp/songs.json
docker exec music_mongo mongo "$MONGO_CONNECTION_URI" --eval 'db.songs.createIndex({artist: "text", title: "text"},{weights: {title: 2},name: "title_artist"})'
