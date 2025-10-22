/**
 * Theme Context Module
 * Manages theme state with support for Light, Dark, and System themes
 * Adapted for Flask application
 */

class ThemeContext {
    constructor() {
        this.theme = 'system';
        this.resolvedTheme = 'light';
        this.listeners = new Set();
        this.mediaQuery = null;
        this.initialized = false;
        
        this.init();
    }

    init() {
        if (this.initialized) return;
        
        // Load theme from localStorage
        this.loadTheme();
        
        // Set up system preference listener
        this.setupSystemPreferenceListener();
        
        // Apply initial theme
        this.updateResolvedTheme();
        this.applyTheme();
        
        this.initialized = true;
        console.log('Theme context initialized');
    }

    loadTheme() {
        try {
            const stored = localStorage.getItem('theme');
            if (stored && ['light', 'dark', 'system'].includes(stored)) {
                this.theme = stored;
            }
        } catch (e) {
            console.warn('Could not load theme from localStorage:', e);
        }
    }

    setupSystemPreferenceListener() {
        if (typeof window !== 'undefined' && window.matchMedia) {
            this.mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
            this.mediaQuery.addEventListener('change', () => {
                if (this.theme === 'system') {
                    this.updateResolvedTheme();
                    this.applyTheme();
                    this.notifyListeners();
                }
            });
        }
    }

    updateResolvedTheme() {
        if (this.theme === 'system') {
            this.resolvedTheme = this.getSystemPreference();
        } else {
            this.resolvedTheme = this.theme;
        }
    }

    getSystemPreference() {
        if (typeof window !== 'undefined' && window.matchMedia) {
            return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
        }
        return 'light';
    }

    setTheme(newTheme) {
        if (!['light', 'dark', 'system'].includes(newTheme)) {
            console.warn('Invalid theme:', newTheme);
            return;
        }

        this.theme = newTheme;
        this.updateResolvedTheme();
        this.applyTheme();
        this.saveTheme();
        this.notifyListeners();
    }

    applyTheme() {
        const root = document.documentElement;
        
        // Remove existing theme classes
        root.classList.remove('light', 'dark');
        
        // Add new theme class
        root.classList.add(this.resolvedTheme);
        
        // Add transition class for smooth theme change
        root.classList.add('theme-transitioning');
        setTimeout(() => {
            root.classList.remove('theme-transitioning');
        }, 300);
    }

    saveTheme() {
        try {
            localStorage.setItem('theme', this.theme);
        } catch (e) {
            console.warn('Could not save theme to localStorage:', e);
        }
    }

    subscribe(listener) {
        this.listeners.add(listener);
        return () => this.listeners.delete(listener);
    }

    notifyListeners() {
        this.listeners.forEach(listener => {
            try {
                listener({
                    theme: this.theme,
                    resolvedTheme: this.resolvedTheme
                });
            } catch (e) {
                console.error('Theme listener error:', e);
            }
        });
    }

    getTheme() {
        return this.theme;
    }

    getResolvedTheme() {
        return this.resolvedTheme;
    }

    isDark() {
        return this.resolvedTheme === 'dark';
    }

    isLight() {
        return this.resolvedTheme === 'light';
    }

    isSystem() {
        return this.theme === 'system';
    }

    destroy() {
        if (this.mediaQuery) {
            this.mediaQuery.removeEventListener('change', this.updateResolvedTheme);
        }
        this.listeners.clear();
        this.initialized = false;
    }
}

// Create global theme context instance
window.themeContext = new ThemeContext();

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ThemeContext;
}
