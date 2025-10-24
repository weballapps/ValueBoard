# 🖥️ Value Investment Dashboard - Desktop Version

## ⚡ Quick Start

### Windows Users
1. **Download** all files from this repository
2. **Double-click** `run_dashboard.bat`
3. **Wait** for installation (first time only)
4. **Done!** Dashboard opens in your browser

### Mac/Linux Users
1. **Download** all files from this repository
2. **Open terminal** in the project folder
3. **Run**: `python run_desktop.py`
4. **Done!** Dashboard opens in your browser

## 🔧 Manual Setup (If needed)

```bash
# 1. Install Python 3.8+ from python.org
# 2. Install requirements
pip install -r requirements.txt

# 3. Test deployment
python test_deployment.py

# 4. Run the app
python run_desktop.py
```

## ✅ Verification

Run the test script to verify everything works:
```bash
python test_deployment.py
```

**Expected output**: 3-4 tests should pass
- ✅ Requirements: All packages installed
- ✅ App Import: No configuration errors  
- ⚠️ Yahoo Finance: May show limited data (normal)
- ✅ Streamlit Startup: App can start

## 🌟 Benefits

- **✅ Bypasses Yahoo Finance cloud restrictions**
- **✅ Full functionality** - all features work
- **✅ International markets** - global stock access
- **✅ Zero cost** - no API fees
- **✅ Fast performance** - runs locally

## 📱 Mobile Access

The app also includes PWA (Progressive Web App) features:
- Install from mobile browser: Chrome → "Install app"
- Works offline with cached data
- Appears as native app icon

## 🚨 Troubleshooting

**Python not found**:
- Install Python 3.8+ from [python.org](https://python.org)
- Make sure "Add to PATH" is checked

**Packages fail to install**:
```bash
python -m pip install --upgrade pip
pip install streamlit yfinance pandas numpy plotly
```

**App won't start**:
- Run `python test_deployment.py` to diagnose
- Check your firewall/antivirus settings
- Try a different port: `streamlit run stock_value_dashboard.py --server.port 8504`

**Yahoo Finance errors**:
- This is expected on some networks
- Try different internet connection
- Desktop version has best success rate

## 🎯 Why Desktop Works

Desktop deployment uses your **personal IP address** instead of shared cloud IPs that Yahoo Finance blocks. This provides:

- Reliable data access
- Full international coverage
- All advanced features
- Zero ongoing costs

Perfect for personal use and sharing with friends/colleagues!