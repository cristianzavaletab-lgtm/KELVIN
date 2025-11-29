/**
 * Progressive Web App (PWA) Setup
 */

// Register Service Worker
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('✅ Service Worker registered:', registration.scope);

                // Check for updates
                registration.addEventListener('updatefound', () => {
                    const newWorker = registration.installing;
                    newWorker.addEventListener('statechange', () => {
                        if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                            showUpdateNotification();
                        }
                    });
                });
            })
            .catch(error => {
                console.log('❌ Service Worker registration failed:', error);
            });
    });
}

// Install Prompt
let deferredPrompt;

window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    showInstallPromotion();
});

function showInstallPromotion() {
    const installBtn = document.querySelector('[data-install-pwa]');
    if (installBtn) {
        installBtn.style.display = 'block';
        installBtn.addEventListener('click', installPWA);
    }
}

async function installPWA() {
    if (!deferredPrompt) return;

    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;

    if (outcome === 'accepted') {
        console.log('✅ PWA installed');
    }

    deferredPrompt = null;
}

// Update Notification
function showUpdateNotification() {
    if (window.App) {
        window.App.showToast('Nueva versión disponible. Recarga la página.', 'info', 5000);
    }
}

// Offline Detection
window.addEventListener('online', () => {
    if (window.App) {
        window.App.showToast('Conexión restaurada', 'success');
    }
});

window.addEventListener('offline', () => {
    if (window.App) {
        window.App.showToast('Sin conexión a internet', 'warning');
    }
});

// iOS Standalone Detection
if (window.navigator.standalone) {
    console.log('📱 Running as PWA on iOS');
}

// Android Standalone Detection
if (window.matchMedia('(display-mode: standalone)').matches) {
    console.log('📱 Running as PWA on Android');
}
