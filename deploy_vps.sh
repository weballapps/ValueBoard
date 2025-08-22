#!/bin/bash

# VPS Deployment Script for Value Investment Dashboard
# Run this script on your VPS server

echo "🏠 Setting up Value Investment Dashboard on VPS"
echo "=============================================="

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required packages
echo "🐍 Installing Python and dependencies..."
sudo apt install python3 python3-pip python3-venv git nano htop screen ufw -y

# Create application directory
echo "📁 Creating application directory..."
mkdir -p ~/dashboard
cd ~/dashboard

# Create virtual environment
echo "🌐 Setting up virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Create requirements.txt
echo "📝 Creating requirements.txt..."
cat > requirements.txt << 'EOF'
streamlit>=1.28.0
yfinance>=0.2.20
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.15.0
requests>=2.28.0
EOF

# Install Python packages
echo "📚 Installing Python packages..."
pip install -r requirements.txt

# Configure firewall
echo "🔥 Configuring firewall..."
sudo ufw allow 22
sudo ufw allow 8501
sudo ufw --force enable

# Create systemd service
echo "⚙️  Creating system service..."
sudo tee /etc/systemd/system/dashboard.service > /dev/null << EOF
[Unit]
Description=Value Investment Dashboard
After=network.target

[Service]
User=$USER
WorkingDirectory=$HOME/dashboard
Environment=PATH=$HOME/dashboard/venv/bin
ExecStart=$HOME/dashboard/venv/bin/streamlit run stock_value_dashboard.py --server.port=8501 --server.address=0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable service
sudo systemctl daemon-reload
sudo systemctl enable dashboard.service

echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Upload your stock_value_dashboard.py file to ~/dashboard/"
echo "2. Start the service: sudo systemctl start dashboard.service"
echo "3. Check status: sudo systemctl status dashboard.service"
echo "4. Access at: http://$(curl -s ifconfig.me):8501"
echo ""
echo "🔧 Manual start option:"
echo "   cd ~/dashboard && source venv/bin/activate"
echo "   streamlit run stock_value_dashboard.py --server.port=8501 --server.address=0.0.0.0"
echo ""
echo "🖥️  Monitor with: sudo systemctl status dashboard.service"