"""
Streamlit App Launcher
Run with: streamlit run app_launcher.py
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Now import and run the app
from src.app import main

if __name__ == "__main__":
    main()
