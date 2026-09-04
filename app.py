from flask import Flask, Response, request
import subprocess
import urllib.parse
import requests
import re
import os
import time

app = Flask(__name__)

VIDEO_ID = "4Ng7A95vHT0"

cache = {
    "url": None,
    "time": 0
}


def get_hls_url():
    now = time.time()

    if cache["url"] and now - cache["time"] < 20:
        return cache["url"]

    result = subprocess.run(
        [
            "yt-dlp",
            "--js-runtimes", "deno",
            "--remote-components", "ejs:github",
            "-g",
            "--no-playlist",
            f"https://www.youtube.com/watch?v={VIDEO_ID}"
        ],
        capture_output=True,
        text=True,
        timeout=30
    )

    url = result.stdout.strip()

    if not url.startswith("http"):
        raise Exception(
            result.stderr.strip() or "HLS URL not found"
        )

    cache["url"] = url
    cache["time"] = now

    return url


@app.route("/")
def home():
    return "YouTube Live Backend OK"


@app.route("/live/<video_id>.m3u8")
def live(video_id):

    if video_id != VIDEO_ID:
        return "Invalid video ID", 404

    try:
        hls_url = get_hls_url()

        r = requests.get(
            hls_url,
            timeout=15,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        if r.status_code != 200:
            return "Unable to fetch YouTube playlist", 502

        playlist = r.text

        base = hls_url.rsplit("/", 1)[0] + "/"

        def rewrite(match):
            url = match.group(1)

            if url.startswith("http"):
                full_url = url
            else:
                full_url = urllib.parse.urljoin(base, url)

            return (
                'URI="/proxy?url=' +
                urllib.parse.quote(full_url, safe="") +
                '"'
            )

        playlist = re.sub(
            r'URI="([^"]+)"',
            rewrite,
            playlist
        )

        lines = playlist.splitlines()

        for i, line in enumerate(lines):
            if line.startswith("http"):
                lines[i] = (
                    "/proxy?url=" +
                    urllib.parse.quote(line, safe="")
                )
            elif line and not line.startswith("#"):
                full_url = urllib.parse.urljoin(base, line)
                lines[i] = (
                    "/proxy?url=" +
                    urllib.parse.quote(full_url, safe="")
                )

        playlist = "\n".join(lines)

        return Response(
            playlist,
            content_type="application/vnd.apple.mpegurl"
        )

    except Exception as e:
        return "Error: " + str(e), 500


@app.route("/proxy")
def proxy():

    url = request.args.get("url")

    if not url:
        return "Missing URL", 400

    try:
        r = requests.get(
            url,
            stream=True,
            timeout=30,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        return Response(
            r.iter_content(chunk_size=1024 * 64),
            status=r.status_code,
            content_type=r.headers.get(
                "Content-Type",
                "application/octet-stream"
            )
        )

    except Exception as e:
        return "Proxy error: " + str(e), 502


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(
        host="0.0.0.0",
        port=port
    )
