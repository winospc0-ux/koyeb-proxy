import requests
from flask import Flask, request, Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# User-Agent to mimic a real browser
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def proxy(path):
    # Try to get the URL from the path or the query string
    # Koyeb might pass it differently
    full_path = request.full_path
    if full_path.startswith('/http'):
        url = full_path[1:]
    elif path.startswith('http'):
        url = path
    else:
        # Check if the URL is passed as a query parameter 'url'
        url = request.args.get('url')
        
    if not url:
        return "Please provide a URL. Example: /https://google.com", 200

    # Clean up URL
    if '?' in url and url.count('http') > 1:
        # Handle cases where the URL itself has query params
        pass 

    headers = {k: v for k, v in request.headers if k.lower() not in ['host', 'content-length']}
    headers['User-Agent'] = UA

    try:
        resp = requests.request(
            method=request.method,
            url=url,
            headers=headers,
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=True,
            timeout=30
        )
        
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items()
                   if name.lower() not in excluded_headers]

        return Response(resp.content, resp.status_code, headers)
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
