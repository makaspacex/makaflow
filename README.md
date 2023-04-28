# singbox-server-manager
simple api admin server for sing-box

## 免密码登录

```
cd
mkdir .ssh
chmod 700 .ssh
cd .ssh
touch authorized_keys
chmod 600 authorized_keys
cat >> authorized_keys <<"EOF"
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCoPjpyunH7Pz87DDSVoK5i1ACZpq0dQcV0ranKr0eXW4KR5ytQiyIhmN0AJVEFHP/8HfW/6cn7N34eIV5M+Iyy0Zl6vKyEepyTj/FS1nsZd3oQumrVS7RNhPhwv17+IIoiOpmlVwgxPx4aBynIWsagFlUjDNAwJl2EAepGUYbkplUUZxt1ryZYCUn9I6/zhbuWX5nYMoU1VKLLAYWJNl1VdAe2C3/WfqlGgXWHEGdcUuamiG1RIaLOkmVU+2dAWLrdD7PZP0TSd4E0ngqIsPmSgq4CqMxTkI7XeXlUsjYo8Uf4GgqQmUxZuEocQPSbMeXtU4U0zcEy0HIPFs0+sHtP izhangxm@gmail.com
EOF
cd
```

## 克隆仓库

```bash
apt install python3-pip tmux screen htop git wget multitail lnav socat nginx -y
git clone https://github.com/izhangxm/singbox-server-manager.git
cd singbox-server-manager
pip3 install -r requriements.txt
cp xray_profile.yaml.example xray_profile.yaml
cp env.yaml.example env.yaml
```

## 安装xray

```bash
# doc https://github.com/XTLS/Xray-install
# core-release https://github.com/XTLS/Xray-core/releases
bash -c "$(curl -L https://github.com/XTLS/Xray-install/raw/main/install-release.sh)" @ install --version 1.8.0

# update geo data
wget  https://github.com/Loyalsoldier/v2ray-rules-dat/releases/download/202304062208/geoip.dat -O /usr/local/share/xray/geoip.dat
wget https://github.com/Loyalsoldier/v2ray-rules-dat/releases/download/202304062208/geosite.dat -O /usr/local/share/xray/geosite.dat 
```

## 安装acme并生成证书

```bash
curl https://get.acme.sh | sh -s email=my@example.com

# 需要80端口空闲
acme.sh --issue -d mydomain.com --webroot /var/www/html/
```

## 配置nginx
```
server {
	listen 1443 ssl http2;
	listen [::]:1443 ssl http2;

	server_name gia01.passwall.vip;
	root /var/www/html;

	# SSL
	ssl_certificate_key /var/www/acme/gia01.passwall.vip_ecc/gia01.passwall.vip.key;
	ssl_certificate /var/www/acme/gia01.passwall.vip_ecc/gia01.passwall.vip.cer;

	# security
	# security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;

    # . files
    location ~ /\.(?!well-known) {
        deny all;
    }

	# index.html fallback
	location / {
		try_files $uri $uri/ /index.html;
	}

	# reverse proxy
	location /api {
		proxy_pass http://127.0.0.1:8180/;
		proxy_http_version	1.1;
        proxy_cache_bypass	$http_upgrade;

        proxy_set_header Upgrade			$http_upgrade;
        proxy_set_header Connection 		"upgrade";
        proxy_set_header Host				$host;
        proxy_set_header X-Real-IP			$remote_addr;
        proxy_set_header X-Forwarded-For	$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto	$scheme;
        proxy_set_header X-Forwarded-Host	$host;
        proxy_set_header X-Forwarded-Port	$server_port;
	}

	# additional config
    # favicon.ico
    location = /favicon.ico {
        log_not_found off;
        access_log off;
    }
    # robots.txt
    location = /robots.txt {
        log_not_found off;
        access_log off;
    }

    # assets, media
    location ~* \.(?:css(\.map)?|js(\.map)?|jpe?g|png|gif|ico|cur|heic|webp|tiff?|mp3|m4a|aac|ogg|midi?|wav|mp4|mov|webm|mpe?g|avi|ogv|flv|wmv)$ {
        expires 7d;
        access_log off;
    }

    # svg, fonts
    location ~* \.(?:svgz?|ttf|ttc|otf|eot|woff2?)$ {
        add_header Access-Control-Allow-Origin "*";
        expires 7d;
        access_log off;
    }

    # gzip
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml application/json application/javascript application/rss+xml application/atom+xml image/svg+xml;
}
```
