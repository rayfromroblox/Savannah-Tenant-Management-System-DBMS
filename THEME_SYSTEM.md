# Enhanced Theme Switching System

A complete theme switching implementation for the Savannah Apartments Management System, adapted from React/Next.js patterns to work with Flask and vanilla JavaScript.

## Features

### 🎨 Three Theme Modes
- **Light Theme**: Clean, bright interface
- **Dark Theme**: Easy-on-the-eyes dark interface  
- **System Theme**: Automatically follows OS preference

### ✨ Advanced Features
- **Real-time System Preference Detection**: Automatically updates when OS theme changes
- **Local Storage Persistence**: Remembers user preference across sessions
- **Smooth Animations**: CSS transitions and JavaScript animations for theme changes
- **Glassmorphism Design**: Modern UI with backdrop blur effects
- **Accessibility Support**: Full keyboard navigation and ARIA labels
- **Mobile Responsive**: Optimized for all screen sizes
- **TypeScript-like Structure**: Well-organized, maintainable code

## File Structure

```
static/
├── js/
│   ├── theme-context.js    # Core theme management
│   ├── theme-toggle.js     # UI component
│   └── app.js             # Main application (existing)
├── css/
│   └── style.css          # Enhanced with theme variables
templates/
└── base.html              # Updated with new theme system
```

## Implementation Details

### Theme Context (`theme-context.js`)

The core theme management system that handles:
- Theme state management (light, dark, system)
- System preference detection
- Local storage persistence
- Real-time updates
- Event subscription system

**Key Methods:**
- `setTheme(theme)`: Change the current theme
- `getTheme()`: Get current theme setting
- `getResolvedTheme()`: Get actual applied theme (light/dark)
- `subscribe(listener)`: Subscribe to theme changes
- `isDark()`, `isLight()`, `isSystem()`: Theme state checks

### Theme Toggle Component (`theme-toggle.js`)

An animated dropdown component featuring:
- Three theme options with icons
- Smooth open/close animations
- Keyboard navigation support
- Mobile-optimized design
- Glassmorphism styling

**Auto-initialization:**
```html
<div class="theme-toggle-container" data-theme-toggle>
    <!-- Component initializes automatically -->
</div>
```

### Enhanced CSS Variables

The CSS system now includes:
- **Light Theme**: Default bright colors
- **Dark Theme**: Dark mode colors
- **System Theme**: Media query-based automatic switching
- **Enhanced Variables**: More comprehensive color palette
- **Shadow System**: Consistent shadow variables
- **Scrollbar Styling**: Custom scrollbar colors

## Usage Examples

### Basic Theme Switching

```javascript
// Get theme context
const themeContext = window.themeContext;

// Set theme
themeContext.setTheme('dark');        // Force dark theme
themeContext.setTheme('light');       // Force light theme  
themeContext.setTheme('system');      // Follow system preference

// Get current theme
console.log(themeContext.getTheme());        // 'system'
console.log(themeContext.getResolvedTheme()); // 'dark' (if system prefers dark)

// Check theme state
if (themeContext.isDark()) {
    console.log('Currently using dark theme');
}
```

### Subscribing to Theme Changes

```javascript
// Subscribe to theme changes
const unsubscribe = themeContext.subscribe(({ theme, resolvedTheme }) => {
    console.log(`Theme changed to: ${theme} (resolved: ${resolvedTheme})`);
    // Update UI elements, charts, etc.
});

// Unsubscribe when done
unsubscribe();
```

### Custom Theme Toggle

```javascript
// Initialize custom theme toggle
const container = document.getElementById('my-theme-toggle');
const toggle = new ThemeToggle(container, {
    showLabels: true,
    glassmorphism: true
});
```

## CSS Customization

### Using Theme Variables

```css
.my-component {
    background: var(--surface);
    color: var(--text-primary);
    border: 1px solid var(--divider);
    box-shadow: var(--shadow-md);
}

.my-component:hover {
    background: var(--hover-bg);
}
```

### Adding New Theme Variables

```css
:root {
    --my-custom-color: #ff6b6b;
}

html.dark {
    --my-custom-color: #ff8e8e;
}

@media (prefers-color-scheme: dark) {
    html:not(.light):not(.dark) {
        --my-custom-color: #ff8e8e;
    }
}
```

## Browser Support

- **Modern Browsers**: Full support with all features
- **Legacy Browsers**: Graceful degradation
- **Mobile Browsers**: Optimized responsive design
- **Accessibility**: Screen reader compatible

## Performance Optimizations

- **Efficient DOM Updates**: Minimal reflows and repaints
- **Event Delegation**: Optimized event handling
- **CSS Containment**: Better rendering performance
- **Reduced Motion Support**: Respects user preferences
- **Memory Management**: Proper cleanup and garbage collection

## Migration from Old System

The new system is backward compatible with the existing theme toggle. The old button will continue to work while the new system provides enhanced functionality.

### Gradual Migration

1. **Phase 1**: New system runs alongside old system
2. **Phase 2**: Replace old toggle with new component
3. **Phase 3**: Remove old theme code

## Testing

Test the theme functionality by:
- Using the theme toggle in the navigation bar
- Switching between Light, Dark, and System themes
- Verifying date input calendars are visible in dark mode
- Testing mobile responsiveness
- Checking accessibility features

## Troubleshooting

### Common Issues

1. **Theme not persisting**: Check localStorage permissions
2. **System theme not updating**: Verify media query support
3. **Animations not smooth**: Check for CSS conflicts
4. **Mobile layout issues**: Verify responsive breakpoints

### Debug Mode

```javascript
// Enable debug logging
window.themeContext.debug = true;
```

## Future Enhancements

- **Theme Customization**: User-defined color schemes
- **Theme Scheduling**: Automatic theme switching by time
- **Theme Sync**: Cross-device theme synchronization
- **Advanced Animations**: More sophisticated transition effects
- **Theme Presets**: Predefined theme collections

## Contributing

When adding new theme-related features:

1. Follow the existing code structure
2. Add proper error handling
3. Include accessibility features
4. Test across all supported browsers
5. Update documentation

## License

This theme system is part of the Savannah Apartments Management System and follows the same licensing terms.
