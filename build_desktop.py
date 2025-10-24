#!/usr/bin/env python3
"""
Desktop builder for Value Investment Dashboard
Creates standalone executable for Windows, Mac, and Linux
"""

import subprocess
import sys
import os
import shutil

def install_requirements():
    """Install required packages for building desktop app"""
    requirements = [
        'streamlit-desktop-app',
        'pyinstaller'
    ]
    
    for package in requirements:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✅ Installed {package}")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")
            return False
    return True

def build_with_streamlit_desktop():
    """Build using streamlit-desktop-app (recommended)"""
    try:
        # Build command
        cmd = [
            'streamlit-desktop-app', 'build', 
            'stock_value_dashboard.py',
            '--name', 'ValueInvestmentDashboard',
            '--onefile'
        ]
        
        # Add icon if available
        if os.path.exists('icon.ico'):
            cmd.extend(['--icon', 'icon.ico'])
        
        print("🔨 Building desktop app with streamlit-desktop-app...")
        subprocess.check_call(cmd)
        print("✅ Desktop app built successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False

def build_with_pyinstaller():
    """Fallback: Build using PyInstaller"""
    try:
        cmd = [
            'pyinstaller',
            '--onefile',
            '--name', 'ValueInvestmentDashboard',
            '--distpath', 'dist',
            '--workpath', 'build',
            '--specpath', 'build',
            'stock_value_dashboard.py'
        ]
        
        # Add icon if available
        if os.path.exists('icon.ico'):
            cmd.extend(['--icon', 'icon.ico'])
        
        print("🔨 Building desktop app with PyInstaller...")
        subprocess.check_call(cmd)
        print("✅ Desktop app built successfully with PyInstaller!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ PyInstaller build failed: {e}")
        return False

def create_installer_script():
    """Create simple installer script for end users"""
    installer_content = '''@echo off
echo Installing Value Investment Dashboard...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8+ first.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python found

REM Install requirements
echo Installing required packages...
pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ Failed to install requirements
    pause
    exit /b 1
)

echo ✅ All packages installed successfully!
echo.
echo 🚀 Starting Value Investment Dashboard...
echo.
echo The app will open in your default web browser.
echo To stop the app, close this window or press Ctrl+C
echo.

REM Start the Streamlit app
streamlit run stock_value_dashboard.py --server.port 8501 --server.headless false

pause
'''
    
    with open('install_and_run.bat', 'w') as f:
        f.write(installer_content)
    
    print("✅ Created install_and_run.bat for easy deployment")

def main():
    """Main build process"""
    print("🏗️  Value Investment Dashboard - Desktop Builder")
    print("=" * 50)
    
    # Check if main file exists
    if not os.path.exists('stock_value_dashboard.py'):
        print("❌ stock_value_dashboard.py not found!")
        return
    
    # Install build requirements
    print("📦 Installing build tools...")
    if not install_requirements():
        print("❌ Failed to install build tools")
        return
    
    # Try streamlit-desktop-app first
    print("\n🔨 Attempting build with streamlit-desktop-app...")
    if build_with_streamlit_desktop():
        print("✅ Build completed successfully!")
    else:
        print("⚠️  streamlit-desktop-app failed, trying PyInstaller...")
        if build_with_pyinstaller():
            print("✅ Build completed with PyInstaller!")
        else:
            print("❌ Both build methods failed")
            print("💡 Creating simple installer script instead...")
            create_installer_script()
            return
    
    # Create simple installer as backup
    create_installer_script()
    
    print("\n🎉 Desktop build process completed!")
    print("\n📁 Output files:")
    if os.path.exists('dist'):
        for file in os.listdir('dist'):
            print(f"   - dist/{file}")
    print("   - install_and_run.bat (simple installer)")
    
    print("\n📋 Distribution options:")
    print("1. Share the .exe file from dist/ folder")
    print("2. Share install_and_run.bat + requirements.txt + .py file")
    print("3. Create GitHub release with both options")

if __name__ == '__main__':
    main()