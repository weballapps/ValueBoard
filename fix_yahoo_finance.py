#!/usr/bin/env python3
"""
Yahoo Finance Fix - Patches the main app to use direct API instead of yfinance
Run this to fix Yahoo Finance data access issues
"""

import os
import re

def patch_main_app():
    """Patch the main app to use direct Yahoo Finance API"""
    
    print("🔧 Patching Value Investment Dashboard to use direct Yahoo Finance API...")
    
    # Read the main app file
    with open('stock_value_dashboard.py', 'r') as f:
        content = f.read()
    
    # Check if already patched
    if 'yahoo_api_direct' in content:
        print("✅ App already patched with direct API")
        return True
    
    # Backup original
    with open('stock_value_dashboard.py.backup', 'w') as f:
        f.write(content)
    print("📦 Created backup: stock_value_dashboard.py.backup")
    
    # Apply patches
    patches = [
        # Replace yfinance import
        (
            r'import yfinance as yf',
            '''# import yfinance as yf  # Replaced with direct API
try:
    from yahoo_api_direct import Ticker, DirectYahooFinance
    # Use direct API instead of yfinance
    yf = type('MockYF', (), {'Ticker': Ticker})()
    print("✅ Using direct Yahoo Finance API (bypasses yfinance issues)")
except ImportError:
    import yfinance as yf
    print("⚠️ Falling back to yfinance (may have data issues)")'''
        ),
        
        # Fix the fetch_stock_data method to handle direct API
        (
            r'self\.ticker = yf\.Ticker\(symbol, session=session\)',
            '''try:
                    # Use direct API
                    from yahoo_api_direct import Ticker
                    self.ticker = Ticker(symbol)
                except ImportError:
                    # Fallback to yfinance
                    self.ticker = yf.Ticker(symbol, session=session)'''
        ),
        
        # Add timeout handling
        (
            r'self\.stock_data = self\.ticker\.history\(period=period\)',
            '''self.stock_data = self.ticker.history(period=period)
                    # Add small delay to avoid overwhelming the API
                    import time
                    time.sleep(0.1)'''
        )
    ]
    
    # Apply each patch
    patched_content = content
    for old_pattern, new_content in patches:
        patched_content = re.sub(old_pattern, new_content, patched_content)
    
    # Write patched version
    with open('stock_value_dashboard.py', 'w') as f:
        f.write(patched_content)
    
    print("✅ Applied Yahoo Finance API patches")
    return True

def test_patched_app():
    """Test if the patched app works"""
    print("\n🧪 Testing patched application...")
    
    try:
        # Test import
        import stock_value_dashboard
        print("✅ App imports successfully")
        
        # Test the analyzer
        analyzer = stock_value_dashboard.ValueInvestmentAnalyzer()
        
        # Test data fetch
        print("📊 Testing data fetch for AAPL...")
        success = analyzer.fetch_stock_data('AAPL', period='1d')
        
        if success:
            print("✅ Data fetch successful!")
            
            # Check what we got
            if analyzer.stock_data is not None and not analyzer.stock_data.empty:
                latest_price = analyzer.stock_data['Close'].iloc[-1]
                print(f"📈 Latest AAPL price: ${latest_price:.2f}")
            
            if analyzer.stock_info:
                current_price = analyzer.stock_info.get('currentPrice', 'N/A')
                company_name = analyzer.stock_info.get('longName', 'N/A')
                print(f"🏢 Company: {company_name}")
                print(f"💰 Current price: ${current_price}")
                
            return True
        else:
            print("❌ Data fetch failed")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def restore_backup():
    """Restore from backup if needed"""
    if os.path.exists('stock_value_dashboard.py.backup'):
        with open('stock_value_dashboard.py.backup', 'r') as f:
            content = f.read()
        with open('stock_value_dashboard.py', 'w') as f:
            f.write(content)
        print("✅ Restored from backup")
        return True
    else:
        print("❌ No backup found")
        return False

def main():
    """Main patch process"""
    print("🔧 Yahoo Finance Direct API Patcher")
    print("=" * 40)
    
    # Check if required files exist
    if not os.path.exists('stock_value_dashboard.py'):
        print("❌ stock_value_dashboard.py not found!")
        return
    
    if not os.path.exists('yahoo_api_direct.py'):
        print("❌ yahoo_api_direct.py not found!")
        print("💡 Make sure you have the direct API wrapper file")
        return
    
    # Test direct API first
    print("🧪 Testing direct API...")
    try:
        from yahoo_api_direct import test_direct_api
        # Run a quick test (suppress output)
        import sys
        from io import StringIO
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        api = DirectYahooFinance()
        quote = api.get_quote('AAPL')
        
        sys.stdout = old_stdout
        
        if quote and quote.get('currentPrice'):
            print(f"✅ Direct API working (AAPL: ${quote['currentPrice']})")
        else:
            print("❌ Direct API not working")
            return
    except Exception as e:
        print(f"❌ Direct API test failed: {e}")
        return
    
    # Apply patches
    if patch_main_app():
        # Test the patched app
        if test_patched_app():
            print("\n🎉 Yahoo Finance fix applied successfully!")
            print("\n🚀 Your app should now work with reliable data access")
            print("   Run: python run_desktop.py")
        else:
            print("\n❌ Patch applied but testing failed")
            print("💡 You may need to restart the application")
    else:
        print("❌ Failed to apply patches")

if __name__ == '__main__':
    main()