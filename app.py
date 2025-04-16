from flask import Flask, request, redirect, abort
from urllib.parse import urlparse
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os

app = Flask(__name__)

# Load allowed domains from env (or hardcode)
ALLOWED_DOMAINS = os.getenv('ALLOWED_DOMAINS', 'todoapp-babe.onrender.com,www.todoapp-babe.onrender.com').split(',')

# Cache setup (1-hour timeout)
app.config['CACHE_TYPE'] = 'SimpleCache'
app.config['CACHE_DEFAULT_TIMEOUT'] = 3600
cache = Cache(app)

# Rate limiting (100 requests/minute per IP)
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per minute"]
)

@app.route('/proxy-youtube')
@cache.cached(timeout=300, query_string=True)  # Cache 5 mins per video ID
@limiter.limit("50 per minute")  # Stricter limit for this endpoint
def proxy_youtube():
    video_id = request.args.get('v')
    if not video_id:
        abort(400, description="Missing video ID parameter")
    
    referer = request.headers.get('Referer')
    if not referer:
        abort(403, description="Direct access not allowed")
    
    referer_domain = urlparse(referer).netloc
    if not any(allowed in referer_domain for allowed in ALLOWED_DOMAINS):
        abort(403, description="Access denied: YouTube can only be accessed via approved domains")
    
    return redirect(f'https://www.youtube.com/watch?v={video_id}')

@app.errorhandler(400)
@app.errorhandler(403)
@app.errorhandler(429)  # Rate limit exceeded
def handle_errors(error):
    return {
        "error": error.description,
        "status": error.code
    }, error.code