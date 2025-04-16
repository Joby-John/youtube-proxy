from flask import Flask, request, redirect, abort
from urllib.parse import urlparse
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os

app = Flask(__name__)

# Configuration
ALLOWED_DOMAINS = os.getenv('ALLOWED_DOMAINS', 'todoapp-babe.onrender.com,www.todoapp-babe.onrender.com').split(',')

# Cache setup
cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache', 'CACHE_DEFAULT_TIMEOUT': 300})

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per minute"]
)

@app.route('/proxy-youtube')
@cache.cached(timeout=300, query_string=True)
@limiter.limit("50 per minute")
def proxy_youtube():
    video_id = request.args.get('v')
    origin = request.args.get('origin', request.headers.get('Referer', ''))
    
    if not video_id:
        abort(400, description="Missing video ID parameter")
    
    parsed_origin = urlparse(origin).netloc if origin else ''
    if not any(allowed in parsed_origin for allowed in ALLOWED_DOMAINS):
        abort(403, description="Access denied: YouTube can only be accessed via approved domains")
    
    response = redirect(f'https://www.youtube.com/embed/{video_id}?autoplay=1&rel=0')
    response.headers['X-Frame-Options'] = f'ALLOW-FROM {origin}'
    response.headers['Content-Security-Policy'] = f"frame-ancestors {origin}"
    return response

@app.errorhandler(400)
@app.errorhandler(403)
@app.errorhandler(429)
def handle_errors(error):
    return {
        "error": error.description,
        "status": error.code
    }, error.code

# Development server (only runs if executed directly)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)