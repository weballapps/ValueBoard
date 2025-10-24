#!/usr/bin/env python3
"""
PWA (Progressive Web App) creator for Value Investment Dashboard
Makes the Streamlit app installable on mobile devices (Android/iOS)
"""

import json
import os

def create_manifest():
    """Create web app manifest for PWA"""
    manifest = {
        "name": "Value Investment Dashboard",
        "short_name": "ValueBoard",
        "description": "Professional stock analysis and value investment dashboard",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": "#1f77b4",
        "orientation": "portrait-primary",
        "scope": "/",
        "icons": [
            {
                "src": "assets/icon-192.png",
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "any maskable"
            },
            {
                "src": "assets/icon-512.png", 
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "any maskable"
            }
        ],
        "categories": ["finance", "business", "productivity"],
        "screenshots": [
            {
                "src": "assets/screenshot-mobile.png",
                "sizes": "390x844",
                "type": "image/png",
                "form_factor": "narrow"
            },
            {
                "src": "assets/screenshot-desktop.png", 
                "sizes": "1280x720",
                "type": "image/png",
                "form_factor": "wide"
            }
        ]
    }
    
    # Create assets directory
    os.makedirs('.streamlit/static/assets', exist_ok=True)
    
    # Write manifest
    with open('.streamlit/static/manifest.json', 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print("✅ Created manifest.json")

def create_service_worker():
    """Create service worker for offline functionality"""
    service_worker = '''
// Value Investment Dashboard Service Worker
const CACHE_NAME = 'valueboard-v1.0.0';
const urlsToCache = [
  '/',
  '/manifest.json',
  '/assets/icon-192.png',
  '/assets/icon-512.png'
];

// Install event
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Cache opened');
        return cache.addAll(urlsToCache);
      })
  );
});

// Fetch event
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Return cached version or fetch from network
        return response || fetch(event.request);
      }
    )
  );
});

// Activate event
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});
'''
    
    with open('.streamlit/static/sw.js', 'w') as f:
        f.write(service_worker)
    
    print("✅ Created service worker (sw.js)")

def create_pwa_injector():
    """Create component to inject PWA code into Streamlit"""
    pwa_component = '''
import streamlit as st
import streamlit.components.v1 as components

def inject_pwa():
    """Inject PWA meta tags and scripts into Streamlit app"""
    
    pwa_html = """
    <script>
    // Add PWA meta tags to head
    if (!document.querySelector('link[rel="manifest"]')) {
        // Manifest link
        const manifest = document.createElement('link');
        manifest.rel = 'manifest';
        manifest.href = '/app/static/manifest.json';
        document.head.appendChild(manifest);
        
        // Theme color
        const themeColor = document.createElement('meta');
        themeColor.name = 'theme-color';
        themeColor.content = '#1f77b4';
        document.head.appendChild(themeColor);
        
        // Apple touch icon
        const appleIcon = document.createElement('link');
        appleIcon.rel = 'apple-touch-icon';
        appleIcon.href = '/app/static/assets/icon-192.png';
        document.head.appendChild(appleIcon);
        
        // Viewport meta (for mobile)
        const viewport = document.createElement('meta');
        viewport.name = 'viewport';
        viewport.content = 'width=device-width, initial-scale=1, shrink-to-fit=no';
        document.head.appendChild(viewport);
    }
    
    // Register service worker
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/app/static/sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    }
    
    // Add install prompt
    let deferredPrompt;
    
    window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        deferredPrompt = e;
        
        // Show install button
        const installDiv = document.createElement('div');
        installDiv.innerHTML = `
            <div style="
                position: fixed; 
                bottom: 20px; 
                right: 20px; 
                background: #1f77b4; 
                color: white; 
                padding: 12px 20px; 
                border-radius: 8px; 
                cursor: pointer;
                z-index: 1000;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                font-family: sans-serif;
                font-size: 14px;
            " onclick="installPWA()">
                📱 Install App
            </div>
        `;
        document.body.appendChild(installDiv);
    });
    
    window.installPWA = async () => {
        if (deferredPrompt) {
            deferredPrompt.prompt();
            const { outcome } = await deferredPrompt.userChoice;
            console.log(`User response to the install prompt: ${outcome}`);
            deferredPrompt = null;
            
            // Remove install button
            document.querySelector('[onclick="installPWA()"]').remove();
        }
    };
    </script>
    """
    
    components.html(pwa_html, height=0)

# Auto-inject PWA when this module is imported
if 'pwa_injected' not in st.session_state:
    inject_pwa()
    st.session_state.pwa_injected = True
'''
    
    with open('pwa_component.py', 'w') as f:
        f.write(pwa_component)
    
    print("✅ Created PWA component (pwa_component.py)")

def create_mobile_css():
    """Create mobile-optimized CSS"""
    mobile_css = '''
/* Mobile-first responsive design for Value Investment Dashboard */

/* Mobile optimizations */
@media (max-width: 768px) {
    /* Reduce padding on mobile */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    
    /* Make metrics more compact on mobile */
    [data-testid="metric-container"] {
        border: 1px solid #e0e0e0;
        padding: 0.5rem;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
    }
    
    /* Stack columns on mobile */
    .row-widget.stHorizontal > div {
        flex-direction: column !important;
    }
    
    /* Improve button sizing */
    .stButton > button {
        width: 100%;
        margin-bottom: 0.5rem;
    }
    
    /* Make tables scroll horizontally */
    .stDataFrame {
        overflow-x: auto;
    }
    
    /* Improve expander styling */
    .streamlit-expanderHeader {
        font-size: 1rem;
        font-weight: 600;
    }
    
    /* Better chart sizing */
    .stPlotlyChart {
        width: 100% !important;
    }
}

/* Install button styling */
.install-button {
    position: fixed;
    bottom: 20px;
    right: 20px;
    background: #1f77b4;
    color: white;
    border: none;
    padding: 12px 20px;
    border-radius: 8px;
    cursor: pointer;
    z-index: 1000;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    font-family: sans-serif;
    font-size: 14px;
}

/* PWA splash screen */
.pwa-splash {
    background: linear-gradient(135deg, #1f77b4, #ff7f0e);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100vh;
    font-family: sans-serif;
}

/* Hide Streamlit branding on mobile */
@media (max-width: 768px) {
    .viewerBadge_container__1QSob {
        display: none;
    }
    
    footer {
        display: none;
    }
}
'''
    
    os.makedirs('.streamlit', exist_ok=True)
    with open('.streamlit/mobile.css', 'w') as f:
        f.write(mobile_css)
    
    print("✅ Created mobile CSS styling")

def create_icon_placeholders():
    """Create placeholder icon files"""
    import base64
    from PIL import Image, ImageDraw
    
    # Create simple icon
    try:
        # Create 192x192 icon
        img = Image.new('RGBA', (192, 192), (31, 119, 180, 255))
        draw = ImageDraw.Draw(img)
        
        # Draw simple chart icon
        draw.rectangle([40, 60, 152, 132], fill=(255, 255, 255, 255))
        draw.line([60, 100, 80, 80, 100, 90, 120, 70, 140, 85], fill=(255, 127, 14, 255), width=3)
        
        # Save 192x192
        os.makedirs('.streamlit/static/assets', exist_ok=True)
        img.save('.streamlit/static/assets/icon-192.png')
        
        # Create 512x512 version
        img_large = img.resize((512, 512), Image.Resampling.LANCZOS)
        img_large.save('.streamlit/static/assets/icon-512.png')
        
        print("✅ Created app icons")
        
    except ImportError:
        print("⚠️  PIL not available, creating placeholder icon files")
        # Create empty files as placeholders
        os.makedirs('.streamlit/static/assets', exist_ok=True)
        with open('.streamlit/static/assets/icon-192.png', 'w') as f:
            f.write("# Placeholder - replace with actual 192x192 PNG icon")
        with open('.streamlit/static/assets/icon-512.png', 'w') as f:
            f.write("# Placeholder - replace with actual 512x512 PNG icon")

def update_main_app():
    """Add PWA import to main app"""
    print("\n📝 To enable PWA features, add this to the top of stock_value_dashboard.py:")
    print("=" * 60)
    print("import pwa_component  # This will auto-inject PWA features")
    print("=" * 60)

def main():
    """Create all PWA files"""
    print("📱 Value Investment Dashboard - PWA Creator")
    print("=" * 50)
    
    create_manifest()
    create_service_worker()
    create_pwa_injector() 
    create_mobile_css()
    create_icon_placeholders()
    update_main_app()
    
    print("\n🎉 PWA setup completed!")
    print("\n📁 Created files:")
    print("   - .streamlit/static/manifest.json")
    print("   - .streamlit/static/sw.js") 
    print("   - .streamlit/static/assets/icon-*.png")
    print("   - .streamlit/mobile.css")
    print("   - pwa_component.py")
    
    print("\n🚀 Next steps:")
    print("1. Add 'import pwa_component' to stock_value_dashboard.py")
    print("2. Replace placeholder icons with your actual app icons")
    print("3. Deploy to any web hosting (GitHub Pages, Netlify, etc.)")
    print("4. Users can then 'Install App' from their mobile browser")
    
    print("\n📱 How users install:")
    print("- Android: Chrome menu → 'Install app' or 'Add to Home screen'")
    print("- iOS: Safari share button → 'Add to Home Screen'")

if __name__ == '__main__':
    main()