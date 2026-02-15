import requests

from flask import Flask
from enum import Enum

app = Flask(__name__)
SITE_FOLDER = 'https://raw.githubusercontent.com/tokarotik/tokarotik.github.io/refs/heads/main'

class MimeTypes(Enum):
    TEXT = "text/plain;"
    HTML = "text/html;"
    CSS = "text/css;"
    JS = "application/javascript;"
    JSON = "application/json;"
    WASM = "application/wasm;"
    BIN = "application/octet-stream"
    PNG = "image/png"

def get_mimetype(filename):
    match filename.split('.')[-1]:
        case 'html': return MimeTypes.HTML
        case 'wasm': return MimeTypes.WASM
        case 'png': return MimeTypes.PNG
        case 'js': return MimeTypes.JS
        case 'pck': return MimeTypes.BIN
        case _: return MimeTypes.HTML

def file_mimetype(filename):
	return get_mimetype(filename).value

def get_url(url):
	if url[0] != '/':
		url = '/' + url
	return SITE_FOLDER + url

@app.route("/favicon.ico")
def nothing():
	return ';'

@app.route("/<path:paths>")
def pages(paths):
    url = get_url(paths)
    text = requests.get(url).text
    print(url)
    print(text)

    if text == '404: Not Found': page_not_found()
    
    return text, 200, {'Content-Type': file_mimetype(paths)}

def page_not_found():
	url = '/404.html'
	url = get_url(url)
	text = requests.get(url).text

	return text, 200, {'Content-Type': file_mimetype(url)}

@app.errorhandler(404)
def _page_not_found(e):
    return page_not_found()

if __name__ == '__main__':
    app.run()