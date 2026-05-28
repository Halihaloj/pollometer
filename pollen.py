import http.server
import socketserver
import webbrowser
import os

# Port where the local server will run
PORT = 8000
FILE_NAME = "pollen_dashboard.html"

# Ensure Python is looking in the exact folder where this script is saved
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Set up the server handler
Handler = http.server.SimpleHTTPRequestHandler

# Start the server
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Local server started on port {PORT}...")
    print("Press Ctrl+C in this terminal to stop the server.")
    
    # Automatically open the default web browser to our HTML file
    webbrowser.open(f"http://localhost:{PORT}/{FILE_NAME}")
    
    # Keep the server running
    httpd.serve_forever()