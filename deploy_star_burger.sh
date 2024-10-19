#!/bin/bash

set -e

project_path="/opt/Adding_orders_to_online_shop"
env_activation_path="env/bin/activate"
ROLLBAR_ACCESS_TOKEN=""
ROLLBAR_USER=""

cd "$project_path"

source "$env_activation_path"

git pull
echo "Git updated!"

LATEST_COMMIT=$(git rev-parse HEAD)
echo "Latest commit: $LATEST_COMMIT"

pip install -r requirements.txt

python3 manage.py makemigrations
python3 manage.py collectstatic --noinput

deactivate
echo "Exited the virtual environment!"

npm cache clean --force
npm ci --silent

echo "Building frontend..."
./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"
echo "Frontend assembled"

systemctl restart gunicorn-dev.service
systemctl reload nginx.service

curl -X POST https://api.rollbar.com/api/1/deploy/ \
-H "Content-Type: application/json" \
-H "X-Rollbar-Access-Token: $ROLLBAR_ACCESS_TOKEN" \
-d '{
  "access_token": "'"$ROLLBAR_ACCESS_TOKEN"'",
  "environment": "production",
  "revision": "'"$LATEST_COMMIT"'",
  "comment": "Deploying version '"$LATEST_COMMIT"'",
  "user": "'"$ROLLBAR_USER"'"
}'

echo "Deployment completed!"
