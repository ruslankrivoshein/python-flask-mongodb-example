# REST API service example

## How it works
Infrastructure includes following:
- MongoDB;
- mongo-express — web-client for MongoDB (available in _/mongo-express/_ or on the port 8081 if local);
- Portainer — web-client for Docker (available in _/portainer/_ or on the port 9000 if local).

Service API follows JSON:API specification. Read more [here](https://jsonapi.org/).  
Requests are serving by `nginx` and proxying to `gunicorn`'s workers. Acceptable content type — `application/vnd.api+json`.  

Endpoints:
- /api/songs/?page[cursor]=&page[size]=&sort= — List of songs with cursor-based pagination;
- /api/songs/avg_difficulty/?level= — Average difficulty, _level_ is optional;
- /api/search/?message= — Case-insensitive search by title and artist;
- /songs/:id/rate/ — Rate song by ID;
- /songs/:id/rating/ — Ratings (highest, lowest, average) of song by ID.

## First launch
### Preparation
Create *.env files for every group from .env.d/.env.example, fill the values.  
To keep data from **MongoDB** and **Portainer** create volumes via 
`docker volume create music_mongo` and `docker volume create music_portainer`.

### Start
The only command to launch the prepared infrastructure is `docker-compose up -d`.

## Development
To launch the infrastructure locally execute `docker-compose -f docker-compose.dev.yaml up -d`.  

Local launching doesn't use `nginx`, so you can start the service by executing `python main.py`.  
> Don't forget to change DB host from `mongo` to `localhost` in _app.env_  

Execute `./init.sh` to initialize database with test data and to create required indexes.

To run tests execute `pytest` inside root folder.  
To measure coverage execute `coverage run -m pytest` and then `coverage report`.   

> Every new blueprint that is going to connect to MongoDB MUST inherit `MongoResourceBlueprint` to process `ObjectId` correctly  

> DO NOT commit *.env files!  

## Miscellaneous
After any _*.env_ update, all touched containers must be recreated via `docker-compose up -d` to apply new config.  

## Troubleshooting
Search every error in containers logs by command `docker-compose logs` and _service_name_ at the end.
Also, don't forget to monitor containers' health by **Portainer**.
