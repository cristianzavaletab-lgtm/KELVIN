/**
 * Main Application JavaScript
 * Mobile-First Interactions
 */

// App State
const App = {
  drawer: null,
  drawerOverlay: null,
  theme: localStorage.getItem('theme') || 'light',
  
  init() {
    this.initDrawer();
    this.initTheme();
    this.initForms();
    this.initToasts();
    this.initLogout();
    console.log('🚀 AGROTECNICA MIJAEL App Initialized');
  },
  
  // Drawer Navigation
  initDrawer() {
    this.drawer = document.querySelector('.drawer');
    this.drawerOverlay = document.querySelector('.drawer-overlay');
    
    const menuBtn = document.querySelector('[data-drawer-toggle]');
    if (menuBtn) {
      menuBtn.addEventListener('click', () => this.toggleDrawer());
    }
    
    if (this.drawerOverlay) {
      this.drawerOverlay.addEventListener('click', () => this.closeDrawer());
    }
  },
  
  toggleDrawer() {
    if (this.drawer && this.drawerOverlay) {
      this.drawer.classList.toggle('active');
      this.drawerOverlay.classList.toggle('active');
      document.body.style.overflow = this.drawer.classList.contains('active') ? 'hidden' : '';
    }
  },
  
  closeDrawer() {
    if (this.drawer && this.drawerOverlay) {
      this.drawer.classList.remove('active');
      this.drawerOverlay.classList.remove('active');
      document.body.style.overflow = '';
    }
  },
  
  // Theme Toggle
  initTheme() {
    document.documentElement.setAttribute('data-theme', this.theme);
    
    const themeToggle = document.querySelector('[data-theme-toggle]');
    if (themeToggle) {
      themeToggle.addEventListener('click', () => this.toggleTheme());
    }
  },
  
  toggleTheme() {
    this.theme = this.theme === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', this.theme);
    localStorage.setItem('theme', this.theme);
  },
  
  // Form Enhancements
  initForms() {
    // Auto-resize textareas
    document.querySelectorAll('textarea').forEach(textarea => {
      textarea.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = this.scrollHeight + 'px';
      });
    });
    
    // File input preview
    document.querySelectorAll('input[type="file"]').forEach(input => {
      input.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file && file.type.startsWith('image/')) {
          const reader = new FileReader();
          reader.onload = function(e) {
            const preview = document.querySelector(`[data-preview="${input.id}"]`);
            if (preview) {
              preview.src = e.target.result;
              preview.style.display = 'block';
            }
          };
          reader.readAsDataURL(file);
        }
      });
    });
  },
  
  // Toast Notifications
  initToasts() {
    const container = document.querySelector('.toast-container');
    if (!container) {
      const toastContainer = document.createElement('div');
      toastContainer.className = 'toast-container';
      document.body.appendChild(toastContainer);
    }
  },
  
  showToast(message, type = 'info', duration = 3000) {
    const container = document.querySelector('.toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    
    container.appendChild(toast);
    
    setTimeout(() => {
      toast.style.opacity = '0';
      setTimeout(() => toast.remove(), 300);
    }, duration);
  },
  
  // Confirm Dialog
  confirm(message, callback) {
    if (window.confirm(message)) {
      callback();
    }
  },
  
  // Loading State
  showLoading(element) {
    const spinner = document.createElement('span');
    spinner.className = 'spinner';
    spinner.setAttribute('data-loading', 'true');
    element.appendChild(spinner);
    element.disabled = true;
  },
  
  hideLoading(element) {
    const spinner = element.querySelector('[data-loading]');
    if (spinner) spinner.remove();
    element.disabled = false;
  }
  ,
  // Logout Cleanup
  initLogout() {
    const links = document.querySelectorAll('[data-logout]');
    links.forEach(link => {
      link.addEventListener('click', async (e) => {
        e.preventDefault();
        try {
          localStorage.clear();
          sessionStorage.clear();
          document.documentElement.setAttribute('data-theme', 'light');
          if (window.caches) {
            const keys = await caches.keys();
            await Promise.all(keys.map(k => caches.delete(k)));
          }
        } catch (err) {}
        const href = link.getAttribute('href');
        if (window.App) {
          window.App.showToast('Sesión cerrada', 'success', 800);
        }
        setTimeout(() => { window.location.href = href; }, 400);
      });
    });
  }
};

// Initialize on DOM ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => App.init());
} else {
  App.init();
}

// Export for use in other scripts
window.App = App;
