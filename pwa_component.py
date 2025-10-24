
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
