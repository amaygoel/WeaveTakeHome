import sys
import os

from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ingestion'))

from db import init_db
from fetch_prs import fetch_prs

if __name__ == '__main__':
    print('=== Initializing database ===')
    init_db()

    print('\n=== Fetching pull requests ===')
    fetch_prs()

    print('\n=== Ingestion complete ===')
