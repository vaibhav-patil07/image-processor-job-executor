from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import time

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        else:
            self.send_response(404)
            self.end_headers()

def ping_loop():
    """Send a ping every 30 seconds to keep connection alive"""
    while True:
        try:
            time.sleep(30)
            print("⏰ Ping - Keepalive")
        except Exception as e:
            print(f"❌ Ping error: {e}")

if __name__ == "__main__":
    # Start ping thread in background
    ping_thread = threading.Thread(target=ping_loop, daemon=True)
    ping_thread.start()
    print("✅ Ping thread started (30s interval)")
    
    server = HTTPServer(("0.0.0.0", 8080), HealthHandler)
    print("✅ Health server running on port 8080")
    server.serve_forever()