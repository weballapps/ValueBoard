#!/usr/bin/env python3
"""
Analyze Yahoo Finance HTML structure to find financial data
"""

import requests
import re
import json

def analyze_yahoo_page(symbol='AAPL'):
    """Analyze Yahoo Finance page structure"""
    print(f"🔍 Analyzing Yahoo Finance page for {symbol}...")
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    
    url = f"https://finance.yahoo.com/quote/{symbol}"
    response = session.get(url, timeout=15)
    
    if response.status_code != 200:
        print(f"❌ Failed to fetch page: {response.status_code}")
        return
    
    html = response.text
    print(f"✅ Fetched {len(html)} characters")
    
    # Look for common financial data patterns
    print("\n🔍 Searching for financial data patterns...")
    
    # Pattern 1: Look for any mention of financial terms
    financial_terms = ['marketCap', 'Market Cap', 'P/E', 'trailingPE', 'forwardPE', 'priceToBook']
    for term in financial_terms:
        matches = re.findall(f'.*{term}.*', html, re.IGNORECASE)
        if matches:
            print(f"✅ Found {len(matches)} matches for '{term}'")
            # Show first 2 matches
            for i, match in enumerate(matches[:2]):
                clean_match = match.strip()[:100]
                print(f"  {i+1}: {clean_match}...")
        else:
            print(f"❌ No matches for '{term}'")
    
    # Pattern 2: Look for JSON data structures
    print("\n📄 Looking for JSON data structures...")
    json_patterns = [
        r'root\.App\.main\s*=\s*(\{.*?\});',
        r'window\.__INITIAL_STATE__\s*=\s*(\{.*?\});',
        r'"context"\s*:\s*(\{.*?\})'
    ]
    
    for i, pattern in enumerate(json_patterns):
        matches = re.findall(pattern, html)
        if matches:
            print(f"✅ Found JSON pattern {i+1}: {len(matches)} matches")
            # Try to parse first match
            try:
                data = json.loads(matches[0])
                print(f"  Successfully parsed JSON with {len(str(data))} characters")
                
                # Look for financial data in the JSON
                financial_keys = find_financial_keys(data)
                if financial_keys:
                    print(f"  Found financial keys: {financial_keys[:5]}...")
                
            except json.JSONDecodeError:
                print(f"  JSON parsing failed for pattern {i+1}")
        else:
            print(f"❌ No matches for JSON pattern {i+1}")
    
    # Pattern 3: Look for table data
    print("\n📊 Looking for table data...")
    table_patterns = [
        r'<td[^>]*>.*?Market Cap.*?</td>.*?<td[^>]*>(.*?)</td>',
        r'<td[^>]*>.*?P/E.*?</td>.*?<td[^>]*>(.*?)</td>',
        r'<span[^>]*>.*?Market Cap.*?</span>.*?<span[^>]*>(.*?)</span>'
    ]
    
    for i, pattern in enumerate(table_patterns):
        matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)
        if matches:
            print(f"✅ Found table pattern {i+1}: {matches[:3]}")
        else:
            print(f"❌ No matches for table pattern {i+1}")

def find_financial_keys(data, path=""):
    """Recursively find financial data keys in JSON"""
    financial_keys = []
    
    if isinstance(data, dict):
        for key, value in data.items():
            current_path = f"{path}.{key}" if path else key
            
            # Check if this key looks financial
            financial_terms = ['market', 'cap', 'pe', 'ratio', 'price', 'book', 'eps', 'revenue', 'dividend']
            if any(term in key.lower() for term in financial_terms):
                financial_keys.append(current_path)
            
            # Recurse into nested structures (but limit depth)
            if isinstance(value, (dict, list)) and len(path.split('.')) < 3:
                financial_keys.extend(find_financial_keys(value, current_path))
    
    elif isinstance(data, list) and len(data) > 0:
        # Check first few items in list
        for i, item in enumerate(data[:3]):
            financial_keys.extend(find_financial_keys(item, f"{path}[{i}]"))
    
    return financial_keys

if __name__ == '__main__':
    analyze_yahoo_page('AAPL')