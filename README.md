<p align="center">
  <img src="/assets/logo.png" alt="Alexa Skill Logo" />
</p>

<h1 align="center">Alexa Q&A Skill</h1>

<p align="center">
  Full code to deploy your own Alexa skill backend with Docker, AWS EC2, API Gateway, ECR, and Gemini.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/AWS-EC2%20%2B%20ECR%20%2B%20API%20Gateway-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/Docker-Deploy-2496ED?style=for-the-badge&logo=docker&logoColor=white" />
  <img src="https://img.shields.io/badge/Gemini-AI-4285F4?style=for-the-badge&logo=google&logoColor=white" />
</p>

## Repository Overview

This repo contains everything needed to run an Alexa skill backend on your own AWS account.

It covers:

1. Creating a custom Alexa skill in the Amazon Developer Console
2. Adding an invocation name and sample phrases
3. Configuring the skill endpoint
4. Creating an API Gateway in AWS
5. Hosting the backend on EC2
6. Getting a Gemini API key from Google AI Studio
7. Building and pushing the Docker image to Amazon ECR
8. Pulling and running the container on EC2

## Architecture

```mermaid
flowchart LR
    U[User speaks to Alexa] --> A[Alexa Skill]
    A --> G[API Gateway HTTPS endpoint]
    G --> E[EC2 Docker container]
    E --> GM[Gemini API]
    E --> R[Alexa JSON response]
    R --> A
```

## Prerequisites

You need:

1. An AWS account
2. An Amazon Developer account
3. AWS CLI installed and configured
4. Docker installed locally
5. An EC2 key pair
6. A Gemini API key
7. Your backend code in this repo

## 1. Create the skill in Alexa Developer Console

1. Go to the Alexa Developer Console
2. Click **Create Skill**
3. Enter a skill name, for example `Mini Link`
4. Choose **Custom**
5. Continue with your preferred hosting option, because this repo hosts the backend itself
6. Create the skill

## 2. Add the invocation name

Set an invocation name users can say naturally, like "Mini Link"

## 3. Add intents and phrases

Create a custom intent:

1. Intent name: `AskAgentIntent`
2. Slot name: `question`
3. Slot type: `AMAZON.SearchQuery`

Example utterances:

1. `ask {question}`
2. `question {question}`
3. `tell me {question}`

Keep these built in intents too:

1. `AMAZON.HelpIntent`
2. `AMAZON.CancelIntent`
3. `AMAZON.StopIntent`
4. `AMAZON.FallbackIntent`

After editing:

1. Click **Save Model**
2. Click **Build Model**

## 4. Get the required env values

Create a local `.env` file first, then copy that same file to EC2 later.

Example:

```env
GEMINI_API_KEY=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_DEFAULT_REGION=eu-central-1
ALEXA_SKILL_ID=
```

### GEMINI_API_KEY

Get this from Google AI Studio.

Steps:

1. Open [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Create or select a project
4. Create an API key
5. Copy it into:

```env
GEMINI_API_KEY=your_gemini_key_here
```

More info: [Gemini API key docs](https://ai.google.dev/gemini-api/docs/api-key)

### AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY

These are AWS access keys for an IAM user.

Steps:

1. Open AWS Console
2. Go to **IAM**
3. Open **Users**
4. Create a user or select an existing user
5. Open the **Security credentials** tab
6. Under **Access keys**, click **Create access key**
7. Copy the generated values into:

```env
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
```

### AWS_DEFAULT_REGION

Set this to the region you use for ECR, EC2, and API Gateway.

Example:

```env
AWS_DEFAULT_REGION=eu-central-1
```

### ALEXA_SKILL_ID

Get this from the Alexa Developer Console.

Steps:

1. Open the Alexa Developer Console
2. Go to **Your Skills**
3. Select your skill
4. Copy the **Skill ID**
5. Paste it into:

```env
ALEXA_SKILL_ID=your_skill_id_here
```

## 5. Create the local `.env`

Create `deploy_config/.env`:

```env
GEMINI_API_KEY=your_gemini_key_here
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
AWS_DEFAULT_REGION=eu-central-1
ALEXA_SKILL_ID=your_skill_id_here
```

Do not commit the real `.env` file.

Example `.gitignore`:

```gitignore
.env
deploy_config/.env
alexa-key.pem
```

## 6. Create an ECR repository

Create a private ECR repository:

```bash
aws ecr create-repository --repository-name alexa-skill --region eu-central-1
```

Repository URL format:

```text
<AWS_ACCOUNT_ID>.dkr.ecr.eu-central-1.amazonaws.com/alexa-skill
```

## 7. Build and push Docker

Log in to ECR:

```bash
aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin <AWS_ACCOUNT_ID>.dkr.ecr.eu-central-1.amazonaws.com
```

Build the image:

```bash
docker build --platform linux/amd64 -t alexa-skill .
```

Tag the image:

```bash
docker tag alexa-skill:latest <AWS_ACCOUNT_ID>.dkr.ecr.eu-central-1.amazonaws.com/alexa-skill:latest
```

Push the image:

```bash
docker push <AWS_ACCOUNT_ID>.dkr.ecr.eu-central-1.amazonaws.com/alexa-skill:latest
```

Use the same commands every time you deploy a new version.

## 8. Launch an EC2 server

Create an EC2 instance in AWS.

Recommended setup:

1. Name: `Alexa-Skill-Server`
2. OS: Amazon Linux 2023
3. Instance type: use a Free Tier eligible micro instance if your AWS account supports it
4. Public IP: enabled
5. Security group:
   1. Allow SSH from your own IP
   2. Allow HTTP from the internet on port 80

In **User Data**, paste:

```bash
#!/bin/bash
yum update -y
yum install -y docker
service docker start
usermod -a -G docker ec2-user
```

After the instance is running:

1. Keep the `.pem` file safe
2. Copy the EC2 public IPv4 address

## 9. SSH into EC2

Secure the key:

```bash
chmod 400 alexa-key.pem
```

Connect:

```bash
ssh -i alexa-key.pem ec2-user@<EC2_IP>
```

## 10. Create the deploy script

Create `deploy_config/up.sh`:

```bash
#!/bin/bash
set -euxo pipefail

aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin <AWS_ACCOUNT_ID>.dkr.ecr.eu-central-1.amazonaws.com

REPO="<AWS_ACCOUNT_ID>.dkr.ecr.eu-central-1.amazonaws.com/alexa-skill"

docker pull $REPO:latest
docker stop alexa_skill || true
docker rm alexa_skill || true

docker run -d \
  --name alexa_skill \
  --restart always \
  -p 80:80 \
  --env-file .env \
  $REPO:latest
```

## 11. Copy `.env` and `up.sh` to EC2

Your `.env` must also exist on the EC2 server because Docker reads it there when the container starts.

Copy `.env`:

```bash
scp -i alexa-key.pem deploy_config/.env ec2-user@<EC2_IP>:~/.env
```

Copy `up.sh`:

```bash
scp -i alexa-key.pem deploy_config/up.sh ec2-user@<EC2_IP>:~/up.sh
```

Run it remotely:

```bash
ssh -i alexa-key.pem ec2-user@<EC2_IP> "chmod +x up.sh && ./up.sh"
```

Your container should now be running on EC2 port 80.

## 12. Create API Gateway

Go to **API Gateway** in AWS and create an **HTTP API**.

Use these values:

1. Integration type: HTTP
2. Backend URL: `http://<EC2_IP>:80`
3. Method: `POST`

Create a route:

```text
POST /alexa
```

Deploy using the default stage.

After creation you will get an invoke URL like:

```text
https://<API_ID>.execute-api.<REGION>.amazonaws.com
```

Your final Alexa endpoint becomes:

```text
https://<API_ID>.execute-api.<REGION>.amazonaws.com/alexa
```

## 13. Add the endpoint in Alexa Developer Console

In Alexa Developer Console:

1. Open your skill
2. Go to **Endpoint**
3. Choose **HTTPS**
4. In **Default Region**, paste:

```text
https://<API_ID>.execute-api.<REGION>.amazonaws.com/alexa
```

5. Save endpoints

## 14. Backend route

Your backend should accept:

```text
POST /alexa
```

Example FastAPI route:

```python
from fastapi import APIRouter, Request

router = APIRouter()

@router.post("/alexa")
async def alexa_endpoint(request: Request):
    body = await request.json()
    return {
        "version": "1.0",
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": "Hello from your Alexa backend"
            },
            "shouldEndSession": True
        }
    }
```

## 15. Test the endpoint

```bash
curl -v -X POST "https://<API_ID>.execute-api.<REGION>.amazonaws.com/alexa" \
 -H "Content-Type: application/json" \
 -d '{
  "version": "1.0",
  "session": {
    "new": true,
    "application": { "applicationId": "test" },
    "user": { "userId": "test-user" }
  },
  "request": {
    "type": "LaunchRequest",
    "requestId": "test-request",
    "timestamp": "2026-03-18T12:00:00Z"
  }
}'
```

## 16. Deploy updates

Whenever you change the code:

```bash
aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin <AWS_ACCOUNT_ID>.dkr.ecr.eu-central-1.amazonaws.com

docker build --platform linux/amd64 -t alexa-skill .
docker tag alexa-skill:latest <AWS_ACCOUNT_ID>.dkr.ecr.eu-central-1.amazonaws.com/alexa-skill:latest
docker push <AWS_ACCOUNT_ID>.dkr.ecr.eu-central-1.amazonaws.com/alexa-skill:latest

ssh -i alexa-key.pem ec2-user@<EC2_IP> "chmod +x up.sh && ./up.sh"
```

## Quick start

```bash
aws ecr create-repository --repository-name alexa-skill --region eu-central-1

aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin <AWS_ACCOUNT_ID>.dkr.ecr.eu-central-1.amazonaws.com

docker build --platform linux/amd64 -t alexa-skill .
docker tag alexa-skill:latest <AWS_ACCOUNT_ID>.dkr.ecr.eu-central-1.amazonaws.com/alexa-skill:latest
docker push <AWS_ACCOUNT_ID>.dkr.ecr.eu-central-1.amazonaws.com/alexa-skill:latest

scp -i alexa-key.pem deploy_config/.env ec2-user@<EC2_IP>:~/.env
scp -i alexa-key.pem deploy_config/up.sh ec2-user@<EC2_IP>:~/up.sh
ssh -i alexa-key.pem ec2-user@<EC2_IP> "chmod +x up.sh && ./up.sh"
```
