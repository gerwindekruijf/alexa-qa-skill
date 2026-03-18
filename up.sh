#!/bin/bash
# deploy_config/up.sh

# 1. Export env vars so AWS CLI can see them
export $(grep -v '^#' .env | xargs)

# 2. Login
aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin <YOUR_REGISTRY>.dkr.ecr.eu-central-1.amazonaws.com

# 3. Deploy
REPO="<YOUR_REGISTRY>.dkr.ecr.eu-central-1.amazonaws.com/alexa-skill"

docker pull $REPO:latest
docker stop alexa_skill || true
docker rm alexa_skill || true

docker run -d \
  --name alexa_skill \
  --restart always \
  -p 80:80 \
  --env-file .env \
  $REPO:latest
