import re
import urllib.request
from flask import Flask, request, redirect, Response

app = Flask(__name__)

@app.route('/')
def home():
    return "YouTube Live Backend is Running!"

@app.route('/live')
def get_live_stream():
    url = request.args.get('url', 'https://www.youtube.com/watch?v=4Ng7A95vHT0')
    
    # Extract Video ID
    video_id_match = re.search(r'(?:v=|\/embed\/|\/1\/|\/v\/|https:\/\/youtu\.be\/)([^"&?\/\s]{11})', url)
    video_id = video_id_match.group(1) if video_id_match else '4Ng7A95vHT0'

    # Direct Invidious/Invidio redirect for bypass
    m3u8_url = f"https://inv.tux.im/latest_version?id={video_id}&italic=true"
    
    return redirect(m3u8_url)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
