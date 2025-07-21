from flask import Flask, request, render_template_string
import requests
import subprocess

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>ReelsyDownload</title>
    <style>
        body { font-family: Arial; text-align: center; padding: 50px; background: #f5f5f5; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        input[type=text] { width: 80%; padding: 15px; font-size: 16px; border: 2px solid #ddd; border-radius: 5px; }
        button { padding: 15px 30px; margin-top: 15px; background: #e1306c; color: white; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; }
        button:hover { background: #c13584; }
        .result { margin-top: 30px; padding: 20px; border-radius: 5px; }
        .success { background: #d4edda; border: 1px solid #c3e6cb; color: #155724; }
        .error { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }
        .download-btn { display: inline-block; padding: 12px 24px; background: #28a745; color: white; text-decoration: none; border-radius: 5px; margin-top: 10px; }
        .download-btn:hover { background: #218838; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎬 ReelsyDownload</h1>
        <p>Download Instagram Reels, Posts, and IGTV videos</p>
        <form method="post">
            <input type="text" name="url" placeholder="Paste Instagram URL here (Reel/Post/IGTV)" required value="{{ url or '' }}" />
            <br/>
            <button type="submit">📥 Download Video</button>
        </form>
        {% if video_url %}
        <div class="result success">
            <h3>✅ Video Found!</h3>
            <p>Your video is ready for download</p>
            <a href="{{ video_url }}" class="download-btn" download>📱 Download Video</a>
            <br><small>Right-click and "Save as" if direct download doesn't work</small>
        </div>
        {% elif error %}
        <div class="result error">
            <h3>❌ {{ error }}</h3>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

def install_ytdlp():
    try:
        subprocess.run(['yt-dlp', '--version'], capture_output=True, check=True)
        return True
    except:
        try:
            subprocess.run(['pip', 'install', 'yt-dlp'], check=True)
            return True
        except:
            return False

def download_instagram_video(url):
    url = url.strip()
    if not any(domain in url for domain in ['instagram.com', 'instagr.am']):
        return None, "Please enter a valid Instagram URL"

    if not install_ytdlp():
        return None, "Failed to install yt-dlp"

    try:
        cmd = ['yt-dlp', '--no-download', '--print', 'url', '--format', 'best[ext=mp4]', url]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip(), None
        else:
            return None, "Could not extract video"
    except subprocess.TimeoutExpired:
        return None, "Timeout. Try again."
    except Exception as e:
        return None, f"Error: {str(e)}"

@app.route("/", methods=["GET", "POST"])
def index():
    video_url = None
    error = None
    url = None

    if request.method == "POST":
        url = request.form.get("url", "").strip()
        if not url:
            error = "Please enter a URL"
        else:
            video_url, error = download_instagram_video(url)

    return render_template_string(HTML_TEMPLATE, video_url=video_url, error=error, url=url)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
