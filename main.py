import requests
from flask import Flask, Response, abort
from enum import Enum
from functools import lru_cache
import logging

app = Flask(__name__)

# Configuration
SITE_FOLDER = 'https://raw.githubusercontent.com/tokarotik/tokarotik.github.io/refs/heads/main'
TIMEOUT = 10  # Request timeout in seconds
CACHE_SIZE = 128  # Number of responses to cache

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MimeTypes(Enum):
    """MIME types for different file extensions"""
    TEXT = "text/plain; charset=utf-8"
    HTML = "text/html; charset=utf-8"
    CSS = "text/css; charset=utf-8"
    JS = "application/javascript; charset=utf-8"
    JSON = "application/json; charset=utf-8"
    WASM = "application/wasm"
    BIN = "application/octet-stream"
    PNG = "image/png"
    JPG = "image/jpeg"
    GIF = "image/gif"
    SVG = "image/svg+xml"
    ICO = "image/x-icon"


def get_mimetype(filename):
    """Determine MIME type based on file extension"""
    extension = filename.split('.')[-1].lower()
    
    mime_map = {
        'html': MimeTypes.HTML,
        'htm': MimeTypes.HTML,
        'css': MimeTypes.CSS,
        'js': MimeTypes.JS,
        'json': MimeTypes.JSON,
        'wasm': MimeTypes.WASM,
        'pck': MimeTypes.BIN,
        'bin': MimeTypes.BIN,
        'png': MimeTypes.PNG,
        'jpg': MimeTypes.JPG,
        'jpeg': MimeTypes.JPG,
        'gif': MimeTypes.GIF,
        'svg': MimeTypes.SVG,
        'ico': MimeTypes.ICO,
        'txt': MimeTypes.TEXT,
    }
    
    return mime_map.get(extension, MimeTypes.HTML)


def build_url(path):
    """Build the full URL for fetching content"""
    if not path.startswith('/'):
        path = '/' + path
    return SITE_FOLDER + path


@lru_cache(maxsize=CACHE_SIZE)
def fetch_content(url):
    """Fetch content from URL with caching and error handling"""
    try:
        logger.info(f"Fetching: {url}")
        response = requests.get(url, timeout=TIMEOUT)
        
        # Check if content exists
        if response.status_code == 404 or response.text == '404: Not Found':
            return None, 404
            
        response.raise_for_status()
        return response.content, response.status_code
        
    except requests.exceptions.Timeout:
        logger.error(f"Timeout fetching {url}")
        return None, 504
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching {url}: {str(e)}")
        return None, 502
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return None, 500


@app.route("/")
def index():
    """Serve the index page"""
    return pages('index.html')


@app.route("/favicon.ico")
def favicon():
    """Serve favicon or return empty response"""
    content, status = fetch_content(build_url('/favicon.ico'))
    
    if content is None or status == 404:
        # Return empty response if favicon not found
        return '', 204
    
    return Response(content, status=status, mimetype=MimeTypes.ICO.value)


@app.route("/<path:paths>")
def pages(paths):
    """Serve content from the remote repository"""
    # Security: Prevent path traversal
    if '..' in paths or paths.startswith('/'):
        abort(403)
    
    url = build_url(paths)
    content, status = fetch_content(url)
    
    if content is None:
        if status == 404:
            return serve_404()
        else:
            abort(status)
    
    mimetype = get_mimetype(paths).value
    return Response(content, status=200, mimetype=mimetype)


def serve_404():
    """Serve custom 404 page"""
    url = build_url('/404.html')
    content, status = fetch_content(url)
    
    if content is None:
        # Fallback 404 page if custom page not found
        return Response(
            "<h1>404 - Page Not Found</h1>",
            status=404,
            mimetype=MimeTypes.HTML.value
        )
    
    return Response(content, status=404, mimetype=MimeTypes.HTML.value)


@app.errorhandler(404)
def handle_404(e):
    """Handle 404 errors"""
    return serve_404()


@app.errorhandler(403)
def handle_403(e):
    """Handle forbidden access"""
    return Response(
        "<h1>403 - Forbidden</h1>",
        status=403,
        mimetype=MimeTypes.HTML.value
    )


@app.errorhandler(500)
def handle_500(e):
    """Handle internal server errors"""
    logger.error(f"Internal server error: {str(e)}")
    return Response(
        "<h1>500 - Internal Server Error</h1>",
        status=500,
        mimetype=MimeTypes.HTML.value
    )


@app.errorhandler(502)
def handle_502(e):
    """Handle bad gateway errors"""
    return Response(
        "<h1>502 - Bad Gateway</h1><p>Unable to fetch content from remote server.</p>",
        status=502,
        mimetype=MimeTypes.HTML.value
    )


@app.errorhandler(504)
def handle_504(e):
    """Handle gateway timeout"""
    return Response(
        "<h1>504 - Gateway Timeout</h1><p>The remote server took too long to respond.</p>",
        status=504,
        mimetype=MimeTypes.HTML.value
    )


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)