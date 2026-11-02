"""Load the page templates (HTML, CSS and JS the builders fill in) from tools/pages/templates/."""
import os

DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')


def load(name):
    with open(os.path.join(DIR, name), encoding='utf-8') as f:
        return f.read()
