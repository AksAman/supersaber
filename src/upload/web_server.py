import time
import wifi
import config


def create_web_dashboard():
    """Create HTML dashboard for WiFi configuration"""
    return """
<!DOCTYPE html>
<html>
<head>
    <title>SuperSaber Configuration</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { 
            font-family: Arial, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0; 
            padding: 20px; 
            color: white;
            min-height: 100vh;
        }
        .container { 
            max-width: 400px; 
            margin: 0 auto; 
            background: rgba(255,255,255,0.1);
            padding: 30px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        }
        h1 { 
            text-align: center; 
            margin-bottom: 30px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .form-group { 
            margin-bottom: 20px; 
        }
        label { 
            display: block; 
            margin-bottom: 5px; 
            font-weight: bold;
        }
        input[type="text"], input[type="password"] { 
            width: 100%; 
            padding: 12px; 
            border: none; 
            border-radius: 8px; 
            font-size: 16px;
            box-sizing: border-box;
            background: rgba(255,255,255,0.9);
            color: #333;
        }
        button { 
            width: 100%; 
            padding: 12px; 
            background: #4CAF50; 
            color: white; 
            border: none; 
            border-radius: 8px; 
            font-size: 16px; 
            cursor: pointer;
            transition: background 0.3s;
        }
        button:hover { 
            background: #45a049; 
        }
        .status { 
            margin-top: 20px; 
            padding: 10px; 
            border-radius: 5px; 
            text-align: center;
        }
        .success { 
            background: rgba(76, 175, 80, 0.3); 
            border: 1px solid #4CAF50;
        }
        .error { 
            background: rgba(244, 67, 54, 0.3); 
            border: 1px solid #f44336;
        }
        .info {
            background: rgba(33, 150, 243, 0.3);
            border: 1px solid #2196F3;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>⚡ SuperSaber Config</h1>
        <form id="wifiForm">
            <div class="form-group">
                <label for="ssid">WiFi Network Name (SSID):</label>
                <input type="text" id="ssid" name="ssid" required>
            </div>
            <div class="form-group">
                <label for="password">WiFi Password:</label>
                <input type="password" id="password" name="password">
            </div>
            <button type="submit">Connect to WiFi</button>
        </form>
        <div id="status"></div>
    </div>
    
    <script>
        document.getElementById('wifiForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const ssid = document.getElementById('ssid').value;
            const password = document.getElementById('password').value;
            const statusDiv = document.getElementById('status');
            
            statusDiv.innerHTML = '<div class="status info">Connecting to WiFi...</div>';
            
            try {
                const response = await fetch('/configure', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ ssid: ssid, password: password })
                });
                
                if (response.ok) {
                    statusDiv.innerHTML = '<div class="status success">WiFi configured! Saber will restart and connect...</div>';
                } else {
                    statusDiv.innerHTML = '<div class="status error">Failed to configure WiFi. Please try again.</div>';
                }
            } catch (error) {
                statusDiv.innerHTML = '<div class="status error">Connection error. Please try again.</div>';
            }
        });
    </script>
</body>
</html>
"""


def handle_web_request(request):
    """Handle web requests for the dashboard"""
    try:
        if request.method == "GET":
            if request.path == "/":
                return create_web_dashboard()
            elif request.path == "/status":
                return '{"status": "online", "mode": "ap"}'
        
        elif request.method == "POST":
            if request.path == "/configure":
                # Parse JSON body
                content_length = int(request.headers.get("Content-Length", 0))
                body = request.raw_request[request.raw_request.find(b"\r\n\r\n") + 4:]
                if len(body) >= content_length:
                    body = body[:content_length]
                
                try:
                    import json
                    data = json.loads(body.decode())
                    ssid = data.get("ssid", "")
                    password = data.get("password", "")
                    
                    if ssid:
                        # Save WiFi credentials
                        config.save_wifi_credentials(ssid, password)
                        print(f"WiFi credentials saved: {ssid}")
                        
                        # Try to connect to WiFi
                        try:
                            wifi.radio.connect(ssid, password)
                            print(f"Connected to WiFi: {ssid}")
                            return '{"success": true, "message": "WiFi configured and connected!"}'
                        except Exception as e:
                            print(f"Failed to connect to WiFi: {e}")
                            return '{"success": false, "message": "WiFi saved but connection failed"}'
                    else:
                        return '{"success": false, "message": "SSID is required"}'
                        
                except Exception as e:
                    print(f"Error parsing request: {e}")
                    return '{"success": false, "message": "Invalid request format"}'
        
        return '{"error": "Not found"}'
        
    except Exception as e:
        print(f"Error handling request: {e}")
        return '{"error": "Internal server error"}'


class WebServer:
    """Simple web server for AP mode configuration"""
    
    def __init__(self):
        self.server_socket = None
        self.pool = None
        self.ssl_context = None
        self.last_web_check = time.monotonic()
    
    def start(self):
        """Start the web server"""
        import socketpool
        import ssl
        
        self.pool = socketpool.SocketPool(wifi.radio)
        self.ssl_context = ssl.create_default_context()
        
        # Create server socket
        self.server_socket = self.pool.socket(self.pool.AF_INET, self.pool.SOCK_STREAM)
        self.server_socket.setsockopt(self.pool.SOL_SOCKET, self.pool.SO_REUSEADDR, 1)
        self.server_socket.bind(("0.0.0.0", 80))
        self.server_socket.listen(1)
        
        print("Web server started on port 80")
        self.last_web_check = time.monotonic()
    
    def handle_requests(self):
        """Handle incoming web requests (non-blocking)"""
        current_time = time.monotonic()
        if current_time - self.last_web_check > 0.1:
            try:
                # Non-blocking check for connections
                self.server_socket.settimeout(0.01)
                client_socket, addr = self.server_socket.accept()
                
                # Read request
                request_data = b""
                while True:
                    try:
                        chunk = client_socket.recv(1024)
                        if not chunk:
                            break
                        request_data += chunk
                        if b"\r\n\r\n" in request_data:
                            break
                    except Exception:
                        break
                
                if request_data:
                    # Parse and handle request
                    request_str = request_data.decode()
                    lines = request_str.split('\r\n')
                    if lines:
                        method_line = lines[0]
                        method, path, _ = method_line.split(' ', 2)
                        
                        # Create simple request object
                        class SimpleRequest:
                            def __init__(self, method, path, headers, body):
                                self.method = method
                                self.path = path
                                self.headers = headers
                                self.raw_request = body
                        
                        headers = {}
                        for line in lines[1:]:
                            if ':' in line:
                                key, value = line.split(':', 1)
                                headers[key.strip()] = value.strip()
                        
                        request = SimpleRequest(method, path, headers, request_data)
                        response = handle_web_request(request)
                        
                        # Send response
                        http_response = f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n{response}"
                        client_socket.send(http_response.encode())
                
                client_socket.close()
                
            except Exception as e:
                # No connection or error, continue
                pass
            
            self.last_web_check = current_time
    
    def stop(self):
        """Stop the web server"""
        if self.server_socket:
            self.server_socket.close()
            self.server_socket = None
