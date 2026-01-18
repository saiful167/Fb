from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import re
import time
from datetime import datetime
from urllib.parse import urlparse

app = Flask(__name__)

# Basic Config
ALLOWED_DOMAINS = ['www.facebook.com', 'm.facebook.com', 'facebook.com']
REQUEST_TIMEOUT = 10 

class FacebookProfileScraper:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }

    def validate_url(self, url):
        parsed = urlparse(url)
        return parsed.netloc in ALLOWED_DOMAINS

    def extract_image_urls(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        images = {'profile_picture': None, 'cover_photo': None, 'all_images': []}
        
        # Regex to find fbcdn images
        img_patterns = re.findall(r'https://scontent[^"\'\\<>\s]+\.fbcdn\.net[^"\'\\<>\s]+\.(?:jpg|jpeg|png|webp)', html_content)
        
        for url in set(img_patterns):
            clean_url = url.replace('\\', '')
            images['all_images'].append(clean_url)
            if '/t39.30808-1/' in clean_url: # Profile pic pattern
                images['profile_picture'] = clean_url
            if '/t39.30808-6/' in clean_url: # Cover photo pattern
                images['cover_photo'] = clean_url
        
        return images

    def scrape(self, profile_url):
        try:
            res = self.session.get(profile_url, headers=self.headers, timeout=REQUEST_TIMEOUT)
            if res.status_code == 200:
                return self.extract_image_urls(res.text)
            return None
        except:
            return None

scraper = FacebookProfileScraper()

@app.route('/')
def home():
    return jsonify({"message": "Facebook Scraper is Live on Vercel", "usage": "/api/all?url=LINK"})

@app.route('/api/all')
def get_images():
    url = request.args.get('url')
    if not url or not scraper.validate_url(url):
        return jsonify({"error": "Invalid Facebook URL"}), 400
    
    data = scraper.scrape(url)
    if data:
        return jsonify({"success": True, "data": data})
    return jsonify({"success": False, "message": "No data found. Facebook might be blocking the request."}), 404

# Vercel requires the app object
app = app
