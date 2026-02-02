#!/usr/bin/env python3
"""
Test script for Jupyter Server Proxy functionality.

This script creates a simple web server that can be accessed through
Jupyter Server Proxy to verify proxy configuration is working correctly.

Usage:
    1. In a Jupyter notebook environment with jupyter-server-proxy installed:
       ```python
       import test_jupyter_proxy
       test_jupyter_proxy.start_test_server(port=9999)
       ```
    
    2. Access via proxy URL: /proxy/9999/
    
    3. Or run standalone:
       python test_jupyter_proxy.py
"""

import http.server
import os
import socketserver
import threading
from pathlib import Path


class ProxyTestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler that serves a test page and logs requests."""
    
    def do_GET(self):
        """Handle GET requests with custom test page."""
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            
            # Get proxy prefix if available
            proxy_prefix = os.environ.get("JUPYTERHUB_SERVICE_PREFIX", "")
            if proxy_prefix and not proxy_prefix.endswith("/"):
                proxy_prefix += "/"
            
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Jupyter Server Proxy Test</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        .container {{
            background: rgba(255, 255, 255, 0.1);
            padding: 30px;
            border-radius: 10px;
            backdrop-filter: blur(10px);
        }}
        h1 {{
            color: #fff;
            text-align: center;
        }}
        .info {{
            background: rgba(255, 255, 255, 0.2);
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .success {{
            background: rgba(76, 175, 80, 0.3);
            border-left: 4px solid #4CAF50;
        }}
        code {{
            background: rgba(0, 0, 0, 0.3);
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
        .test-button {{
            background: #4CAF50;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            margin: 10px 5px;
        }}
        .test-button:hover {{
            background: #45a049;
        }}
        #api-result {{
            margin-top: 20px;
            padding: 10px;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 5px;
            min-height: 50px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎉 Jupyter Server Proxy Test Page</h1>
        
        <div class="info success">
            <strong>✅ Success!</strong> The proxy is working correctly.
        </div>
        
        <div class="info">
            <h3>Connection Details:</h3>
            <p><strong>Request Path:</strong> <code>{self.path}</code></p>
            <p><strong>Server Port:</strong> <code>{self.server.server_port}</code></p>
            <p><strong>Proxy Prefix:</strong> <code>{proxy_prefix or "Not set (direct access)"}</code></p>
            <p><strong>Access URL:</strong> <code>{proxy_prefix}proxy/{self.server.server_port}/</code></p>
        </div>
        
        <div class="info">
            <h3>Interactive Tests:</h3>
            <button class="test-button" onclick="testApi()">Test API Endpoint</button>
            <button class="test-button" onclick="testStatic()">Load Static Resource</button>
            <div id="api-result"></div>
        </div>
        
        <div class="info">
            <h3>Environment Variables:</h3>
            <ul>
                <li><strong>JUPYTERHUB_SERVICE_PREFIX:</strong> <code>{os.environ.get("JUPYTERHUB_SERVICE_PREFIX", "Not set")}</code></li>
                <li><strong>JUPYTERHUB_BASE_URL:</strong> <code>{os.environ.get("JUPYTERHUB_BASE_URL", "Not set")}</code></li>
                <li><strong>JUPYTERHUB_USER:</strong> <code>{os.environ.get("JUPYTERHUB_USER", "Not set")}</code></li>
            </ul>
        </div>
        
        <div class="info">
            <h3>How to Use:</h3>
            <ol>
                <li>If you see this page, jupyter-server-proxy is working! ✨</li>
                <li>Try the interactive tests above to verify API routing</li>
                <li>Check the browser console for detailed request information</li>
            </ol>
        </div>
    </div>
    
    <script>
        console.log('Jupyter Server Proxy Test Page loaded');
        console.log('Current URL:', window.location.href);
        console.log('Proxy prefix:', '{proxy_prefix}');
        
        function testApi() {{
            const resultDiv = document.getElementById('api-result');
            resultDiv.innerHTML = '<em>Loading...</em>';
            
            fetch('/api/test')
                .then(response => response.json())
                .then(data => {{
                    resultDiv.innerHTML = `<strong>API Response:</strong><br><code>${{JSON.stringify(data, null, 2)}}</code>`;
                }})
                .catch(error => {{
                    resultDiv.innerHTML = `<strong style="color: #ff6b6b;">Error:</strong> ${{error.message}}`;
                }});
        }}
        
        function testStatic() {{
            const resultDiv = document.getElementById('api-result');
            resultDiv.innerHTML = '<em>Checking static resource...</em>';
            
            fetch('/static/test.txt')
                .then(response => response.text())
                .then(data => {{
                    resultDiv.innerHTML = `<strong>Static Resource:</strong><br><code>${{data}}</code>`;
                }})
                .catch(error => {{
                    resultDiv.innerHTML = `<strong style="color: #ff6b6b;">Note:</strong> Static resource not found (expected for basic test)`;
                }});
        }}
    </script>
</body>
</html>
"""
            self.wfile.write(html_content.encode())
            return
        
        elif self.path == "/api/test":
            # Simple API endpoint for testing
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            
            response = {
                "status": "ok",
                "message": "API endpoint working through proxy",
                "port": self.server.server_port,
                "path": self.path
            }
            self.wfile.write(str(response).encode())
            return
        
        else:
            # For other paths, try to serve files if they exist
            super().do_GET()
    
    def log_message(self, format, *args):
        """Override to add custom logging."""
        print(f"[Proxy Test Server] {self.address_string()} - {format % args}")


def start_test_server(port=9999, background=True):
    """
    Start a test web server that can be accessed through Jupyter Server Proxy.
    
    Args:
        port (int): Port number to run the server on (default: 9999)
        background (bool): Run server in background thread (default: True)
    
    Returns:
        threading.Thread or None: Server thread if background=True, None otherwise
    """
    Handler = ProxyTestHandler
    
    try:
        with socketserver.TCPServer(("", port), Handler) as httpd:
            print(f"\n{'='*60}")
            print(f"  Jupyter Server Proxy Test Server")
            print(f"{'='*60}")
            print(f"  Server running on port {port}")
            print(f"  Access via proxy: /proxy/{port}/")
            
            # Check if we're in JupyterHub/Binder environment
            prefix = os.environ.get("JUPYTERHUB_SERVICE_PREFIX", "")
            if prefix:
                if not prefix.endswith("/"):
                    prefix += "/"
                print(f"  Full URL: {prefix}proxy/{port}/")
            
            print(f"{'='*60}\n")
            
            if background:
                def serve():
                    try:
                        httpd.serve_forever()
                    except KeyboardInterrupt:
                        print("\nShutting down test server...")
                
                thread = threading.Thread(target=serve, daemon=True)
                thread.start()
                return thread
            else:
                try:
                    httpd.serve_forever()
                except KeyboardInterrupt:
                    print("\nShutting down test server...")
                    return None
    
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"\n❌ Error: Port {port} is already in use.")
            print(f"   Try a different port or stop the existing server.\n")
        else:
            raise


def create_jupyter_server_config():
    """
    Generate a sample jupyter_server_config.py entry for this test server.
    This can be added to ~/.jupyter/jupyter_server_config.py
    """
    config = """
# Add this to ~/.jupyter/jupyter_server_config.py
# to automatically register the test server with jupyter-server-proxy

c.ServerProxy.servers = {
    'proxy-test': {
        'command': ['python', '-m', 'test_jupyter_proxy'],
        'port': 9999,
        'timeout': 30,
        'absolute_url': False,
        'launcher_entry': {
            'enabled': True,
            'title': 'Jupyter Proxy Test',
            'icon_path': '/static/base/images/favicon.ico'
        }
    }
}
"""
    print(config)
    return config


if __name__ == "__main__":
    import sys
    
    # Parse command line args
    port = 9999
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port number: {sys.argv[1]}")
            print("Usage: python test_jupyter_proxy.py [port]")
            sys.exit(1)
    
    # Run server in foreground when executed directly
    print("\n💡 Tip: Run this in a Jupyter notebook for automatic proxy integration:")
    print("   import test_jupyter_proxy")
    print("   test_jupyter_proxy.start_test_server(port=9999)\n")
    
    start_test_server(port=port, background=False)
