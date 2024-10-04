#!/bin/bash

project_path=""
env_activation_path=""
ROLLBAR_ACCESS_TOKEN=""
ROLLBAR_USER=""

cd "$project_path" || { echo "Couldn't navigate to the directory $project_path"; exit 1; }

if [ -f "$env_activation_path" ]; then
    source "$env_activation_path"
else
    echo "The virtual environment activation file was not found: $env_activation_path"
    exit 1
fi

if git pull; then
    echo "Git all right!"

    if command -v pip &> /dev/null; then
        pip install -r requirements.txt
        echo "Dependencies are set!"
    else
        echo "pip was not found. Skipping the installation of dependencies."
    fi

else
    echo "Git pull is bad!"
    exit 1
fi

python3 manage.py makemigrations || { echo "Failed to make migrations"; exit 1; }
python3 manage.py collectstatic --noinput || { echo "Failed to collect static files"; exit 1; }

deactivate
echo "Exited the virtual environment!"

if command -v npm &> /dev/null; then
    if npm ci --dev --silent; then
        echo "Npm All right!"
    else
        echo "Npm encountered an error!"
    fi
else
    echo "npm was not found. Skipping the installation of npm dependencies."
fi

echo "The cathedral of the frontend..."
./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"
echo "The frontend is assembled"

systemctl restart gunicorn-dev.service || { echo "Failed to restart gunicorn-dev.service"; exit 1; }
systemctl reload nginx.service || { echo "Failed to reload nginx.service"; exit 1; }

curl -X POST https://api.rollbar.com/api/1/deploy/ \
-H "Content-Type: application/json" \
-H "X-Rollbar-Access-Token: $ROLLBAR_ACCESS_TOKEN" \
-d '{
  "access_token": "'"$ROLLBAR_ACCESS_TOKEN"'",
  "environment": "production",
  "revision": "1.0.0",
  "comment": "Deploying version 1.0.0",
  "user": "'"$ROLLBAR_USER"'"
}'

echo "Deployment completed successfully!"
