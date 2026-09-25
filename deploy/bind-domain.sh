#!/bin/bash
set -e
HOST="lisenok-ru.ru"
EMAIL="n.3leonora@yandex.ru"
ROOT="/opt/lisenok"

ufw allow 80/tcp || true
ufw allow 443/tcp || true
mkdir -p /var/www/html

# HTTP must answer ACME for the new domain; keep old HTTPS working.
cat > /etc/nginx/sites-available/lisenok <<'EOF'
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name lisenok-ru.ru www.lisenok-ru.ru 89.110.94.112 89.110.94.112.sslip.io;
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

server {
    listen 443 ssl;
    listen [::]:443 ssl;
    http2 on;
    server_name 89.110.94.112.sslip.io;
    client_max_body_size 20m;
    ssl_certificate /etc/letsencrypt/live/89.110.94.112.sslip.io/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/89.110.94.112.sslip.io/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
    }
}
EOF

nginx -t
systemctl reload nginx

certbot certonly --webroot -w /var/www/html -d "$HOST" -d "www.$HOST" --non-interactive --agree-tos -m "$EMAIL" --expand
test -f /etc/letsencrypt/ssl-dhparams.pem || openssl dhparam -out /etc/letsencrypt/ssl-dhparams.pem 2048

cp "$ROOT/deploy/nginx-https.conf" /etc/nginx/sites-available/lisenok
sed -i 's/\r$//' /etc/nginx/sites-available/lisenok
nginx -t
systemctl reload nginx
echo "https://$HOST"
