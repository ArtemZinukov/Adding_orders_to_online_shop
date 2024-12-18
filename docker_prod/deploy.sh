#!/bin/bash

EMAIL="zinykov_a@mail.ru"
DOMAIN="zinukov-a.ru"
DOMAIN_ALIAS="www.zinukov-a.ru"

if ! [ -x "$(command -v nginx)" ]; then
  echo "Nginx не установлен. Установка Nginx..."
  sudo apt update
  sudo apt install nginx -y
  sudo systemctl enable nginx
  sudo systemctl start nginx
  echo "Nginx успешно установлен."
else
  echo "Nginx уже установлен."
fi

if ! [ -x "$(command -v certbot)" ]; then
  echo "Certbot не установлен. Установка Certbot..."
  sudo add-apt-repository ppa:certbot/certbot -y
  sudo apt update
  sudo apt install certbot python3-certbot-nginx -y
  echo "Certbot успешно установлен."
else
  echo "Certbot уже установлен"
fi

if ! [ -x "$(command -v crontab)" ]; then
  echo "Crontab не установлен. Установка Crontab..."
  sudo apt update
  sudo apt install cron
  echo "Crontab успешно установлен."
fi

CERT_DIR="/etc/letsencrypt/live/$DOMAIN"
if [ -d "$CERT_DIR" ]; then
  echo "Existing SSL certificate found at $CERT_DIR."
  read -p "Вы хотите обновить SSL сертификат? (y/n) " UPDATE_CERT
  if [ "$UPDATE_CERT" = "y" ]; then
    echo "Обновление SSL сертификата..."
    sudo certbot --nginx -d $DOMAIN -d $DOMAIN_ALIAS --email $EMAIL --agree-tos --non-interactive --expand
  else
    echo "Сохранение существующего SSL-сертификата."
  fi
else
  echo "Существующий сертификат SSL не найден. Получение нового..."
  sudo certbot --nginx -d $DOMAIN -d $DOMAIN_ALIAS --email $EMAIL --agree-tos --non-interactive --expand
fi

if [ -f "/etc/nginx/sites-enabled/default" ]; then
  sudo rm /etc/nginx/sites-enabled/default
  echo "Удален файл конфигурации Nginx по умолчанию."
fi

echo "Настройка Nginx для использования SSL-сертификатов..."
CONFIG="
server {
    listen 80;
    server_name $DOMAIN $DOMAIN_ALIAS;
    return 301 https://\$host\$request_uri;
}

server {
    listen 443 ssl;
    server_name www.zinukov-a.ru zinukov-a.ru;
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;

    }

    location /static/ {
        alias  /opt/star-burger/static;
        expires 15d;
    }

     location /media/ {
        alias  /opt/star-burger/media;
        expires 7d;
    }
}"

echo "$CONFIG" | sudo tee /etc/nginx/sites-enabled/starburger > /dev/null
sudo nginx -t
sudo systemctl reload nginx

echo "Проверка конфигурации SSL..."
curl -I https://$DOMAIN
openssl s_client -connect $DOMAIN:443 -servername $DOMAIN

echo "Создание и запуск Docker-контейнеров..."
cd /opt/star-burger/docker_prod
docker compose up -d --build

echo "Развертывание успешно завершено."

echo "Настройка задания cron для автоматического обновления сертификата..."
sudo crontab -l | { cat; echo "0 0 */30 * * /usr/bin/certbot renew --quiet"; } | sudo crontab -
echo "Задание Cron успешно настроено."

echo "Настройка задания cron для автоматической очистки сессий..."
sudo crontab -l | { cat; echo "0 0 * * 0 docker exec -it star_burger python manage.py clearsessions"; } | sudo crontab -
echo "Задание Cron успешно настроено."
