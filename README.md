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
git clone https://github.com/izhangxm/makaflow.git
cd makaflow
pip3 install -r requriements.txt
cp data/server_tps/xray_profile.yaml.example runtime/xray_profile.yaml
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
