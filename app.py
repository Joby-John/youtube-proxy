from flask import Flask, request, redirect, abort
from urllib.parse import urlparse
import os

app = Flask(__name__)

# Allowed domains (replace with your website)
ALLOWED_DOMAINS = ['todoapp-babe.onrender.com', 'www.todoapp-babe.onrender.com']

@app.route('/proxy-youtube')
def proxy_youtube():
    # Get video ID from query parameter
    video_id = request.args.get('v')
    if not video_id:
        abort(400, description="Missing video ID parameter")
    
    # Verify the request comes from allowed domain
    referer = request.headers.get('Referer')
    if not referer:
        abort(403, description="Direct access not allowed")
    
    referer_domain = urlparse(referer).netloc
    if not any(allowed in referer_domain for allowed in ALLOWED_DOMAINS):
        abort(403, description="Access denied: YouTube can only be accessed via approved domains")
    
    # Redirect to YouTube (or you could fetch and modify the response)
    return redirect(f'https://www.youtube.com/watch?v={video_id}')

@app.errorhandler(400)
@app.errorhandler(403)
def handle_errors(error):
    return {
        "error": error.description,
        "status": error.code
    }, error.code

