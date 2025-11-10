# database.py
import sqlite3
from datetime import datetime

def save_ad(ad):
    conn = sqlite3.connect('data/ads.db')
    c = conn.cursor()
    c.execute('''
        INSERT OR IGNORE INTO ads 
        (title, description, url, price, city, category, source, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        ad['title'],
        ad['description'],
        ad['url'],
        str(ad['price']),
        ad['city'],
        ad['category'],
        ad['source'],
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()

def ad_exists(url):
    conn = sqlite3.connect('data/ads.db')
    c = conn.cursor()
    c.execute('SELECT 1 FROM ads WHERE url = ?', (url,))
    exists = c.fetchone() is not None
    conn.close()
    return exists

def init_db():
    conn = sqlite3.connect('data/ads.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS ads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            url TEXT UNIQUE,
            price TEXT,
            city TEXT,
            category TEXT,
            source TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()