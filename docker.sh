# #/bin/bash

# Build the Docker image
docker build -t mosaify-website .

# Run the Docker container
docker run -p 8000:8000 mosaify-website
