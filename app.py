import re
from flask import Flask, request, redirect

app = Flask(__name__)

@app.route('/')
def home():
    return "YouTube Live Backend is Running!"

# URL query വഴി വരുന്നവയ്ക്ക് (?url=...)
@app.route('/live')
def get_live_param():
    url = request.args.get('url', 'https://www.youtube.com/watch?v=4Ng7A95vHT0')
    video_id_match = re.search(r'(?:v=|\/embed\/|\/1\/|\/v\/|https:\/\/youtu\.be\/)([^"&?\/\s]{11})', url)
    video_id = video_id_match.group(1) if video_id_match else '4Ng7A95vHT0'
    return redirect(f"https://inv.tux.im/latest_version?id={video_id}&italic=true")

# ഡയറക്ട് പാത്ത് വഴി വരുന്നവയ്ക്ക് (/live/VIDEO_ID.m3u8)
@app.route('/live/<path:video_id>')
def get_live_path(video_id):
    # .m3u8 നീക്കം ചെയ്യുന്നു
    clean_id = video_id.replace('.m3u8', '')
    return redirect(f"https://inv.tux.im/latest_version?id={clean_id}&italic=true")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
