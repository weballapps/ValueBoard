#!/usr/bin/env python3
"""
Direct Yahoo Finance API wrapper
Bypasses yfinance library issues by calling Yahoo APIs directly
"""

import requests
import pandas as pd
import time
import random
from datetime import datetime, timedelta
import json

class DirectYahooFinance:
    """Direct Yahoo Finance API wrapper to replace yfinance"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site'
        })
        
    def _make_request(self, url, params=None, retries=3):
        """Make request with retries and delays"""
        for attempt in range(retries):
            try:
                if attempt > 0:
                    delay = random.uniform(1, 3) * (2 ** attempt)
                    time.sleep(delay)
                
                response = self.session.get(url, params=params, timeout=15)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    print(f"Rate limited on attempt {attempt + 1}, retrying...")
                    continue
                else:
                    print(f"API returned status {response.status_code}")
                    return None
                    
            except Exception as e:
                if attempt == retries - 1:
                    print(f"Request failed after {retries} attempts: {e}")
                    return None
                continue
        
        return None
    
    def get_quote(self, symbol):
        """Get current quote data for a symbol"""
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        params = {
            'interval': '1d',
            'range': '1d',
            'includePrePost': 'true'
        }
        
        data = self._make_request(url, params)
        if not data:
            return None
            
        try:
            result = data['chart']['result'][0]
            meta = result['meta']
            
            quote_data = {
                'symbol': symbol,
                'currentPrice': meta.get('regularMarketPrice'),
                'previousClose': meta.get('previousClose'),
                'regularMarketOpen': meta.get('regularMarketOpen'),
                'regularMarketDayHigh': meta.get('regularMarketDayHigh'),
                'regularMarketDayLow': meta.get('regularMarketDayLow'),
                'regularMarketVolume': meta.get('regularMarketVolume'),
                'currency': meta.get('currency'),
                'exchangeName': meta.get('exchangeName'),
                'longName': meta.get('longName', symbol),
                'shortName': meta.get('shortName', symbol)
            }
            
            return quote_data
            
        except (KeyError, IndexError, TypeError) as e:
            print(f"Error parsing quote data for {symbol}: {e}")
            return None
    
    def get_history(self, symbol, period='2y'):
        """Get historical price data"""
        # Convert period to timestamps
        end_time = int(time.time())
        
        period_map = {
            '1d': 1,
            '5d': 5,
            '1mo': 30,
            '3mo': 90,
            '6mo': 180,
            '1y': 365,
            '2y': 730,
            '5y': 1825,
            '10y': 3650,
            'max': 7300
        }
        
        days = period_map.get(period, 730)
        start_time = end_time - (days * 24 * 60 * 60)
        
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        params = {
            'period1': start_time,
            'period2': end_time,
            'interval': '1d',
            'includePrePost': 'true',
            'events': 'div%2Csplit'
        }
        
        data = self._make_request(url, params)
        if not data:
            return pd.DataFrame()
            
        try:
            result = data['chart']['result'][0]
            timestamps = result['timestamp']
            quotes = result['indicators']['quote'][0]
            
            # Create DataFrame
            df = pd.DataFrame({
                'Open': quotes['open'],
                'High': quotes['high'], 
                'Low': quotes['low'],
                'Close': quotes['close'],
                'Volume': quotes['volume']
            })
            
            # Convert timestamps to datetime index
            df.index = pd.to_datetime([datetime.fromtimestamp(ts) for ts in timestamps])
            df.index.name = 'Date'
            
            # Remove rows with all NaN values
            df = df.dropna(how='all')
            
            return df
            
        except (KeyError, IndexError, TypeError) as e:
            print(f"Error parsing historical data for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_info(self, symbol):
        """Get detailed company information"""
        # Get quote data first
        quote = self.get_quote(symbol)
        if not quote:
            return {}
        
        # Get additional company info
        url = f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/{symbol}"
        params = {
            'modules': 'summaryDetail,defaultKeyStatistics,financialData,calendarEvents,upgradeDowngradeHistory,price,balanceSheetHistory,incomeStatementHistory,cashflowStatementHistory'
        }
        
        data = self._make_request(url, params)
        if not data:
            return quote  # Return basic quote data if detailed info fails
        
        try:
            result = data['quoteSummary']['result'][0]
            
            # Combine data from different modules
            info = quote.copy()
            
            # Add data from different modules
            for module_name, module_data in result.items():
                if module_data:
                    for key, value in module_data.items():
                        if isinstance(value, dict) and 'raw' in value:
                            info[key] = value['raw']
                        elif isinstance(value, dict) and 'fmt' in value:
                            info[key] = value.get('raw', value['fmt'])
                        else:
                            info[key] = value
            
            return info
            
        except (KeyError, IndexError, TypeError) as e:
            print(f"Error parsing detailed info for {symbol}: {e}")
            return quote  # Return basic quote data
    
    def search(self, query):
        """Search for symbols by company name"""
        url = "https://query1.finance.yahoo.com/v1/finance/search"
        params = {
            'q': query,
            'quotesCount': 10,
            'newsCount': 0
        }
        
        data = self._make_request(url, params)
        if not data:
            return []
        
        try:
            quotes = data.get('quotes', [])
            results = []
            
            for quote in quotes:
                if quote.get('typeDisp') in ['Equity', 'ETF']:
                    results.append({
                        'symbol': quote.get('symbol'),
                        'name': quote.get('longname', quote.get('shortname', '')),
                        'type': quote.get('typeDisp'),
                        'exchange': quote.get('exchDisp', ''),
                        'score': quote.get('score', 0)
                    })
            
            return results
            
        except (KeyError, TypeError) as e:
            print(f"Error parsing search results: {e}")
            return []

class DirectTicker:
    """yfinance-compatible wrapper using direct API"""
    
    def __init__(self, symbol, session=None):
        self.symbol = symbol.upper()
        self.api = DirectYahooFinance()
        self._info = None
        self._history_cache = {}
    
    @property
    def info(self):
        """Get stock info (cached)"""
        if self._info is None:
            self._info = self.api.get_info(self.symbol)
        return self._info
    
    def history(self, period='2y', **kwargs):
        """Get historical data"""
        if period not in self._history_cache:
            self._history_cache[period] = self.api.get_history(self.symbol, period)
        return self._history_cache[period]
    
    @property
    def financials(self):
        """Placeholder for financials (would need separate implementation)"""
        return pd.DataFrame()
    
    @property
    def balance_sheet(self):
        """Placeholder for balance sheet (would need separate implementation)"""  
        return pd.DataFrame()
    
    @property
    def cashflow(self):
        """Placeholder for cash flow (would need separate implementation)"""
        return pd.DataFrame()
    
    @property
    def quarterly_financials(self):
        """Placeholder for quarterly financials"""
        return pd.DataFrame()
    
    @property
    def quarterly_balance_sheet(self):
        """Placeholder for quarterly balance sheet"""
        return pd.DataFrame()
    
    @property
    def quarterly_cashflow(self):
        """Placeholder for quarterly cash flow"""
        return pd.DataFrame()
    
    @property
    def news(self):
        """Placeholder for news"""
        return []

# Function to replace yfinance.Ticker
def Ticker(symbol, session=None):
    """Drop-in replacement for yf.Ticker"""
    return DirectTicker(symbol, session)

# Test function
def test_direct_api():
    """Test the direct API wrapper"""
    print("Testing Direct Yahoo Finance API...")
    
    api = DirectYahooFinance()
    
    # Test quote
    print("\\n1. Testing quote:")
    quote = api.get_quote('AAPL')
    if quote:
        print(f"✅ AAPL price: ${quote['currentPrice']}")
    else:
        print("❌ Quote failed")
    
    # Test history
    print("\\n2. Testing history:")
    history = api.get_history('AAPL', '1mo')
    if not history.empty:
        print(f"✅ History: {len(history)} days of data")
        print(f"   Latest close: ${history['Close'].iloc[-1]:.2f}")
    else:
        print("❌ History failed")
    
    # Test search
    print("\\n3. Testing search:")
    results = api.search('Apple')
    if results:
        print(f"✅ Search: {len(results)} results")
        for r in results[:3]:
            print(f"   {r['symbol']}: {r['name']}")
    else:
        print("❌ Search failed")
    
    # Test ticker wrapper
    print("\\n4. Testing Ticker wrapper:")
    ticker = Ticker('MSFT')
    info = ticker.info
    if info and info.get('currentPrice'):
        print(f"✅ MSFT via Ticker: ${info['currentPrice']}")
    else:
        print("❌ Ticker wrapper failed")

if __name__ == '__main__':
    test_direct_api()