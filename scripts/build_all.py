#!/usr/bin/env python3
"""
Build All
Runs all build scripts in sequence.
"""

import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent


def main():
    scripts = [
        SCRIPTS_DIR / 'build_homepage.py',
        SCRIPTS_DIR / 'build_sitemap.py',
    ]
    
    for script in scripts:
        print(f'\n=== Running {script.name} ===')
        result = subprocess.run([sys.executable, str(script)])
        if result.returncode != 0:
            print(f'Error running {script.name}')
            sys.exit(1)
    
    print('\n=== Build complete ===')


if __name__ == '__main__':
    main()


