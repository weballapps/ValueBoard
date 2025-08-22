# 🏠 VPS Deployment Guide - Value Investment Dashboard

## 🎯 Goal: Private hosting on your own server with custom IP:PORT access

### Step 1: Get a VPS Server

#### Recommended Providers:
- **DigitalOcean**: $5/month droplet (1GB RAM, 25GB SSD) - [digitalocean.com](https://digitalocean.com)
- **Linode**: $5/month Nanode (1GB RAM, 25GB SSD) - [linode.com](https://linode.com)  
- **Vultr**: $5/month instance (1GB RAM, 25GB SSD) - [vultr.com](https://vultr.com)
- **Hetzner**: €4.15/month CX11 (1GB RAM, 20GB SSD) - [hetzner.com](https://hetzner.com)

#### VPS Configuration:
- **OS**: Ubuntu 22.04 LTS (recommended)
- **RAM**: 1GB minimum (2GB preferred for better performance)
- **Storage**: 25GB sufficient
- **Location**: Choose closest to your users

### Step 2: Initial Server Setup

#### Connect to your VPS:
```bash
# SSH into your server (replace with your server IP)
ssh root@YOUR_SERVER_IP

# Or if you set up a user account:
ssh username@YOUR_SERVER_IP
```

#### Update system and install Python:
```bash
# Update package list
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv git nano htop screen -y

# Verify installation
python3 --version
pip3 --version
```

### Step 3: Upload Your Application

#### Method 1: Direct Copy-Paste (Simplest)
```bash
# Create directory for your app
mkdir ~/dashboard
cd ~/dashboard

# Create the main Python file
nano stock_value_dashboard.py
# Copy-paste your entire stock_value_dashboard.py content here
# Save with Ctrl+X, Y, Enter

# Create requirements file
nano requirements.txt
# Add the content:
streamlit>=1.28.0
yfinance>=0.2.20
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.15.0
requests>=2.28.0
# Save with Ctrl+X, Y, Enter
```

#### Method 2: SCP Upload (From your local machine)
```bash
# From your local machine, upload all files
scp -r /Users/pballest/PycharmProjects/Value/* root@YOUR_SERVER_IP:/root/dashboard/
```

#### Method 3: Git Clone (If you want to use Git later)
```bash
# If you put it on GitHub
git clone https://github.com/yourusername/your-repo.git dashboard
cd dashboard
```

### Step 4: Install Dependencies

```bash
cd ~/dashboard

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Test installation
python3 -c "import streamlit; print('Streamlit installed successfully')"
```

### Step 5: Configure Firewall

```bash
# Allow SSH (important - don't lock yourself out!)
sudo ufw allow 22

# Allow your custom port (example: 8501)
sudo ufw allow 8501

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

### Step 6: Run Your Application

#### Test Run (Temporary):
```bash
cd ~/dashboard
source venv/bin/activate
streamlit run stock_value_dashboard.py --server.port=8501 --server.address=0.0.0.0
```

**Your app should now be accessible at**: `http://YOUR_SERVER_IP:8501`

### Step 7: Keep App Running Permanently

#### Method 1: Using Screen (Simple)
```bash
# Install screen if not already installed
sudo apt install screen

# Start a screen session
screen -S dashboard

# Run your app
cd ~/dashboard
source venv/bin/activate
streamlit run stock_value_dashboard.py --server.port=8501 --server.address=0.0.0.0

# Detach from screen: Press Ctrl+A, then D
# Your app keeps running even when you log out

# To reconnect later:
screen -r dashboard
```

#### Method 2: Using systemd (Professional)
```bash
# Create service file
sudo nano /etc/systemd/system/dashboard.service

# Add this content:
[Unit]
Description=Value Investment Dashboard
After=network.target

[Service]
User=root
WorkingDirectory=/root/dashboard
Environment=PATH=/root/dashboard/venv/bin
ExecStart=/root/dashboard/venv/bin/streamlit run stock_value_dashboard.py --server.port=8501 --server.address=0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target

# Save and enable the service
sudo systemctl daemon-reload
sudo systemctl enable dashboard.service
sudo systemctl start dashboard.service

# Check status
sudo systemctl status dashboard.service
```

### Step 8: Custom Port and Security

#### Use a Custom Port (More Secure):
```bash
# Instead of 8501, use a random port like 9847
streamlit run stock_value_dashboard.py --server.port=9847 --server.address=0.0.0.0

# Update firewall
sudo ufw allow 9847
sudo ufw delete allow 8501  # Remove old rule
```

#### Access URL becomes: `http://YOUR_SERVER_IP:9847`

### Step 9: Optional Enhancements

#### Add Basic Authentication:
```bash
# Install nginx for reverse proxy with auth
sudo apt install nginx apache2-utils

# Create password file
sudo htpasswd -c /etc/nginx/.htpasswd your_username

# Configure nginx (advanced - creates a login page)
```

#### Add SSL Certificate (HTTPS):
```bash
# Install certbot
sudo apt install certbot

# Get certificate (requires domain name)
sudo certbot certonly --standalone -d yourdomain.com
```

#### Monitor Your App:
```bash
# Install monitoring tools
sudo apt install htop

# Check app status
ps aux | grep streamlit

# Check logs
journalctl -u dashboard.service -f
```

### Step 10: Sharing Access

#### Your users access via:
- **URL**: `http://YOUR_SERVER_IP:PORT`
- **Example**: `http://134.56.78.90:9847`
- **No accounts needed** - just give them the URL
- **Works on any device** with a browser

#### Privacy Level:
- ✅ **Maximum Privacy**: Only accessible via direct IP:PORT
- ✅ **No Search Indexing**: Won't appear in Google
- ✅ **Custom Port**: Makes it even harder to discover
- ✅ **Full Control**: You manage everything
- ✅ **No Third Parties**: Your server, your rules

## 🚀 Quick Start Commands (All-in-One)

```bash
# After getting your VPS, run these commands:
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv screen -y
mkdir ~/dashboard && cd ~/dashboard

# Upload your files here (copy-paste or SCP)
# Create requirements.txt and stock_value_dashboard.py

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

sudo ufw allow 22
sudo ufw allow 8501
sudo ufw enable

screen -S dashboard
streamlit run stock_value_dashboard.py --server.port=8501 --server.address=0.0.0.0
# Press Ctrl+A, then D to detach

# Access at: http://YOUR_SERVER_IP:8501
```

## 💰 Cost Breakdown:
- **VPS**: $5/month
- **Domain** (optional): $10/year  
- **SSL Certificate**: Free with Let's Encrypt
- **Total**: ~$5/month for complete control

## 🛡️ Security Tips:
1. **Change default SSH port** from 22 to something else
2. **Use SSH keys** instead of passwords
3. **Regular backups** of your application
4. **Monitor server resources** with `htop`
5. **Keep system updated**: `sudo apt update && sudo apt upgrade`

---

**You'll have complete control over your Value Investment Dashboard with maximum privacy!**