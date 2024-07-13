# #/bin/bash

# Build the Docker image
docker build -t mosaify-website .

# Run the Docker container
# docker run --cpu-quota 50000 --memory 8g --env-file .env -p 8000:8000 mosaify-website
docker run --env-file .env -p 8000:8000 mosaify-website


