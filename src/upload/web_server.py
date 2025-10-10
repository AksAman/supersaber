import time
import wifi
import config


def create_web_dashboard():
    """Create HTML dashboard for WiFi configuration"""
    with open("web_server.html", "r") as f:
        return f.read()


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
