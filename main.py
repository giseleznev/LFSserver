from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
import urllib.parse as urlparse
import json

oid_file = {'e88c695aaaf302e11ccb00c2b34c4da72e298b9d445f7961efc1decccaf03578' : 'pic.jpg'}
# dict oid:file name
# if new file added, dict should be updated

def JsonAnswer(post_data): # this function constructs a json response file
    f = open('1.json', 'r')
    msg = f.read()
    msg = json.loads(msg)
    msg['objects'][0]['oid'] = post_data['objects'][0]['oid']
    msg['objects'][0]['size'] = post_data['objects'][0]['size']
    msg['objects'][0]['actions']['download']['href'] = "http://localhost:8000/" + post_data['objects'][0]['oid']
    f = open('1.json', 'w')
    f.write(json.dumps(msg))

class HttpGetHandler(BaseHTTPRequestHandler):
    def do_GET(self):  # returns file which oid was asked in url
        print('Get answer')
        o = urlparse.urlparse(self.path)
        self.send_response(200)
        self.send_header('Content-type', 'application')
        self.end_headers()
        with open(oid_file[o.path[1:]], 'rb') as file:
            self.wfile.write(file.read())

    def do_POST(self): # returns json where href url leads to a needed oid
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        post_data = json.loads(post_data)  # dict made from POST request data
        print("WANT:")
        print(post_data['objects'][0]['oid'])
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        JsonAnswer(post_data)  # creates a json file to send as an answer
        with open('1.json', 'rb') as file:
            self.wfile.write(file.read())

def run(server_class=HTTPServer, handler_class=BaseHTTPRequestHandler):
  server_address = ("127.0.0.1", 8000)  
  httpd = server_class(server_address, handler_class)
  httpd.serve_forever()

run(handler_class=HttpGetHandler)