module.exports = {
    content: [
        './templates/**/*.html',
        './core/templates/**/*.html',
    ],
    theme: {
        extend: {
            colors: {
                'primary': '#7C3AED',    // Rich Purple
                'teal': '#0D9488',       // Premium Teal
                'coral': '#F97316',      // Accent Coral
                'fuchsia': '#DB2777',    // Highlight Fuchsia
                'emerald': '#10B981',    // Success Emerald
                'amber': '#F59E0B',      // Warning Amber
                'rose': '#EF4444',       // Error Rose
            },
            boxShadow: {
                'premium': '0 8px 32px 0 rgba(31, 38, 135, 0.37)',
            },
            animation: {
                'gradient': 'gradient 15s ease infinite',
            },
            keyframes: {
                gradient: {
                    '0%, 100%': { backgroundPosition: '0% 50%' },
                    '50%': { backgroundPosition: '100% 50%' },
                },
            },
        },
    },
    plugins: [],
}