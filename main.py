from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
import urllib.parse as urlparse
import json
import subprocess

prepare_json = "{ \"transfer\": \"basic\", \"objects\": []}"

example_json = "{ \"objects\": [{ \"oid\": \"1111111\", \"size\": 123, \"actions\": {\"download\": {\"href\": \"\",\"expires_in\": 3600}}}]}"

answer_json = ""


oid_file = {} # dict oid:file name
# if new file added, dict should be updated by UpdatedDict

def UpdateDict(): # this function constructs a valid dict
    process = subprocess.Popen(["git", "lfs", "ls-files"], stdout=subprocess.PIPE)
    output = process.communicate()[0]
    ListAnswer = output.split()
    for Index in range(0, len(ListAnswer), 3):
        FileName = ListAnswer[Index+2].decode("utf-8")
        process2 = subprocess.Popen(["git", "lfs", "pointer", "--file=" + FileName], stdout=subprocess.PIPE)
        output2 = process2.communicate()[0]
        ListAnswer2 = output2.split()
        Oid = ListAnswer2[3].decode("utf-8")[7:]
        print(Oid)
        print(FileName)
        oid_file.update([(Oid, FileName)])

def JsonAnswer(post_data): # this function constructs a json response file 
    msg_prepare = prepare_json
    msg_example = example_json
    for i in post_data['objects']:
        if i['oid'] in oid_file:
            msg_prepare['objects'].append(dict(json.loads(msg_example)['objects'][0])) # adds a {...} object for a file we have
            msg_prepare['objects'][-1]['actions']['download']['href'] = "http://localhost:8000/" + i['oid'] #"https://bucketforserver.s3.eu-north-1.amazonaws.com/" + oid_file[i['oid']]
            msg_prepare['objects'][-1]['oid'] = i['oid']
            msg_prepare['objects'][-1]['size'] = i['size']
            print("Preparing: ", msg_prepare)
        else:
            msg_prepare['objects'].append(dict(json.loads(msg_example)['objects'][1])) # adds a {...error...} object for a file we do not have
            msg_prepare['objects'][-1]['oid'] = i['oid']
            msg_prepare['objects'][-1]['size'] = i['size']
    f = open('answer.json', 'w')
    f.write(json.dumps(msg_prepare))
    return 'answer.json'

class HttpGetHandler(BaseHTTPRequestHandler):
    def do_GET(self):  # returns file which oid was asked in url

        o = urlparse.urlparse(self.path)
        self.send_response(200)
        self.send_header('Content-type', 'application')
        self.end_headers()
        print('Get answer:' + o.path[1:])
        with open(oid_file[o.path[1:]], 'rb') as file:
            self.wfile.write(file.read())    
        
    def do_POST(self): # returns json where href url leads to a needed oid
        UpdateDict()
        print("WANT:")
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        post_data = json.loads(post_data)  # dict made from POST request data
        for i in post_data['objects']:
            print(i['oid'])
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        # creates a json file to send as an answer
        with open(JsonAnswer(post_data), 'rb') as file:
            self.wfile.write(file.read())

def run(server_class=HTTPServer, handler_class=BaseHTTPRequestHandler):
  server_address = ("127.0.0.1", 8000)
  httpd = server_class(server_address, handler_class)
  httpd.serve_forever()

run(handler_class=HttpGetHandler)
