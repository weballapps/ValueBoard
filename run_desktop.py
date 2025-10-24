#!/usr/bin/env python3
"""
Simple desktop launcher for Value Investment Dashboard
Easier alternative to building standalone executables
"""

import subprocess
import sys
import os
import webbrowser
import time
import signal
import platform

def check_python():
    """Check if Python is available"""
    try:
        version = sys.version_info
        if version.major >= 3 and version.minor >= 8:
            print(f"✅ Python {version.major}.{version.minor}.{version.micro} found")
            return True
        else:
            print(f"❌ Python {version.major}.{version.minor} found, but Python 3.8+ required")
            return False
    except:
        print("❌ Python not found")
        return False

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✅ All packages installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install requirements")
        print("💡 Try running: pip install -r requirements.txt")
        return False

def find_free_port():
    """Find a free port for Streamlit"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

def start_streamlit():
    """Start Streamlit application"""
    port = find_free_port()
    url = f"http://localhost:{port}"
    
    print(f"🚀 Starting Value Investment Dashboard...")
    print(f"📊 Opening dashboard at: {url}")
    print("⏹️  To stop the application, close this window or press Ctrl+C")
    print("=" * 60)
    
    # Start Streamlit in background
    streamlit_process = subprocess.Popen([
        sys.executable, '-m', 'streamlit', 'run', 
        'stock_value_dashboard.py',
        '--server.port', str(port),
        '--server.headless', 'true',
        '--server.enableCORS', 'false',
        '--server.enableXsrfProtection', 'false',
        '--browser.gatherUsageStats', 'false'
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Wait a moment for Streamlit to start
    time.sleep(3)
    
    # Open browser
    try:
        webbrowser.open(url)
        print("✅ Dashboard opened in your browser")
    except:
        print(f"🌐 Please open your browser and go to: {url}")
    
    # Handle shutdown gracefully
    def signal_handler(sig, frame):
        print("\n⏹️  Shutting down dashboard...")
        streamlit_process.terminate()
        try:
            streamlit_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            streamlit_process.kill()
        print("✅ Dashboard stopped")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    if platform.system() != 'Windows':
        signal.signal(signal.SIGTERM, signal_handler)
    
    # Keep running until interrupted
    try:
        streamlit_process.wait()
    except KeyboardInterrupt:
        signal_handler(None, None)

def main():
    """Main launcher function"""
    print("🖥️  Value Investment Dashboard - Desktop Launcher")
    print("=" * 55)
    
    # Check if we're in the right directory
    if not os.path.exists('stock_value_dashboard.py'):
        print("❌ stock_value_dashboard.py not found!")
        print("💡 Please run this script from the project directory")
        input("Press Enter to exit...")
        return
    
    # Check Python version
    if not check_python():
        input("Press Enter to exit...")
        return
    
    # Install requirements
    if not install_requirements():
        input("Press Enter to exit...")
        return
    
    # Start the application
    try:
        start_streamlit()
    except Exception as e:
        print(f"❌ Failed to start dashboard: {e}")
        input("Press Enter to exit...")

if __name__ == '__main__':
    main()