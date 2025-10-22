/**
 * Theme Toggle Component
 * Animated dropdown toggle with Light, Dark, and System options
 * Adapted for Flask application
 */

class ThemeToggle {
    constructor(container, options = {}) {
        this.container = container;
        this.options = {
            animationDuration: 200,
            glassmorphism: true,
            showLabels: true,
            ...options
        };
        
        this.isOpen = false;
        this.themeContext = window.themeContext;
        this.unsubscribe = null;
        
        this.init();
    }

    init() {
        this.createToggle();
        this.bindEvents();
        this.subscribeToThemeChanges();
        this.updateDisplay();
    }

    createToggle() {
        this.container.innerHTML = '';
        
        // Create toggle button
        this.toggleButton = document.createElement('button');
        this.toggleButton.className = 'theme-toggle-btn';
        this.toggleButton.setAttribute('aria-label', 'Toggle theme');
        this.toggleButton.setAttribute('aria-expanded', 'false');
        this.toggleButton.setAttribute('aria-haspopup', 'true');
        
        // Create dropdown container
        this.dropdown = document.createElement('div');
        this.dropdown.className = 'theme-dropdown';
        this.dropdown.setAttribute('role', 'menu');
        this.dropdown.setAttribute('aria-hidden', 'true');
        
        // Theme options
        this.themes = [
            {
                value: 'light',
                label: 'Light',
                icon: this.createIcon('sun'),
                description: 'Light theme'
            },
            {
                value: 'dark',
                label: 'Dark',
                icon: this.createIcon('moon'),
                description: 'Dark theme'
            },
            {
                value: 'system',
                label: 'System',
                icon: this.createIcon('monitor'),
                description: 'Follow system preference'
            }
        ];
        
        // Create dropdown items
        this.themes.forEach(theme => {
            const item = this.createThemeItem(theme);
            this.dropdown.appendChild(item);
        });
        
        this.container.appendChild(this.toggleButton);
        this.container.appendChild(this.dropdown);
    }

    createIcon(type) {
        const icon = document.createElement('span');
        icon.className = `theme-icon theme-icon-${type}`;
        
        switch (type) {
            case 'sun':
                icon.innerHTML = `
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="12" cy="12" r="5"/>
                        <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
                    </svg>
                `;
                break;
            case 'moon':
                icon.innerHTML = `
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
                    </svg>
                `;
                break;
            case 'monitor':
                icon.innerHTML = `
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
                        <line x1="8" y1="21" x2="16" y2="21"/>
                        <line x1="12" y1="17" x2="12" y2="21"/>
                    </svg>
                `;
                break;
        }
        
        return icon;
    }

    createThemeItem(theme) {
        const item = document.createElement('button');
        item.className = 'theme-option';
        item.setAttribute('role', 'menuitem');
        item.setAttribute('data-theme', theme.value);
        
        item.innerHTML = `
            <span class="theme-option-icon">${theme.icon.outerHTML}</span>
            <span class="theme-option-label">${theme.label}</span>
            <span class="theme-option-check" aria-hidden="true">✓</span>
        `;
        
        return item;
    }

    bindEvents() {
        // Toggle button click
        this.toggleButton.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.toggle();
        });
        
        // Theme option clicks
        this.dropdown.addEventListener('click', (e) => {
            const option = e.target.closest('.theme-option');
            if (option) {
                const theme = option.getAttribute('data-theme');
                this.selectTheme(theme);
                this.close();
            }
        });
        
        // Close on outside click
        document.addEventListener('click', (e) => {
            if (!this.container.contains(e.target)) {
                this.close();
            }
        });
        
        // Close on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.close();
                this.toggleButton.focus();
            }
        });
        
        // Handle keyboard navigation
        this.dropdown.addEventListener('keydown', (e) => {
            this.handleKeyboardNavigation(e);
        });
    }

    handleKeyboardNavigation(e) {
        const options = Array.from(this.dropdown.querySelectorAll('.theme-option'));
        const currentIndex = options.indexOf(document.activeElement);
        
        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                const nextIndex = (currentIndex + 1) % options.length;
                options[nextIndex].focus();
                break;
            case 'ArrowUp':
                e.preventDefault();
                const prevIndex = currentIndex <= 0 ? options.length - 1 : currentIndex - 1;
                options[prevIndex].focus();
                break;
            case 'Enter':
            case ' ':
                e.preventDefault();
                if (document.activeElement.classList.contains('theme-option')) {
                    const theme = document.activeElement.getAttribute('data-theme');
                    this.selectTheme(theme);
                    this.close();
                }
                break;
        }
    }

    subscribeToThemeChanges() {
        if (this.themeContext) {
            this.unsubscribe = this.themeContext.subscribe(({ theme, resolvedTheme }) => {
                this.updateDisplay();
            });
        }
    }

    toggle() {
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    }

    open() {
        this.isOpen = true;
        this.toggleButton.setAttribute('aria-expanded', 'true');
        this.dropdown.setAttribute('aria-hidden', 'false');
        this.dropdown.classList.add('theme-dropdown-open');
        
        // Focus first option
        const firstOption = this.dropdown.querySelector('.theme-option');
        if (firstOption) {
            setTimeout(() => firstOption.focus(), 100);
        }
    }

    close() {
        this.isOpen = false;
        this.toggleButton.setAttribute('aria-expanded', 'false');
        this.dropdown.setAttribute('aria-hidden', 'true');
        this.dropdown.classList.remove('theme-dropdown-open');
    }

    selectTheme(theme) {
        if (this.themeContext) {
            this.themeContext.setTheme(theme);
        }
    }

    updateDisplay() {
        if (!this.themeContext) return;
        
        const currentTheme = this.themeContext.getTheme();
        const currentThemeData = this.themes.find(t => t.value === currentTheme);
        
        if (currentThemeData) {
            // Update toggle button content
            this.toggleButton.innerHTML = `
                <span class="theme-toggle-icon">${currentThemeData.icon.outerHTML}</span>
                ${this.options.showLabels ? `<span class="theme-toggle-label">${currentThemeData.label}</span>` : ''}
                <span class="theme-toggle-arrow">▼</span>
            `;
            
            // Update option states
            this.dropdown.querySelectorAll('.theme-option').forEach(option => {
                const isSelected = option.getAttribute('data-theme') === currentTheme;
                option.classList.toggle('theme-option-selected', isSelected);
                option.setAttribute('aria-selected', isSelected);
            });
        }
    }

    destroy() {
        if (this.unsubscribe) {
            this.unsubscribe();
        }
        
        // Remove event listeners
        this.toggleButton.removeEventListener('click', this.toggle);
        this.dropdown.removeEventListener('click', this.handleClick);
        
        // Clean up DOM
        this.container.innerHTML = '';
    }
}

// Auto-initialize theme toggles
document.addEventListener('DOMContentLoaded', () => {
    const themeToggleContainers = document.querySelectorAll('[data-theme-toggle]');
    themeToggleContainers.forEach(container => {
        new ThemeToggle(container);
    });
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ThemeToggle;
}
