#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
from gevent import monkey
from flask.wrappers import Response
if not monkey.is_module_patched('__builtin__'):
    monkey.patch_all() # causes problems if done twice

from flask import Flask, render_template, request, Blueprint, Response
from flask_sockets import Sockets
import requests
import os, time, sys
import psutil, subprocess
import threading
import socket
from websocket import create_connection, WebSocket, ABNF
from geventwebsocket.websocket import WebSocket as gWebSocket

FlexxBlueprint = Blueprint('FlexxApps', __name__, static_folder='static')
app = FlexxBlueprint
FlexxWS = Blueprint('FlexxWS', __name__)
sockets = FlexxWS

SITE_NAME = '127.0.0.1:8081/'
RUN_COMMAND = r'python.exe FlexxMain.py'
RUN_CWD = os.path.dirname(__file__)
FIND_STRING = 'FlexxMain.py'
STARTUPINFO = subprocess.STARTUPINFO()
STARTUPINFO.dwFlags = subprocess.STARTF_USESHOWWINDOW
STARTUPINFO.wShowWindow = 6 # SW_HIDE=0, SW_MINIMIZE=6

def keep_alive_thread():
    """Start a python script and keep it alive
    Note:
    Python process may change pid after creation, need to use the script name
    """
    #outfile = open('flexx_out.txt','w') #same with "w" or "a" as opening mode
    while(1):
        thread_found = False
        for proc in psutil.process_iter(['name', 'cmdline']): 
            if proc.name() == 'python.exe':
                cmdline = ' '.join(proc.info['cmdline'])
                if cmdline.find(FIND_STRING) != -1:
                    thread_found = True
                    if not threading.main_thread().is_alive():
                        print(f"Killing: {proc.info}")
                        proc.kill() # kill here if main tread has stopped but do not return until not found
                    break
        if not thread_found:
            if not threading.main_thread().is_alive():
                return # only return here
            process=subprocess.Popen(RUN_COMMAND, creationflags=subprocess.CREATE_NEW_CONSOLE, cwd=RUN_CWD, startupinfo=STARTUPINFO, stdout=sys.stdout, stderr=sys.stderr)
            time.sleep(10)
            continue
        for i in range(60):
            time.sleep(1)
            if not threading.main_thread().is_alive():
                break # delay killing to just after finding it in case it changed pid
            
thread1 = threading.Thread(target = keep_alive_thread)
thread1.start()

# @app.route('/img/<path:path>')
# def img_files(path):
#     return app.send_static_file('img/' + path)

@app.route('/<path:path>.map')
def map_files(path):
    return ''

@app.route('/', defaults={'path': ''}, methods=['GET','POST'])
@app.route('/<path:path>',methods=['GET','POST',"DELETE"])
def proxy(path):
    global SITE_NAME
    if path.startswith('assets'):
        path = f"flexx/{path}"
    excluded_headers = ['host', 'connection', 'pragma', 'cache-control', 'sec-fetch-site', 'sec-fetch-mode', 'sec-fetch-dest', 'referer', 'User-Agent']
    request_headers = {name: value for (name, value) in  request.headers.items() if name.lower() not in excluded_headers}
    if request.method=='GET':
        resp = requests.get(f'{request.scheme}://{SITE_NAME}{path}', headers = request_headers)
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        returned_headers = [(name, value) for (name, value) in  resp.headers.items() if name.lower() not in excluded_headers]
    elif request.method=='POST':
        resp = requests.post(f'{request.scheme}://{SITE_NAME}{path}',json=request.get_json())
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        returned_headers = [(name, value) for (name, value) in resp.headers.items() if name.lower() not in excluded_headers]
    elif request.method=='DELETE':
        resp = requests.delete(f'{request.scheme}://{SITE_NAME}{path}').content
    content_type=resp.headers.get('Content-Type',None)
    response = Response(resp.content, 
                        status=resp.status_code, 
                        headers=returned_headers,
                        mimetype=None,
                        content_type=content_type,
                        direct_passthrough=False)
    return response

def remote_handler(client_socket, remote_socket):
    while True:
        message = remote_socket.recv()
        if message == '' and not remote_socket.connected:
            break
        client_socket.send(message)
    client_socket.close()
    return

@sockets.route('/ws/<path:path>')
def proxy_socket(ws, path):
    # create connection to the remote:
    keep_headers = ['cookie']
    request_headers = {name: value for (name, value) in  request.headers.items() if name.lower() in keep_headers}
    pws = WebSocket(enable_multithread=True)
    pws.connect(f"ws://{SITE_NAME}flexx/ws/{path}", header=request_headers)
    # start remote handler:
    remote_handler_thread = threading.Thread(target=remote_handler,args=(ws, pws))
    remote_handler_thread.start()

    #pws = create_connection(f"ws://{SITE_NAME}flexx/{request.full_path}", header=request_headers, class_=MyWebSocket)
    while not ws.closed:
        message = ws.receive()
        if isinstance(message,(bytearray,bytes)):
            opcode = ABNF.OPCODE_BINARY
        elif isinstance(message, str):
            opcode = ABNF.OPCODE_TEXT
        elif message is None:
            assert ws.closed
            break
        else:
            raise ValueError('Unknown message type')
        pws.send(message, opcode=opcode)
    pws.close()
    return

if __name__ == '__main__':
    @app.route('/stop')
    def stop():
        global server
        server.stop()
        return 'stopping'

    app = Flask(__name__)
    app.secret_key = 'feca0226-1746-6666-92ac-1999e1eea085'
    ########### Register apps ###########
    app.register_blueprint(FlexxBlueprint, url_prefix='/flexx')
    ########### Register sockets ###########
    sockets = Sockets(app) # keep at the end
    sockets.register_blueprint(FlexxWS, url_prefix='/flexx')

    # from gevent import monkey; monkey.patch_all() # moved at beginning
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    import platform
    
    server = pywsgi.WSGIServer(('127.0.0.1', 5000), app, handler_class=WebSocketHandler)
    print("Server Started!")
    server.serve_forever()
