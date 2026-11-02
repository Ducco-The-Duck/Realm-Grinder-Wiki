"""Load the page templates (HTML, CSS and JS the builders fill in) from tools/pages/templates/."""
import os

DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
THEME = '/*THEME*/\n'


def _read(name):
    with open(os.path.join(DIR, name), encoding='utf-8') as f:
        return f.read()


def load(name):
    """a template; the line /*THEME*/ stands for the colours and base style every page shares (theme.css)"""
    text = _read(name)
    if THEME in text:
        text = text.replace(THEME, _read('theme.css'))
    return text
