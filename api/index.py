from flask import Flask, request, Response
from curl_cffi import requests
from urllib.parse import urlparse

app = Flask(__name__)

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def proxy(path):
    url = request.url
    target_idx = url.find('http', 8)
    if target_idx == -1:
        return "Koyeb Proxy is running! Usage: https://your-app.koyeb.app/https://target-url.com/path", 200

    target_url = url[target_idx:]
    if target_url.startswith('https:/') and not target_url.startswith('https://'):
        target_url = 'https://' + target_url[7:]
    elif target_url.startswith('http:/') and not target_url.startswith('http://'):
        target_url = 'http://' + target_url[6:]

    # Clone headers and remove host, connection, content-length, cloudflare, and browser specific ones to prevent mismatches
    headers = {}
    exclude_headers = {
        'host', 'content-length', 'connection', 'transfer-encoding',
        'user-agent', 'sec-ch-ua', 'sec-ch-ua-mobile', 'sec-ch-ua-platform',
        'x-forwarded-for', 'x-real-ip', 'cf-connecting-ip', 'cf-ray', 'cf-visitor', 'cf-ew-via', 'cdn-loop'
    }
    for k, v in request.headers.items():
        if k.lower() not in exclude_headers:
            headers[k] = v

    try:
        parsed = urlparse(target_url)
        headers['Host'] = parsed.netloc
        headers['Referer'] = f"{parsed.scheme}://{parsed.netloc}/"
    except Exception:
        pass

    try:
        r = requests.request(
            method=request.method,
            url=target_url,
            headers=headers,
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=True,
            timeout=25,
            impersonate="chrome120"
        )
        
        # Prepare response headers, bypass hop-by-hop headers
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        resp_headers = [(k, v) for k, v in r.headers.items() if k.lower() not in excluded_headers]
        resp_headers.append(('Access-Control-Allow-Origin', '*'))
        resp_headers.append(('Access-Control-Allow-Methods', 'GET, HEAD, POST, OPTIONS, PUT, DELETE'))
        resp_headers.append(('Access-Control-Allow-Headers', '*'))

        return Response(r.content, r.status_code, resp_headers)
    except Exception as e:
        return f"Proxy Error: {str(e)}", 500
