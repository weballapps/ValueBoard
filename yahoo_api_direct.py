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
        """Get detailed company information with multiple fallback approaches"""
        # Get quote data first
        quote = self.get_quote(symbol)
        if not quote:
            return {}
        
        info = quote.copy()
        
        # Try multiple data sources in order of preference
        data_sources = [
            self._try_api_approach,
            self._try_alternative_apis,
            self._try_web_scraping_for_fundamentals,
            self._try_basic_calculations
        ]
        
        for source_func in data_sources:
            try:
                enhanced_info = source_func(symbol, info)
                if enhanced_info and len(enhanced_info) > len(info):
                    info = enhanced_info
                    
                    # Check if we have enough fundamental data to skip further attempts
                    fundamental_metrics = ['trailingPE', 'forwardPE', 'priceToBook', 'marketCap', 'dividendYield']
                    found_metrics = sum(1 for metric in fundamental_metrics if info.get(metric) is not None and info.get(metric) != 0)
                    
                    if found_metrics >= 3:  # If we have good fundamental data, stop here
                        break
            except Exception as e:
                continue
        
        # Return only real data that we actually fetched
        return info
    
    def _try_api_approach(self, symbol, quote):
        """Try multiple API endpoints to get real data"""
        # Try different endpoint combinations
        api_attempts = [
            # Comprehensive endpoint
            {
                'url': f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/{symbol}",
                'params': {'modules': 'summaryDetail,defaultKeyStatistics,financialData,price,upgradeDowngradeHistory'}
            },
            # Alternative endpoint  
            {
                'url': f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}",
                'params': {'interval': '1d', 'range': '1d', 'includePrePost': 'true'}
            },
            # Simple info endpoint
            {
                'url': f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/{symbol}",
                'params': {'modules': 'price,summaryDetail'}
            }
        ]
        
        for attempt in api_attempts:
            try:
                data = self._make_request(attempt['url'], attempt['params'])
                if not data:
                    continue
                
                info = quote.copy()
                
                # Parse different response structures
                if 'quoteSummary' in data:
                    result = data['quoteSummary']['result']
                    if result and len(result) > 0:
                        # Process all modules
                        for module_name, module_data in result[0].items():
                            if module_data:
                                for key, value in module_data.items():
                                    if isinstance(value, dict) and 'raw' in value:
                                        info[key] = value['raw']
                                    elif isinstance(value, dict) and 'fmt' in value:
                                        info[key] = value.get('raw', value['fmt'])
                                    else:
                                        info[key] = value
                
                elif 'chart' in data:
                    # Parse chart response for basic data
                    chart_result = data['chart']['result'][0]
                    meta = chart_result['meta']
                    for key, value in meta.items():
                        if key not in info:  # Don't override existing data
                            info[key] = value
                
                # If we got meaningful additional data, return it
                if len(info) > len(quote) + 2:  # More than just basic quote data
                    return info
                    
            except Exception as e:
                continue
        
        return quote
    
    def _try_alternative_apis(self, symbol, info):
        """Try alternative financial data sources"""
        # Yahoo Finance mobile API (sometimes works when main API doesn't)
        mobile_endpoints = [
            f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbol}",
            f"https://query2.finance.yahoo.com/v7/finance/options/{symbol}",
            f"https://query1.finance.yahoo.com/v11/finance/quoteSummary/{symbol}?modules=price"
        ]
        
        for url in mobile_endpoints:
            try:
                data = self._make_request(url)
                if data:
                    # Parse quote response
                    if 'quoteResponse' in data and 'result' in data['quoteResponse']:
                        results = data['quoteResponse']['result']
                        if results and len(results) > 0:
                            result = results[0]
                            
                            # Map financial metrics
                            field_mapping = {
                                'trailingPE': result.get('trailingPE'),
                                'forwardPE': result.get('forwardPE'), 
                                'priceToBook': result.get('priceToBook'),
                                'marketCap': result.get('marketCap'),
                                'sharesOutstanding': result.get('sharesOutstanding'),
                                'dividendYield': result.get('dividendYield'),
                                'trailingEps': result.get('epsTrailingTwelveMonths'),
                                'bookValue': result.get('bookValue')
                            }
                            
                            # Add valid data
                            for key, value in field_mapping.items():
                                if value is not None and value != 0:
                                    info[key] = value
                            
                            # If we got substantial data, return it
                            if len([v for v in field_mapping.values() if v is not None]) >= 3:
                                return info
                    
                    # Parse options response for basic data
                    if 'optionChain' in data and 'result' in data['optionChain']:
                        results = data['optionChain']['result']
                        if results and len(results) > 0:
                            quote_data = results[0].get('quote', {})
                            for key in ['trailingPE', 'forwardPE', 'priceToBook', 'marketCap']:
                                if key in quote_data and quote_data[key] is not None:
                                    info[key] = quote_data[key]
                                    
            except Exception as e:
                continue
        
        return info
    
    def _try_basic_calculations(self, symbol, info):
        """Calculate missing metrics from available data"""
        current_price = info.get('currentPrice', 0)
        if not current_price:
            return info
        
        # Calculate market cap if we have shares outstanding
        if 'marketCap' not in info and 'sharesOutstanding' in info:
            shares = info['sharesOutstanding']
            if shares > 0:
                info['marketCap'] = shares * current_price
        
        # Calculate P/E from EPS if available
        if 'trailingPE' not in info and 'trailingEps' in info:
            eps = info['trailingEps']
            if eps > 0:
                info['trailingPE'] = current_price / eps
        
        # Calculate EPS from P/E if available
        if 'trailingEps' not in info and 'trailingPE' in info:
            pe = info['trailingPE']
            if pe > 0:
                info['trailingEps'] = current_price / pe
        
        # Calculate book value from P/B ratio
        if 'bookValue' not in info and 'priceToBook' in info:
            pb = info['priceToBook']
            if pb > 0:
                info['bookValue'] = current_price / pb
        
        # Calculate P/B from book value
        if 'priceToBook' not in info and 'bookValue' in info:
            bv = info['bookValue']
            if bv > 0:
                info['priceToBook'] = current_price / bv
        
        return info
    
    def _try_web_scraping_for_fundamentals(self, symbol, info):
        """Try to extract real fundamental data from Yahoo Finance web pages"""
        try:
            # Try the main quote page and key statistics page
            pages_to_try = [
                f"https://finance.yahoo.com/quote/{symbol}",
                f"https://finance.yahoo.com/quote/{symbol}/key-statistics"
            ]
            
            for url in pages_to_try:
                try:
                    response = self.session.get(url, timeout=10)
                    if response.status_code != 200:
                        continue
                    
                    html = response.text
                    
                    # Extract fundamental data using multiple approaches
                    extracted_data = self._extract_fundamentals_from_html(html)
                    
                    # Merge any real data found
                    for key, value in extracted_data.items():
                        if value is not None and value != 0 and key not in info:
                            info[key] = value
                    
                    # If we found substantial fundamental data, return it
                    fundamental_count = sum(1 for key in ['trailingPE', 'priceToBook', 'marketCap', 'dividendYield'] 
                                          if info.get(key) is not None and info.get(key) != 0)
                    if fundamental_count >= 2:
                        break
                        
                except Exception as e:
                    continue
            
            return info
            
        except Exception as e:
            return info
    
    def _extract_fundamentals_from_html(self, html):
        """Extract fundamental metrics from HTML using various patterns"""
        import re
        import json
        
        fundamentals = {}
        
        # Method 1: Look for JSON data embedded in the HTML
        json_patterns = [
            r'root\.App\.main\s*=\s*(\{.*?\});',
            r'"QuoteSummaryStore":\s*(\{.*?"summaryDetail"[^}]*\})',
            r'"defaultKeyStatistics":\s*(\{.*?\})',
            r'"summaryDetail":\s*(\{.*?\})',
            r'"financialData":\s*(\{.*?\})'
        ]
        
        for pattern in json_patterns:
            matches = re.finditer(pattern, html, re.DOTALL)
            for match in matches:
                try:
                    json_str = match.group(1)
                    # Try to parse as JSON
                    data = json.loads(json_str)
                    extracted = self._extract_from_json_recursive(data)
                    fundamentals.update(extracted)
                except (json.JSONDecodeError, ValueError):
                    continue
        
        # Method 2: Look for specific patterns in visible text
        text_patterns = {
            'trailingPE': [
                r'P/E\s*(?:Ratio)?\s*(?:\(ttm\))?\s*</?\w*>\s*([0-9.,]+)',
                r'Trailing P/E.*?([0-9.,]+)',
                r'PE.*?([0-9.,]+)',
                r'pe-ratio[^>]*>([0-9.,]+)'
            ],
            'forwardPE': [
                r'Forward P/E.*?([0-9.,]+)',
                r'Forward PE.*?([0-9.,]+)'
            ],
            'priceToBook': [
                r'Price/Book.*?([0-9.,]+)',
                r'P/B.*?([0-9.,]+)',
                r'Book.*?([0-9.,]+)'
            ],
            'marketCap': [
                r'Market Cap.*?\$([0-9.,KMBT]+)',
                r'Market Capitalization.*?\$([0-9.,KMBT]+)',
                r'Mkt Cap.*?\$([0-9.,KMBT]+)'
            ],
            'dividendYield': [
                r'Dividend.*?Yield.*?([0-9.,]+)%',
                r'Yield.*?([0-9.,]+)%',
                r'dividend.*?([0-9.,]+)%'
            ]
        }
        
        for metric, patterns in text_patterns.items():
            if metric in fundamentals:  # Skip if already found
                continue
                
            for pattern in patterns:
                matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)
                for match in matches:
                    try:
                        value_str = match.replace(',', '')
                        
                        # Handle market cap suffixes
                        if metric == 'marketCap':
                            if value_str.endswith('K'):
                                value = float(value_str[:-1]) * 1000
                            elif value_str.endswith('M'):
                                value = float(value_str[:-1]) * 1000000
                            elif value_str.endswith('B'):
                                value = float(value_str[:-1]) * 1000000000
                            elif value_str.endswith('T'):
                                value = float(value_str[:-1]) * 1000000000000
                            else:
                                value = float(value_str)
                        elif metric == 'dividendYield':
                            value = float(value_str) / 100  # Convert percentage to decimal
                        else:
                            value = float(value_str)
                        
                        # Sanity check the values
                        if metric == 'trailingPE' and 1 <= value <= 1000:
                            fundamentals[metric] = value
                            break
                        elif metric == 'priceToBook' and 0.1 <= value <= 100:
                            fundamentals[metric] = value
                            break
                        elif metric == 'marketCap' and value > 1000000:  # At least $1M
                            fundamentals[metric] = value
                            break
                        elif metric == 'dividendYield' and 0 <= value <= 0.2:  # 0-20%
                            fundamentals[metric] = value
                            break
                        elif metric == 'forwardPE' and 1 <= value <= 1000:
                            fundamentals[metric] = value
                            break
                            
                    except (ValueError, AttributeError):
                        continue
        
        return fundamentals
    
    def _extract_from_json_recursive(self, data, fundamentals=None):
        """Recursively extract financial metrics from JSON data"""
        if fundamentals is None:
            fundamentals = {}
        
        if isinstance(data, dict):
            # Look for direct metrics
            target_metrics = {
                'trailingPE': ['trailingPE', 'trailingPe'],
                'forwardPE': ['forwardPE', 'forwardPe'], 
                'priceToBook': ['priceToBook', 'priceToBookRatio'],
                'marketCap': ['marketCap', 'marketCapitalization'],
                'dividendYield': ['dividendYield', 'yield'],
                'trailingEps': ['trailingEps', 'epsTrailingTwelveMonths']
            }
            
            for our_key, possible_keys in target_metrics.items():
                if our_key in fundamentals:  # Already found
                    continue
                    
                for key in possible_keys:
                    if key in data:
                        value = data[key]
                        # Handle nested objects with 'raw' field
                        if isinstance(value, dict) and 'raw' in value:
                            value = value['raw']
                        
                        if value is not None and isinstance(value, (int, float)) and value != 0:
                            fundamentals[our_key] = value
                            break
            
            # Recurse into nested objects
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    self._extract_from_json_recursive(value, fundamentals)
        
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list)):
                    self._extract_from_json_recursive(item, fundamentals)
        
        return fundamentals
    
    def _add_intelligent_estimates(self, symbol, info):
        """Add intelligent estimates only as final fallback"""
        current_price = info.get('currentPrice', 0)
        if not current_price:
            return info
        
        # Only add estimates for missing critical metrics
        if 'trailingPE' not in info or info.get('trailingPE', 0) <= 0:
            info['trailingPE'] = self._estimate_pe_ratio(symbol, current_price)
        
        if 'priceToBook' not in info or info.get('priceToBook', 0) <= 0:
            info['priceToBook'] = self._estimate_pb_ratio(symbol, current_price)
        
        if 'dividendYield' not in info or info.get('dividendYield', 0) <= 0:
            info['dividendYield'] = self._estimate_dividend_yield(symbol)
        
        # Estimate shares outstanding for market cap calculation
        if 'sharesOutstanding' not in info or info.get('sharesOutstanding', 0) <= 0:
            info['sharesOutstanding'] = self._estimate_shares_outstanding(symbol, current_price)
        
        # Calculate market cap from estimated shares
        if 'marketCap' not in info or info.get('marketCap', 0) <= 0:
            shares = info.get('sharesOutstanding', 0)
            if shares > 0:
                info['marketCap'] = shares * current_price
        
        # Calculate derived metrics
        if 'trailingEps' not in info or info.get('trailingEps', 0) <= 0:
            pe = info.get('trailingPE', 0)
            if pe > 0:
                info['trailingEps'] = current_price / pe
        
        if 'bookValue' not in info or info.get('bookValue', 0) <= 0:
            pb = info.get('priceToBook', 0)
            if pb > 0:
                info['bookValue'] = current_price / pb
        
        if 'forwardPE' not in info or info.get('forwardPE', 0) <= 0:
            trailing_pe = info.get('trailingPE', 0)
            if trailing_pe > 0:
                info['forwardPE'] = trailing_pe * 0.9
        
        # Add industry for analysis
        if 'industry' not in info:
            info['industry'] = 'Technology'
        
        return info
    
    def _estimate_shares_outstanding(self, symbol, current_price):
        """Estimate shares outstanding for major companies"""
        symbol = symbol.upper()
        
        # Known approximate shares for major companies (in billions)
        known_shares = {
            'AAPL': 15.5,
            'MSFT': 7.4, 
            'GOOGL': 12.8,
            'GOOG': 12.8,
            'AMZN': 10.6,
            'TSLA': 3.2,
            'NVDA': 2.5,
            'META': 2.6,
            'NFLX': 0.44,
            'JPM': 2.9,
            'BAC': 8.2,
            'JNJ': 2.4,
            'PG': 2.4,
            'KO': 4.3,
            'WMT': 2.7,
            'V': 2.1,
            'MA': 1.0
        }
        
        if symbol in known_shares:
            return known_shares[symbol] * 1000000000  # Convert to actual shares
        
        # Generic estimate based on stock price
        if current_price > 500:
            return 1000000000  # 1B shares for very high price stocks
        elif current_price > 200:
            return 3000000000  # 3B shares
        elif current_price > 100:
            return 5000000000  # 5B shares  
        elif current_price > 50:
            return 8000000000  # 8B shares
        else:
            return 15000000000  # 15B shares for lower price stocks
    
    def _try_web_scraping_approach(self, symbol, quote):
        """Fallback web scraping approach for fundamental data"""
        try:
            # Try multiple Yahoo Finance pages for comprehensive data
            pages_to_try = [
                f"https://finance.yahoo.com/quote/{symbol}",  # Main quote page
                f"https://finance.yahoo.com/quote/{symbol}/key-statistics",  # Key stats
                f"https://finance.yahoo.com/quote/{symbol}/analysis"  # Analysis page
            ]
            
            info = quote.copy()
            
            for url in pages_to_try:
                try:
                    response = self.session.get(url, timeout=10)
                    if response.status_code != 200:
                        continue
                    
                    html = response.text
                    
                    # Extract key metrics using multiple approaches
                    import re
                    import json
                    
                    # Approach 1: JSON data extraction
                    json_patterns = [
                        r'root\.App\.main\s*=\s*(\{.*?\});',
                        r'"QuoteSummaryStore":\s*(\{.*?"price":\{.*?\})',
                        r'"summaryDetail":\s*(\{.*?\})',
                        r'"defaultKeyStatistics":\s*(\{.*?\})'
                    ]
                    
                    for pattern in json_patterns:
                        matches = re.finditer(pattern, html)
                        for match in matches:
                            try:
                                json_str = match.group(1)
                                if json_str.count('{') > json_str.count('}'):
                                    # Try to balance braces
                                    brace_diff = json_str.count('{') - json_str.count('}')
                                    json_str += '}' * brace_diff
                                
                                json_data = json.loads(json_str)
                                extracted_info = self._extract_from_json(json_data, {})
                                
                                # Merge any new data found
                                for key, value in extracted_info.items():
                                    if key not in info and value is not None:
                                        info[key] = value
                                        
                            except (json.JSONDecodeError, ValueError):
                                continue
                    
                    # Approach 2: Enhanced HTML text extraction
                    new_info = self._extract_from_html_text(html, info)
                    
                    # Merge any new data
                    for key, value in new_info.items():
                        if key not in info and value is not None:
                            info[key] = value
                    
                    # Approach 3: Table-based extraction for key statistics page
                    if 'key-statistics' in url:
                        table_info = self._extract_from_statistics_table(html)
                        for key, value in table_info.items():
                            if key not in info and value is not None:
                                info[key] = value
                    
                    # If we found substantial data, we can break
                    if len(info) > len(quote) + 5:
                        break
                        
                except Exception as e:
                    continue
            
            # Calculate Market Cap if missing but have shares and price
            if 'marketCap' not in info and 'sharesOutstanding' in info and 'currentPrice' in info:
                try:
                    info['marketCap'] = info['sharesOutstanding'] * info['currentPrice']
                except:
                    pass
            
            # Estimate missing data from available data
            if 'trailingPE' not in info and 'currentPrice' in info and 'trailingEps' in info:
                try:
                    if info['trailingEps'] > 0:
                        info['trailingPE'] = info['currentPrice'] / info['trailingEps']
                except:
                    pass
            
            # Add basic estimates for missing critical data to enable analysis
            if 'industry' not in info:
                info['industry'] = 'Technology'  # Default for many stocks
            
            # Estimate market cap using shares * price if we have current price
            if 'marketCap' not in info and 'currentPrice' in info:
                # Use typical shares outstanding for major companies as rough estimate
                if symbol.upper() in ['AAPL']:
                    info['sharesOutstanding'] = 15500000000  # Approximate AAPL shares
                elif symbol.upper() in ['MSFT']:
                    info['sharesOutstanding'] = 7400000000   # Approximate MSFT shares
                elif symbol.upper() in ['GOOGL', 'GOOG']:
                    info['sharesOutstanding'] = 12800000000  # Approximate GOOGL shares
                elif symbol.upper() in ['AMZN']:
                    info['sharesOutstanding'] = 10600000000  # Approximate AMZN shares
                elif symbol.upper() in ['TSLA']:
                    info['sharesOutstanding'] = 3200000000   # Approximate TSLA shares
                else:
                    # Generic estimate based on price range
                    if info['currentPrice'] > 100:
                        info['sharesOutstanding'] = 5000000000  # High price stocks
                    else:
                        info['sharesOutstanding'] = 10000000000  # Lower price stocks
                
                if 'sharesOutstanding' in info:
                    info['marketCap'] = info['sharesOutstanding'] * info['currentPrice']
            
            # Estimate stock-specific ratios based on company characteristics
            if 'trailingPE' not in info and 'currentPrice' in info:
                info['trailingPE'] = self._estimate_pe_ratio(symbol, info['currentPrice'])
            
            if 'forwardPE' not in info and 'trailingPE' in info:
                info['forwardPE'] = info['trailingPE'] * 0.9  # Slightly lower forward P/E
            
            if 'priceToBook' not in info:
                info['priceToBook'] = self._estimate_pb_ratio(symbol, info.get('currentPrice', 0))
            
            if 'trailingEps' not in info and 'currentPrice' in info and 'trailingPE' in info:
                if info['trailingPE'] > 0:
                    info['trailingEps'] = info['currentPrice'] / info['trailingPE']
            
            if 'bookValue' not in info and 'currentPrice' in info and 'priceToBook' in info:
                if info['priceToBook'] > 0:
                    info['bookValue'] = info['currentPrice'] / info['priceToBook']
            
            # Add more realistic dividend yield estimates
            if 'dividendYield' not in info:
                info['dividendYield'] = self._estimate_dividend_yield(symbol)
            
            return info
            
        except Exception as e:
            print(f"Web scraping failed for {symbol}: {e}")
            return quote
    
    def _extract_from_json(self, json_data, info):
        """Extract financial data from JSON structure"""
        def search_nested(obj, keys_found=None):
            if keys_found is None:
                keys_found = {}
            
            if isinstance(obj, dict):
                for key, value in obj.items():
                    # Look for financial metrics
                    if key in ['marketCap', 'trailingPE', 'forwardPE', 'priceToBook', 
                              'trailingEps', 'bookValue', 'sharesOutstanding', 
                              'dividendYield', 'totalRevenue']:
                        if isinstance(value, dict) and 'raw' in value:
                            keys_found[key] = value['raw']
                        elif isinstance(value, (int, float)):
                            keys_found[key] = value
                    
                    # Recurse into nested objects
                    if isinstance(value, (dict, list)):
                        search_nested(value, keys_found)
            
            elif isinstance(obj, list):
                for item in obj:
                    if isinstance(item, (dict, list)):
                        search_nested(item, keys_found)
            
            return keys_found
        
        financial_data = search_nested(json_data)
        info.update(financial_data)
        return info
    
    def _extract_from_html_text(self, html, info):
        """Extract financial data from HTML text patterns"""
        import re
        
        # Look for table-like patterns in the HTML
        patterns = {
            'marketCap': [
                r'Market Cap[^>]*>([0-9,.KMBT]+)',
                r'market-cap[^>]*>([0-9,.KMBT]+)',
                r'>Market Cap</.*?>([0-9,.KMBT]+)'
            ],
            'trailingPE': [
                r'P/E Ratio[^>]*>([0-9,.]+)',
                r'pe-ratio[^>]*>([0-9,.]+)', 
                r'>PE Ratio</.*?>([0-9,.]+)'
            ],
            'priceToBook': [
                r'Price/Book[^>]*>([0-9,.]+)',
                r'price-book[^>]*>([0-9,.]+)',
                r'>Price to Book</.*?>([0-9,.]+)'
            ]
        }
        
        for metric, pattern_list in patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
                if match:
                    try:
                        value_str = match.group(1).replace(',', '')
                        # Handle K, M, B, T suffixes
                        if value_str.endswith('K'):
                            info[metric] = float(value_str[:-1]) * 1000
                        elif value_str.endswith('M'):
                            info[metric] = float(value_str[:-1]) * 1000000
                        elif value_str.endswith('B'):
                            info[metric] = float(value_str[:-1]) * 1000000000
                        elif value_str.endswith('T'):
                            info[metric] = float(value_str[:-1]) * 1000000000000
                        else:
                            info[metric] = float(value_str)
                        break  # Found a match, move to next metric
                    except ValueError:
                        continue
        
        return info
    
    def _extract_from_statistics_table(self, html):
        """Extract data from Yahoo Finance statistics tables"""
        import re
        
        info = {}
        
        # Enhanced patterns for key statistics
        stat_patterns = {
            'marketCap': [
                r'Market Cap[^>]*>[^>]*>([0-9.,KMBT]+)',
                r'Market\s+Cap.*?([0-9.,KMBT]+)',
                r'market-cap[^>]*>([0-9.,KMBT]+)'
            ],
            'trailingPE': [
                r'Trailing P/E[^>]*>[^>]*>([0-9.,\-]+)',
                r'P/E\s+Ratio[^>]*>[^>]*>([0-9.,\-]+)',
                r'trailing.*pe[^>]*>([0-9.,\-]+)'
            ],
            'forwardPE': [
                r'Forward P/E[^>]*>[^>]*>([0-9.,\-]+)',
                r'forward.*pe[^>]*>([0-9.,\-]+)'
            ],
            'priceToBook': [
                r'Price/Book[^>]*>[^>]*>([0-9.,\-]+)',
                r'P/B\s+Ratio[^>]*>[^>]*>([0-9.,\-]+)',
                r'price.*book[^>]*>([0-9.,\-]+)'
            ],
            'epsTrailingTwelveMonths': [
                r'Diluted EPS[^>]*>[^>]*>([0-9.,\-]+)',
                r'EPS[^>]*>[^>]*>([0-9.,\-]+)',
                r'earnings.*share[^>]*>([0-9.,\-]+)'
            ],
            'bookValue': [
                r'Book Value[^>]*>[^>]*>([0-9.,\-]+)',
                r'book.*value[^>]*>([0-9.,\-]+)'
            ],
            'sharesOutstanding': [
                r'Shares Outstanding[^>]*>[^>]*>([0-9.,KMBT]+)',
                r'shares.*outstanding[^>]*>([0-9.,KMBT]+)'
            ],
            'dividendYield': [
                r'Forward Annual Dividend Yield[^>]*>[^>]*>([0-9.,\-]+%?)',
                r'Dividend.*Yield[^>]*>[^>]*>([0-9.,\-]+%?)',
                r'dividend.*yield[^>]*>([0-9.,\-]+%?)'
            ]
        }
        
        for metric, patterns in stat_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)
                for match in matches:
                    try:
                        value_str = match.strip().replace(',', '').replace('%', '')
                        
                        # Skip invalid values
                        if value_str in ['N/A', '--', '-', '']:
                            continue
                        
                        # Handle suffixes
                        if value_str.endswith('K'):
                            value = float(value_str[:-1]) * 1000
                        elif value_str.endswith('M'):
                            value = float(value_str[:-1]) * 1000000
                        elif value_str.endswith('B'):
                            value = float(value_str[:-1]) * 1000000000
                        elif value_str.endswith('T'):
                            value = float(value_str[:-1]) * 1000000000000
                        else:
                            value = float(value_str)
                        
                        # Special handling for percentage dividends
                        if metric == 'dividendYield' and match.endswith('%'):
                            value = value / 100
                        
                        if value > 0:  # Only use positive values
                            info[metric] = value
                            break  # Found valid value, move to next metric
                            
                    except (ValueError, AttributeError):
                        continue
        
        return info
    
    def _estimate_pe_ratio(self, symbol, current_price):
        """Estimate realistic P/E ratio based on company and price characteristics"""
        symbol = symbol.upper()
        
        # Company-specific P/E estimates based on known characteristics
        company_pe_estimates = {
            'AAPL': 28.5,   # Premium tech valuation
            'MSFT': 32.0,   # High-growth software
            'GOOGL': 24.0,  # Mature tech with growth
            'GOOG': 24.0,   # Same as GOOGL
            'AMZN': 45.0,   # High-growth e-commerce
            'TSLA': 55.0,   # High-growth EV
            'NVDA': 65.0,   # AI/chip growth premium
            'META': 22.0,   # Social media mature
            'NFLX': 35.0,   # Streaming growth
            'CRM': 45.0,    # SaaS growth
            'ADBE': 40.0,   # Software growth
            'ORCL': 18.0,   # Mature enterprise software
            'IBM': 15.0,    # Legacy tech
            'JPM': 12.0,    # Banking sector
            'BAC': 11.0,    # Banking sector
            'WFC': 10.0,    # Banking sector
            'JNJ': 16.0,    # Healthcare stable
            'PFE': 14.0,    # Pharma
            'KO': 25.0,     # Consumer staples premium
            'PG': 24.0,     # Consumer goods premium
            'WMT': 26.0,    # Retail defensive
            'DIS': 28.0,    # Entertainment/media
            'V': 32.0,      # Payment networks premium
            'MA': 31.0,     # Payment networks premium
        }
        
        if symbol in company_pe_estimates:
            return company_pe_estimates[symbol]
        
        # Industry-based estimates for unknown stocks
        if current_price > 300:
            return 35.0  # High-price premium stocks
        elif current_price > 150:
            return 28.0  # Mid-high price stocks
        elif current_price > 50:
            return 22.0  # Mid-price stocks
        else:
            return 18.0  # Lower price stocks
    
    def _estimate_pb_ratio(self, symbol, current_price):
        """Estimate realistic P/B ratio based on company characteristics"""
        symbol = symbol.upper()
        
        # Company-specific P/B estimates
        company_pb_estimates = {
            'AAPL': 45.0,   # Asset-light tech
            'MSFT': 12.0,   # Software/cloud
            'GOOGL': 6.5,   # Tech with some assets
            'GOOG': 6.5,    # Same as GOOGL
            'AMZN': 8.0,    # E-commerce/cloud
            'TSLA': 12.0,   # Manufacturing premium
            'NVDA': 22.0,   # Chip design premium
            'META': 6.8,    # Social media
            'NFLX': 4.5,    # Content/streaming
            'JPM': 1.8,     # Banking typical
            'BAC': 1.4,     # Banking typical
            'WFC': 1.2,     # Banking typical
            'JNJ': 5.5,     # Healthcare
            'PFE': 3.2,     # Pharma
            'KO': 10.0,     # Brand premium
            'PG': 7.5,      # Consumer brands
            'WMT': 5.2,     # Retail
            'DIS': 2.8,     # Entertainment/assets
            'V': 17.0,      # Payment networks
            'MA': 15.0,     # Payment networks
        }
        
        if symbol in company_pb_estimates:
            return company_pb_estimates[symbol]
        
        # Generic estimates based on price range (rough industry proxy)
        if current_price > 200:
            return 8.0   # Likely growth/tech
        elif current_price > 100:
            return 5.0   # Mixed industries
        elif current_price > 50:
            return 3.5   # Traditional industries
        else:
            return 2.0   # Value/cyclical stocks
    
    def _estimate_dividend_yield(self, symbol):
        """Estimate dividend yield based on company type"""
        symbol = symbol.upper()
        
        # Company-specific dividend yield estimates
        dividend_yields = {
            'AAPL': 0.0047,  # 0.47%
            'MSFT': 0.0068,  # 0.68%
            'GOOGL': 0.0,    # No dividend
            'GOOG': 0.0,     # No dividend
            'AMZN': 0.0,     # No dividend
            'TSLA': 0.0,     # No dividend
            'NVDA': 0.0035,  # 0.35%
            'META': 0.0,     # No dividend
            'NFLX': 0.0,     # No dividend
            'JPM': 0.025,    # 2.5%
            'BAC': 0.028,    # 2.8%
            'WFC': 0.032,    # 3.2%
            'JNJ': 0.030,    # 3.0%
            'PFE': 0.055,    # 5.5%
            'KO': 0.031,     # 3.1%
            'PG': 0.024,     # 2.4%
            'WMT': 0.030,    # 3.0%
            'DIS': 0.0,      # Suspended
            'V': 0.0075,     # 0.75%
            'MA': 0.0055,    # 0.55%
        }
        
        return dividend_yields.get(symbol, 0.015)  # 1.5% default
    
    def get_analyst_recommendations(self, symbol):
        """Get analyst recommendations and target price from real sources"""
        analyst_data = {}
        
        # Try API endpoints first
        api_endpoints = [
            f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/{symbol}?modules=upgradeDowngradeHistory,financialData",
            f"https://query1.finance.yahoo.com/v7/finance/options/{symbol}"
        ]
        
        for url in api_endpoints:
            try:
                data = self._make_request(url)
                if data and 'quoteSummary' in data:
                    result = data['quoteSummary']['result']
                    if result and len(result) > 0:
                        if 'financialData' in result[0]:
                            financial_data = result[0]['financialData']
                            if 'targetMeanPrice' in financial_data:
                                target_price = financial_data['targetMeanPrice']
                                if isinstance(target_price, dict) and 'raw' in target_price:
                                    analyst_data['targetMeanPrice'] = target_price['raw']
                            if 'recommendationMean' in financial_data:
                                rec_mean = financial_data['recommendationMean']
                                if isinstance(rec_mean, dict) and 'raw' in rec_mean:
                                    analyst_data['recommendationMean'] = rec_mean['raw']
                            if 'numberOfAnalystOpinions' in financial_data:
                                num_analysts = financial_data['numberOfAnalystOpinions']
                                if isinstance(num_analysts, dict) and 'raw' in num_analysts:
                                    analyst_data['numberOfAnalysts'] = num_analysts['raw']
                        
                        if 'upgradeDowngradeHistory' in result[0]:
                            upgrade_data = result[0]['upgradeDowngradeHistory']
                            if 'history' in upgrade_data:
                                analyst_data['recentChanges'] = upgrade_data['history'][:5]
                        
                        if analyst_data:  # If we got some data, return it
                            return analyst_data
            except Exception as e:
                continue
        
        # If API fails, try web scraping the main Yahoo Finance page
        if not analyst_data:
            analyst_data = self._scrape_analyst_data_from_web(symbol)
        
        return analyst_data
    
    def _scrape_analyst_data_from_web(self, symbol):
        """Scrape analyst data from Yahoo Finance web page"""
        try:
            url = f"https://finance.yahoo.com/quote/{symbol}"
            response = self.session.get(url, timeout=15)
            
            if response.status_code != 200:
                return {}
            
            html = response.text
            analyst_data = {}
            
            import re
            
            # Look for analyst recommendation data in the HTML
            # Yahoo Finance often embeds this in JSON within script tags
            json_patterns = [
                r'\"recommendationTrend\":\s*\{[^}]*\"trend\":\s*\[([^\]]+)\]',
                r'\"financialData\":\s*\{[^}]*\"targetMeanPrice\":\s*\{[^}]*\"raw\":\s*([0-9.]+)',
                r'\"financialData\":\s*\{[^}]*\"recommendationMean\":\s*\{[^}]*\"raw\":\s*([0-9.]+)',
                r'\"financialData\":\s*\{[^}]*\"numberOfAnalystOpinions\":\s*\{[^}]*\"raw\":\s*([0-9]+)'
            ]
            
            # Look for target price
            target_patterns = [
                r'Price Target.*?\$([0-9,.]+)',
                r'Target.*?\$([0-9,.]+)',
                r'target.*?price.*?\$([0-9,.]+)',
                r'\"targetMeanPrice\"[^}]*\"raw\":\s*([0-9.]+)'
            ]
            
            for pattern in target_patterns:
                match = re.search(pattern, html, re.IGNORECASE)
                if match:
                    try:
                        target_price = float(match.group(1).replace(',', ''))
                        analyst_data['targetMeanPrice'] = target_price
                        break
                    except ValueError:
                        continue
            
            # Look for recommendation mean
            rec_patterns = [
                r'\"recommendationMean\"[^}]*\"raw\":\s*([0-9.]+)',
                r'recommendation.*?([0-9.]+)',
                r'\"recommendation\":\s*([0-9.]+)'
            ]
            
            for pattern in rec_patterns:
                match = re.search(pattern, html, re.IGNORECASE)
                if match:
                    try:
                        rec_mean = float(match.group(1))
                        analyst_data['recommendationMean'] = rec_mean
                        break
                    except ValueError:
                        continue
            
            # Look for number of analysts
            analyst_count_patterns = [
                r'\"numberOfAnalystOpinions\"[^}]*\"raw\":\s*([0-9]+)',
                r'([0-9]+)\s*analyst',
                r'analyst.*?([0-9]+)',
                r'\"numBrokerStocksRecommendations\":\s*([0-9]+)'
            ]
            
            for pattern in analyst_count_patterns:
                matches = re.findall(pattern, html, re.IGNORECASE)
                for match in matches:
                    try:
                        num_analysts = int(match)
                        if 1 <= num_analysts <= 100:  # Reasonable range
                            analyst_data['numberOfAnalysts'] = num_analysts
                            break
                    except ValueError:
                        continue
                if 'numberOfAnalysts' in analyst_data:
                    break
            
            return analyst_data
            
        except Exception as e:
            print(f"Web scraping analyst data failed for {symbol}: {e}")
            return {}
    
    def _estimate_analyst_data(self, symbol):
        """Provide estimated analyst recommendations when API data is unavailable"""
        # Get current quote to base estimates on
        quote = self.get_quote(symbol)
        if not quote:
            return {}
        
        current_price = quote.get('currentPrice', 0)
        if not current_price:
            return {}
        
        # Company-specific target price and recommendation estimates
        symbol_upper = symbol.upper()
        
        # More realistic company-specific estimates
        company_targets = {
            'AAPL': {'target_multiplier': 1.15, 'rec_mean': 2.1, 'analysts': 35},  # 15% upside, Strong Buy
            'MSFT': {'target_multiplier': 1.18, 'rec_mean': 2.0, 'analysts': 40},  # 18% upside, Buy
            'GOOGL': {'target_multiplier': 1.22, 'rec_mean': 2.2, 'analysts': 32},  # 22% upside, Buy
            'GOOG': {'target_multiplier': 1.22, 'rec_mean': 2.2, 'analysts': 32},   # Same as GOOGL
            'AMZN': {'target_multiplier': 1.25, 'rec_mean': 2.3, 'analysts': 38},   # 25% upside, Buy
            'TSLA': {'target_multiplier': 1.08, 'rec_mean': 2.8, 'analysts': 28},   # 8% upside, Hold (volatile)
            'NVDA': {'target_multiplier': 1.12, 'rec_mean': 2.4, 'analysts': 30},   # 12% upside, Buy
            'META': {'target_multiplier': 1.20, 'rec_mean': 2.1, 'analysts': 35},   # 20% upside, Buy
            'NFLX': {'target_multiplier': 1.16, 'rec_mean': 2.5, 'analysts': 25},   # 16% upside, Hold
            'JPM': {'target_multiplier': 1.10, 'rec_mean': 2.4, 'analysts': 22},    # 10% upside, Hold
            'BAC': {'target_multiplier': 1.08, 'rec_mean': 2.6, 'analysts': 20},    # 8% upside, Hold
            'JNJ': {'target_multiplier': 1.05, 'rec_mean': 2.3, 'analysts': 18},    # 5% upside, Buy
            'PFE': {'target_multiplier': 1.12, 'rec_mean': 2.4, 'analysts': 16},    # 12% upside, Hold
            'KO': {'target_multiplier': 1.06, 'rec_mean': 2.5, 'analysts': 15},     # 6% upside, Hold
            'PG': {'target_multiplier': 1.04, 'rec_mean': 2.4, 'analysts': 17},     # 4% upside, Hold
            'WMT': {'target_multiplier': 1.08, 'rec_mean': 2.3, 'analysts': 20},    # 8% upside, Buy
            'DIS': {'target_multiplier': 1.18, 'rec_mean': 2.6, 'analysts': 22},    # 18% upside, Hold
            'V': {'target_multiplier': 1.12, 'rec_mean': 2.1, 'analysts': 25},      # 12% upside, Buy
            'MA': {'target_multiplier': 1.11, 'rec_mean': 2.2, 'analysts': 24},     # 11% upside, Buy
        }
        
        if symbol_upper in company_targets:
            data = company_targets[symbol_upper]
            estimated_target = current_price * data['target_multiplier']
            rec_mean = data['rec_mean']
            num_analysts = data['analysts']
        else:
            # Generic estimates based on stock price (as proxy for company size/type)
            if current_price > 300:
                estimated_target = current_price * 1.14  # 14% upside for high-price stocks
                rec_mean = 2.3  # Buy
                num_analysts = 25
            elif current_price > 100:
                estimated_target = current_price * 1.12  # 12% upside
                rec_mean = 2.4  # Buy-Hold
                num_analysts = 20
            elif current_price > 50:
                estimated_target = current_price * 1.10  # 10% upside
                rec_mean = 2.6  # Hold
                num_analysts = 15
            else:
                estimated_target = current_price * 1.08  # 8% upside for smaller stocks
                rec_mean = 2.7  # Hold
                num_analysts = 12
        
        return {
            'targetMeanPrice': estimated_target,
            'recommendationMean': rec_mean,
            'numberOfAnalysts': num_analysts,
            'estimated': True  # Flag to indicate this is estimated data
        }
    
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