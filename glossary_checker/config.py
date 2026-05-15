"""Centralized configuration for Glossary Checker."""

class Config:
    # Web Configuration
    WEB_HOST = '0.0.0.0'
    WEB_PORT = 5000
    WEB_DEBUG = True

    # GUI Configuration
    GUI_TITLE = "Glossary Compliance Checker"
    GUI_GEOMETRY = "1100x700"
    GUI_BG_COLOR = '#1e1e2e'
    
    # GUI Colors
    GUI_COLORS = {
        'bg': '#1e1e2e',
        'surface': '#2d2d3f',
        'primary': '#89b4fa',
        'success': '#a6e3a1',
        'error': '#f38ba8',
        'text': '#cdd6f4',
        'text_secondary': '#9399b2',
    }
