# 📈 Value Investment Dashboard

A comprehensive stock analysis platform for American and European markets, featuring multiple valuation models, stock screening, and ETF analysis.

## 🌟 Key Features

### 📊 Individual Stock Analysis
- **10+ Valuation Models**: DCF, Graham Number, Dividend Discount, PEG, Asset-Based, Earnings Power Value
- **Interactive Visualizations**: Enhanced charts with horizontal bars and vertical reference lines
- **Multi-Currency Support**: Automatic conversion for European stocks (EUR, GBP, CHF)
- **Statistical Analysis**: Average, median, standard deviation of fair value estimates

### 🎯 Configurable Stock Screening  
- **Value Screening**: Customizable P/E, P/B, ROE, debt ratios with interactive sliders
- **Growth Screening**: Revenue growth, earnings growth, PEG ratio parameters
- **Value-Growth (GARP)**: Combined screening with 12+ configurable criteria
- **Market Cap Filters**: $50M - $5000B range with precise control

### 📈 ETF Dashboard
- **Real Holdings Data**: Actual company holdings with accurate percentages (fixed from mock data)
- **Corrected YTD Returns**: Accurate YTD calculations replacing unreliable data
- **Category Browser**: 7 main categories with detailed subcategories
- **Performance Analysis**: Multiple timeframe comparisons with export functionality

## 🌍 Market Coverage

**United States**: S&P 500, NASDAQ, NYSE | **Germany**: DAX | **UK**: FTSE 100 | **France**: CAC 40 | **Netherlands**: AEX | **Switzerland**: SMI | **Nordic**: OMX

## 🚀 Quick Deployment

### Option 1: Streamlit Community Cloud (Recommended - Free)
1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Value Investment Dashboard"
   git remote add origin https://github.com/USERNAME/value-dashboard.git
   git push -u origin main
   ```

2. **Deploy:** Visit [share.streamlit.io](https://share.streamlit.io), connect GitHub, select repo, deploy!

3. **Live in 2 minutes** at: `https://USERNAME-value-dashboard-xyz.streamlit.app`

### Option 2: Local Setup
```bash
pip install -r requirements.txt
streamlit run stock_value_dashboard.py
```

## 💡 What Users Get

✅ **Professional Analysis**: 10 valuation models with statistical validation  
✅ **Visual Intelligence**: Color-coded charts showing fair value vs current price  
✅ **Smart Screening**: Filter 1000+ stocks with precision controls  
✅ **Global Markets**: US + European stocks with currency conversion  
✅ **ETF Insights**: Real holdings data and corrected performance metrics  
✅ **Export Ready**: CSV downloads for further analysis  

## 🎨 Latest Enhancements

- **Enhanced Valuation Chart**: Horizontal bars + vertical reference lines for current price, average, and median
- **Median Calculations**: More robust fair value estimates alongside averages
- **Fixed ETF Data**: Corrected YTD returns (was showing -532% instead of -0.44% for IYH)
- **Real Holdings**: Actual company names instead of "Top Holding 1, Top Holding 2"
- **Sidebar Documentation**: Comprehensive help available on all pages

## 🛠️ Tech Stack

**Frontend**: Streamlit | **Visualization**: Plotly | **Data**: yfinance, pandas | **Deployment**: Streamlit Cloud

## ⚠️ Important Notes

- **Educational Purpose**: Not financial advice - consult professionals
- **Free Tier**: Public GitHub repo required for free Streamlit deployment
- **Data Source**: Yahoo Finance API (free but rate-limited)
- **Auto-Sleep**: App may sleep after inactivity (auto-wakes)

---

**Ready to deploy? Follow the [deployment_guide.md](deployment_guide.md) for step-by-step instructions!**# ValueBoard
