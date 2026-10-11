#!/bin/sh
# Serve docs/ at http://localhost:8766 for local preview.
cd "$(dirname "$0")/../docs" && exec python -m http.server 8766
