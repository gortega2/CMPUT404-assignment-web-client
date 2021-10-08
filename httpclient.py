#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host_port(self,port):
        if port != None:
            return int(port)
        else:
            return 80

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        pattern = r'HTTP/[\d.]+ ([\d]+)'
        result = re.search(pattern, data)
        if result != None:
            return result.group(1)
        else:
            return None

    def get_headers(self,data):
        pattern = r"([\w\s\W]+)\r\n\r\n"
        result = re.search(pattern, data)
        if result != None:
            return result.group(1)
        else:
            return None

    def get_body(self, data):
        pattern = r"\r\n\r\n([\w\W\s]+)"
        result = re.search(pattern, data)
        if result != None:
            return result.group(1)
        else:
            return None #MIght change to None later


    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        code = 500
        body = ""
        query = urllib.parse.urlparse(url)
        port = self.get_host_port(query.port)
        msg = self.create_msg("GET", query.path, query.hostname, args=args)
        self.connect(query.hostname, port)
        self.sendall(msg)
        data = self.recvall(self.socket)
        self.close()
        code = int(self.get_code(data))
        headers = self.get_headers(data)
        body = self.get_body(data)
        #print(code, data)
        print(code, body)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""
        query = urllib.parse.urlparse(url)
        port = self.get_host_port(query.port)
        msg = self.create_msg("POST", query.path, query.hostname, args=args)
        self.connect(query.hostname, port)
        self.sendall(msg)
        data = self.recvall(self.socket)
        self.close()
        code = int(self.get_code(data))
        body = self.get_body(data)
        #print(code, data)
        print(code, body)
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
    def create_msg(self, command, path, host, args=None):
        if path == "":
            path = "/"
        data = command + " " + path + " HTTP/1.1\r\n"
        data += "Host: " + host + '\r\n'
        length = 0
        body = ''
        if command == 'GET':
            if args!= None:
                query = urllib.parse.urlencode(args)
                if "?" in path:
                    path = path + '&' + str(query)
                else:
                    path = path + '?' + str(query)
                data = command + " " + path + " HTTP/1.1\r\n"
                data += "Host: " + host + '\r\n' 

            data += "Connection: close\r\n"
            data += "Accept: text/html\r\n\r\n"
        else:
            data += "Content-type: application/x-www-form-urlencoded\r\n"
            if args != None:
                body = urllib.parse.urlencode(args)
                length = len(body.encode('utf-8'))
            data += "Content-length: {}{}".format(length,'\r\n\r\n')
            data += body
        return data

    def create_post_body(self, request_body, application_type):
        return

if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        for x in sys.argv:
            print("printing argvs", x)
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        for x in sys.argv:
            print("printing argvs", x)
        print(client.command( sys.argv[1] ))
