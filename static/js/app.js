/**
 * Modern JavaScript Application Module
 * Vanilla JS with modular architecture for Savannah Apartments Management System
 */

// Main Application Class - Performance Optimized
class SavannahApp {
    constructor() {
        this.modules = new Map();
        this.eventListeners = new Map();
        this.initialized = false;
        this.config = {
            animationDuration: 200, // Reduced for faster animations
            toastDuration: 3000,    // Reduced for better UX
            debounceDelay: 150,     // Reduced for more responsive input
            apiTimeout: 5000        // Reduced for faster API calls
        };
        
        // Performance optimizations
        this.rafId = null;
        this.throttleMap = new Map();
        this.debounceMap = new Map();
        this.observerCache = new Map();
    }

    // Initialize the application
    init() {
        if (this.initialized) return;
        
        this.setupModules();
        this.bindGlobalEvents();
        this.initializeComponents();
        this.initialized = true;
        
        console.log('Savannah App initialized successfully');
    }

    // Setup all modules
    setupModules() {
        this.modules.set('toast', new ToastManager(this.config));
        this.modules.set('modal', new ModalManager(this.config));
        this.modules.set('form', new FormManager(this.config));
        this.modules.set('progress', new ProgressManager(this.config));
        this.modules.set('countdown', new CountdownManager(this.config));
        this.modules.set('animations', new AnimationManager(this.config));
        this.modules.set('api', new APIManager(this.config));
    }

    // Bind global event listeners
    bindGlobalEvents() {
        // Global keyboard shortcuts
        document.addEventListener('keydown', this.handleGlobalKeydown.bind(this));
        
        // Form submissions
        document.addEventListener('submit', this.handleFormSubmit.bind(this));
        
        // Link clicks for smooth transitions
        document.addEventListener('click', this.handleLinkClick.bind(this));
    }

    // Initialize components on page load
    initializeComponents() {
        // Initialize progress bars
        this.initProgressBars();
        
        // Initialize countdown timers
        this.initCountdownTimers();
        
        // Initialize form validation
        this.initFormValidation();
        
        // Initialize modals
        this.initModals();
        
        // Add loading states
        this.addLoadingStates();
    }

    // Handle theme toggle (removed to avoid conflicts with base template)
    handleThemeToggle() {
        // Theme toggle is handled in base.html template
        console.log('Theme toggle handled by base template');
    }

    // Handle global keyboard shortcuts
    handleGlobalKeydown(event) {
        // Escape key closes modals
        if (event.key === 'Escape') {
            this.getModule('modal').closeAll();
        }
        
        // Ctrl/Cmd + K for search (if search exists)
        if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
            event.preventDefault();
            const searchInput = document.querySelector('input[type="search"]');
            if (searchInput) {
                searchInput.focus();
            }
        }
    }

    // Handle form submissions with loading states
    handleFormSubmit(event) {
        // DISABLED - Let forms submit naturally without any JavaScript interference
        return;
    }

    // Handle link clicks for smooth transitions
    handleLinkClick(event) {
        const link = event.target.closest('a');
        if (!link || link.target === '_blank') return;
        
        // Add smooth transition class
        document.body.classList.add('page-transition');
        
        // Remove transition class after navigation
        setTimeout(() => {
            document.body.classList.remove('page-transition');
        }, 150);
    }

    // Initialize progress bars
    initProgressBars() {
        const progressBars = document.querySelectorAll('.progress-bar');
        progressBars.forEach(bar => {
            this.getModule('progress').initProgressBar(bar);
        });
    }

    // Initialize countdown timers
    initCountdownTimers() {
        const countdownElements = document.querySelectorAll('[data-countdown]');
        countdownElements.forEach(element => {
            this.getModule('countdown').initCountdown(element);
        });
    }

    // Initialize form validation
    initFormValidation() {
        const forms = document.querySelectorAll('form[data-validate]');
        forms.forEach(form => {
            this.getModule('form').initValidation(form);
        });
    }

    // Initialize modals
    initModals() {
        const modalTriggers = document.querySelectorAll('[data-modal-target]');
        modalTriggers.forEach(trigger => {
            this.getModule('modal').bindTrigger(trigger);
        });
    }

    // Add loading states to buttons and forms
    addLoadingStates() {
        // DISABLED - Let forms work naturally without JavaScript interference
        return;
    }

    // Get module instance
    getModule(name) {
        return this.modules.get(name);
    }

    // Utility method for smooth scrolling
    smoothScrollTo(element, offset = 0) {
        const targetPosition = element.offsetTop - offset;
        window.scrollTo({
            top: targetPosition,
            behavior: 'smooth'
        });
    }

    // Performance-optimized debouncing with caching
    debounce(func, wait) {
        const key = func.toString();
        if (this.debounceMap.has(key)) {
            return this.debounceMap.get(key);
        }
        
        let timeout;
        const debounced = function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func.apply(this, args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
        
        this.debounceMap.set(key, debounced);
        return debounced;
    }

    // Performance-optimized throttling with caching
    throttle(func, wait) {
        const key = func.toString();
        if (this.throttleMap.has(key)) {
            return this.throttleMap.get(key);
        }
        
        let inThrottle;
        const throttled = function executedFunction(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, wait);
            }
        };
        
        this.throttleMap.set(key, throttled);
        return throttled;
    }

    // Optimized requestAnimationFrame with cleanup
    requestAnimationFrame(callback) {
        if (this.rafId) {
            cancelAnimationFrame(this.rafId);
        }
        this.rafId = window.requestAnimationFrame(callback);
    }

    // Optimized DOM query with caching
    querySelector(selector, cache = true) {
        if (cache && this.observerCache.has(selector)) {
            return this.observerCache.get(selector);
        }
        
        const element = document.querySelector(selector);
        if (cache && element) {
            this.observerCache.set(selector, element);
        }
        return element;
    }

    // Batch DOM operations for better performance
    batchDOMOperations(operations) {
        requestAnimationFrame(() => {
            operations.forEach(operation => {
                if (typeof operation === 'function') {
                    operation();
                }
            });
        });
    }

    // Cleanup method for memory management
    cleanup() {
        if (this.rafId) {
            cancelAnimationFrame(this.rafId);
            this.rafId = null;
        }
        
        this.throttleMap.clear();
        this.debounceMap.clear();
        this.observerCache.clear();
        this.eventListeners.clear();
    }
}

// Toast Manager Module
class ToastManager {
    constructor(config) {
        this.config = config;
        this.toasts = new Set();
        this.container = this.createContainer();
    }

    createContainer() {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container';
            document.body.appendChild(container);
        }
        return container;
    }

    show(message, type = 'info', duration = null) {
        const toast = this.createToast(message, type);
        this.container.appendChild(toast);
        this.toasts.add(toast);

        // Animate in
        requestAnimationFrame(() => {
            toast.classList.add('toast-show');
        });

        // Auto remove
        const removeDelay = duration || this.config.toastDuration;
        setTimeout(() => {
            this.remove(toast);
        }, removeDelay);

        return toast;
    }

    createToast(message, type) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <span class="toast-message">${message}</span>
                <button class="toast-close" aria-label="Close notification">&times;</button>
            </div>
        `;

        // Close button functionality
        const closeBtn = toast.querySelector('.toast-close');
        closeBtn.addEventListener('click', () => this.remove(toast));

        return toast;
    }

    remove(toast) {
        if (!toast || !this.toasts.has(toast)) return;
        
        toast.classList.add('toast-hide');
        this.toasts.delete(toast);
        
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }

    clear() {
        this.toasts.forEach(toast => this.remove(toast));
    }
}

// Modal Manager Module
class ModalManager {
    constructor(config) {
        this.config = config;
        this.activeModals = new Set();
        this.setupGlobalHandlers();
    }

    setupGlobalHandlers() {
        // Close on backdrop click
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-backdrop')) {
                this.closeAll();
            }
        });

        // Close on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.activeModals.size > 0) {
                this.closeAll();
            }
        });
    }

    open(modalId) {
        const modal = document.getElementById(modalId);
        if (!modal) return;

        modal.classList.add('modal-show');
        this.activeModals.add(modal);
        document.body.classList.add('modal-open');

        // Focus management
        const focusableElements = modal.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        if (focusableElements.length > 0) {
            focusableElements[0].focus();
        }
    }

    close(modalId) {
        const modal = document.getElementById(modalId);
        if (!modal) return;

        modal.classList.remove('modal-show');
        this.activeModals.delete(modal);
        
        if (this.activeModals.size === 0) {
            document.body.classList.remove('modal-open');
        }
    }

    closeAll() {
        this.activeModals.forEach(modal => {
            modal.classList.remove('modal-show');
        });
        this.activeModals.clear();
        document.body.classList.remove('modal-open');
    }

    bindTrigger(trigger) {
        const modalId = trigger.dataset.modalTarget;
        trigger.addEventListener('click', (e) => {
            e.preventDefault();
            this.open(modalId);
        });
    }
}

// Form Manager Module
class FormManager {
    constructor(config) {
        this.config = config;
        this.validators = new Map();
        this.setupDefaultValidators();
    }

    setupDefaultValidators() {
        this.validators.set('required', (value) => value.trim() !== '');
        this.validators.set('email', (value) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value));
        this.validators.set('phone', (value) => /^[\+]?[1-9][\d]{0,15}$/.test(value.replace(/\s/g, '')));
        this.validators.set('minLength', (value, min) => value.length >= min);
        this.validators.set('maxLength', (value, max) => value.length <= max);
    }

    initValidation(form) {
        const inputs = form.querySelectorAll('input, select, textarea');
        
        // Use event delegation for better performance
        form.addEventListener('blur', (e) => {
            if (e.target.matches('input, select, textarea')) {
                this.validateField(e.target);
            }
        }, true);
        
        form.addEventListener('input', this.debounce((e) => {
            if (e.target.matches('input, select, textarea')) {
                this.validateField(e.target);
            }
        }, this.config.debounceDelay), true);

        // DISABLED - Let forms submit without JavaScript validation interference
        // form.addEventListener('submit', (e) => {
        //     // All validation disabled - let server handle validation
        // });
    }

    validateField(field) {
        const rules = this.getValidationRules(field);
        let isValid = true;
        let errorMessage = '';

        for (const rule of rules) {
            if (!this.validateRule(field.value, rule)) {
                isValid = false;
                errorMessage = rule.message;
                break;
            }
        }

        this.showFieldValidation(field, isValid, errorMessage);
        return isValid;
    }

    validateForm(form) {
        const fields = form.querySelectorAll('input, select, textarea');
        let isFormValid = true;

        fields.forEach(field => {
            if (!this.validateField(field)) {
                isFormValid = false;
            }
        });

        return isFormValid;
    }

    getValidationRules(field) {
        const rules = [];
        const attributes = field.attributes;

        if (attributes.required) {
            rules.push({ type: 'required', message: 'This field is required' });
        }

        if (attributes.type && attributes.type.value === 'email') {
            rules.push({ type: 'email', message: 'Please enter a valid email address' });
        }

        if (attributes.type && attributes.type.value === 'tel') {
            rules.push({ type: 'phone', message: 'Please enter a valid phone number' });
        }

        if (attributes.minlength) {
            rules.push({ 
                type: 'minLength', 
                value: parseInt(attributes.minlength.value),
                message: `Minimum length is ${attributes.minlength.value} characters`
            });
        }

        if (attributes.maxlength) {
            rules.push({ 
                type: 'maxLength', 
                value: parseInt(attributes.maxlength.value),
                message: `Maximum length is ${attributes.maxlength.value} characters`
            });
        }

        return rules;
    }

    validateRule(value, rule) {
        const validator = this.validators.get(rule.type);
        if (!validator) return true;
        
        return validator(value, rule.value);
    }

    showFieldValidation(field, isValid, errorMessage) {
        const container = field.closest('.form-group') || field.parentNode;
        let errorElement = container.querySelector('.field-error');

        if (isValid) {
            field.classList.remove('field-invalid');
            field.classList.add('field-valid');
            if (errorElement) {
                errorElement.remove();
            }
        } else {
            field.classList.remove('field-valid');
            field.classList.add('field-invalid');
            
            if (!errorElement) {
                errorElement = document.createElement('div');
                errorElement.className = 'field-error';
                container.appendChild(errorElement);
            }
            errorElement.textContent = errorMessage;
        }
    }

    showLoadingState(button) {
        const originalText = button.textContent;
        const originalDisabled = button.disabled;
        
        button.disabled = true;
        button.textContent = 'Loading...';
        button.classList.add('btn-loading');

        // Store original state for restoration
        button.dataset.originalText = originalText;
        button.dataset.originalDisabled = originalDisabled;
    }

    hideLoadingState(button) {
        button.disabled = button.dataset.originalDisabled === 'true';
        button.textContent = button.dataset.originalText;
        button.classList.remove('btn-loading');
    }

    addLoadingState(button) {
        // DISABLED - Let buttons work naturally without JavaScript interference
        return;
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// Progress Manager Module
class ProgressManager {
    constructor(config) {
        this.config = config;
        this.progressBars = new Map();
    }

    initProgressBar(element) {
        const progressBar = {
            element: element,
            value: parseInt(element.dataset.value) || 0,
            max: parseInt(element.dataset.max) || 100,
            animated: element.dataset.animated !== 'false'
        };

        this.progressBars.set(element, progressBar);
        this.updateProgress(element, progressBar.value, progressBar.animated);
    }

    updateProgress(element, value, animated = true) {
        const progressBar = this.progressBars.get(element);
        if (!progressBar) return;

        const percentage = Math.min(Math.max((value / progressBar.max) * 100, 0), 100);
        const fillElement = element.querySelector('.progress-fill');
        
        if (fillElement) {
            if (animated) {
                fillElement.style.transition = `width ${this.config.animationDuration}ms ease-out`;
            } else {
                fillElement.style.transition = 'none';
            }
            
            fillElement.style.width = `${percentage}%`;
            progressBar.value = value;
        }

        // Update percentage display
        const percentageElement = element.querySelector('.progress-percentage');
        if (percentageElement) {
            percentageElement.textContent = `${Math.round(percentage)}%`;
        }
    }

    animateProgress(element, targetValue, duration = 1000) {
        const progressBar = this.progressBars.get(element);
        if (!progressBar) return;

        const startValue = progressBar.value;
        const startTime = performance.now();

        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Easing function (ease-out)
            const easeOut = 1 - Math.pow(1 - progress, 3);
            const currentValue = startValue + (targetValue - startValue) * easeOut;
            
            this.updateProgress(element, currentValue, false);
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };

        requestAnimationFrame(animate);
    }
}

// Countdown Manager Module
class CountdownManager {
    constructor(config) {
        this.config = config;
        this.countdowns = new Map();
        this.intervalId = null;
    }

    initCountdown(element) {
        const targetDate = new Date(element.dataset.countdown);
        if (isNaN(targetDate.getTime())) return;

        const countdown = {
            element: element,
            targetDate: targetDate,
            active: true
        };

        this.countdowns.set(element, countdown);
        this.startCountdown();
    }

    startCountdown() {
        if (this.intervalId) return;

        this.intervalId = setInterval(() => {
            this.updateAllCountdowns();
        }, 1000);

        // Initial update
        this.updateAllCountdowns();
    }

    updateAllCountdowns() {
        const now = new Date();
        let hasActiveCountdowns = false;

        this.countdowns.forEach((countdown, element) => {
            if (!countdown.active) return;

            const timeLeft = countdown.targetDate - now;
            
            if (timeLeft <= 0) {
                this.handleCountdownComplete(element, countdown);
                return;
            }

            this.updateCountdownDisplay(element, timeLeft);
            hasActiveCountdowns = true;
        });

        if (!hasActiveCountdowns) {
            this.stopCountdown();
        }
    }

    updateCountdownDisplay(element, timeLeft) {
        const time = this.calculateTimeUnits(timeLeft);
        const display = this.formatCountdownDisplay(time);
        
        element.textContent = display;
        element.dataset.timeLeft = timeLeft;
    }

    calculateTimeUnits(milliseconds) {
        const totalSeconds = Math.floor(milliseconds / 1000);
        const totalMinutes = Math.floor(totalSeconds / 60);
        const totalHours = Math.floor(totalMinutes / 60);
        const totalDays = Math.floor(totalHours / 24);
        const totalMonths = Math.floor(totalDays / 30);

        return {
            months: totalMonths,
            days: totalDays % 30,
            hours: totalHours % 24,
            minutes: totalMinutes % 60,
            seconds: totalSeconds % 60
        };
    }

    formatCountdownDisplay(time) {
        const parts = [];
        
        if (time.months > 0) parts.push(`${time.months}m`);
        if (time.days > 0) parts.push(`${time.days}d`);
        if (time.hours > 0) parts.push(`${time.hours}h`);
        if (time.minutes > 0) parts.push(`${time.minutes}m`);
        if (time.seconds > 0) parts.push(`${time.seconds}s`);

        return parts.join(' ') || '0s';
    }

    handleCountdownComplete(element, countdown) {
        countdown.active = false;
        element.textContent = 'Expired';
        element.classList.add('countdown-expired');
        
        // Trigger custom event
        element.dispatchEvent(new CustomEvent('countdownComplete', {
            detail: { element, countdown }
        }));
    }

    stopCountdown() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
    }
}

// Animation Manager Module
class AnimationManager {
    constructor(config) {
        this.config = config;
        this.observer = this.createIntersectionObserver();
    }

    createIntersectionObserver() {
        return new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });
    }

    observe(element) {
        this.observer.observe(element);
    }

    unobserve(element) {
        this.observer.unobserve(element);
    }

    // Confetti animation for celebrations
    createConfetti(container = document.body) {
        const confettiCount = 50;
        const colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'];
        
        for (let i = 0; i < confettiCount; i++) {
            this.createConfettiPiece(container, colors);
        }
    }

    createConfettiPiece(container, colors) {
        const piece = document.createElement('div');
        piece.className = 'confetti-piece';
        piece.style.cssText = `
            position: fixed;
            width: 10px;
            height: 10px;
            background: ${colors[Math.floor(Math.random() * colors.length)]};
            top: -10px;
            left: ${Math.random() * 100}%;
            z-index: 9999;
            pointer-events: none;
        `;

        container.appendChild(piece);

        // Animate confetti
        const animation = piece.animate([
            { transform: 'translateY(0) rotate(0deg)', opacity: 1 },
            { transform: `translateY(${window.innerHeight + 100}px) rotate(720deg)`, opacity: 0 }
        ], {
            duration: 3000,
            easing: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)'
        });

        animation.addEventListener('finish', () => {
            piece.remove();
        });
    }
}

// API Manager Module
class APIManager {
    constructor(config) {
        this.config = config;
        this.baseURL = window.location.origin;
        this.defaultHeaders = {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        };
    }

    async request(endpoint, options = {}) {
        const url = endpoint.startsWith('http') ? endpoint : `${this.baseURL}${endpoint}`;
        
        const config = {
            method: 'GET',
            headers: { ...this.defaultHeaders, ...options.headers },
            ...options
        };

        // Add timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.config.apiTimeout);
        config.signal = controller.signal;

        try {
            const response = await fetch(url, config);
            clearTimeout(timeoutId);

            if (!response.ok) {
                if (response.status === 404) {
                    throw new Error('Resource not found');
                } else if (response.status === 500) {
                    throw new Error('Server error occurred');
                } else {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
            }

            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            }
            
            return await response.text();
        } catch (error) {
            clearTimeout(timeoutId);
            throw error;
        }
    }

    async get(endpoint, options = {}) {
        return this.request(endpoint, { ...options, method: 'GET' });
    }

    async post(endpoint, data, options = {}) {
        return this.request(endpoint, {
            ...options,
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async put(endpoint, data, options = {}) {
        return this.request(endpoint, {
            ...options,
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    async delete(endpoint, options = {}) {
        return this.request(endpoint, { ...options, method: 'DELETE' });
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.savannahApp = new SavannahApp();
    window.savannahApp.init();
});

// Export for global access
window.SavannahApp = SavannahApp;
