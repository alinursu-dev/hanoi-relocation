#!/usr/bin/env python3
"""
Hanoi Relocation Dashboard - Flask App
Run with: python run.py
"""
from app import create_app

app = create_app()



if __name__ == '__main__':
    print("\n Hanoi Relocation Dashboard")
    print("=" * 40)
    print("Starting server at http://localhost:5001")
    print("Press Ctrl+C to stop\n")
    app.run(debug=True, port=5001)
