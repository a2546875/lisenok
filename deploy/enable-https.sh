#!/bin/bash
set -e
HOST="lisenok-ru.ru"
EMAIL="n.3leonora@yandex.ru"
ROOT="/opt/lisenok"

ufw allow 443/tcp || true
mkdir -p /var/www/html
apt-get update -y
DEBIAN_FRONTEND=noninteractive apt-get install -y certbot python3-certbot-nginx

# HTTP only first, so ACME can answer
cat > /etc/nginx/sites-available/lisenok <<'EOF'
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name 89.110.94.112 89.110.94.112.sslip.io;
    client_max_body_size 20m;
    location /.well-known/acme-challenge/ { root /var/www/html; }
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF
ln -sfn /etc/nginx/sites-available/lisenok /etc/nginx/sites-enabled/lisenok
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl reload nginx

certbot certonly --webroot -w /var/www/html -d "$HOST" --non-interactive --agree-tos -m "$EMAIL" --keep-until-expiring
test -f /etc/letsencrypt/ssl-dhparams.pem || openssl dhparam -out /etc/letsencrypt/ssl-dhparams.pem 2048

cp "$ROOT/deploy/nginx-https.conf" /etc/nginx/sites-available/lisenok
nginx -t
systemctl reload nginx
echo "https://$HOST"
