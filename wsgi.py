from app import app
from waitress import serve

if __name__ == "__main__":
    serve(
        app,
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 10000)),
        threads=4,
        channel_timeout=60
    )