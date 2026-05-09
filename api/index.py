import sys
import os

# Add the parent directory to sys.path so that 'src' can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.app import create_app

app = create_app()

# Vercel requires the application to be named 'app'
