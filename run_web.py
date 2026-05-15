#!/usr/bin/env python3
"""Launch the Glossary Checker web interface."""
from glossary_checker.web import app
from glossary_checker.config import Config

if __name__ == '__main__':
    app.run(debug=Config.WEB_DEBUG, host=Config.WEB_HOST, port=Config.WEB_PORT)
