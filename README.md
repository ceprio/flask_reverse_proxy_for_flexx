# flask_reverse_proxy_for_flexx
This is a working example of a reverse proxy implementation in flask to redirect web traffic to a flexx application.

### Why a reverse proxy?

Flexx is based on tornado which relies on the asyncio features of Python. This is incompatible with flask which to my knowledge cannot entertain directly an app based on asyncio calls.

### What is special about this reverse proxy?

It needs to implement bidirectional websocket connection from the client to the internal server.

### Any way to insert a Flexx app directly into flask?

Well maybe but I needed something quick and this is the best I found. If you want to try see: [https://pymotw.com/3/asyncio/executors.html](https://pymotw.com/3/asyncio/executors.html)

## Installation

1. Make sure you install requirements:
```
pip install -r requirements.txt
```

1. Check if the FlexxMain app works:
```
python FlexxMain.py
```
And go to [http://localhost:8081](http://localhost:8081) to see if the app is there. If it is, stop the server (ctrl-c).

1. Start flask with the reverse-proxy:
```
python DetachedFlexx.py
```
Then go to the Flask server: [http://localhost:5000/flexx](http://localhost:5000/flexx). You should see the app.


Go into the flexx folder and run `python DetachedFlexx.py`

BE WARNED: The installation of the websocket module is done with the websocket-client package. (pip install websocket-client)


## Structure of the sample

### The flexx application

The flexx application in this case is a simple application based on a PyWidget that can run 
server side Python code. Any type of flexx application would do. The only requirement is that 
the flexx application is served at address http://localhost:8081 so that the reverse proxy 
can redirect requests from your server to this local address.

### The `DetachedFlexx.py` file

This is where the magic appends.

1. Start a thread that will start the flexx application (see above) as an independent process script. That thead 
will also make sure that if the application stops for whatever reason, it is restarted. It will also 
kill the flexx process if the flask server is stopped.

2. Create a flask blueprint named flexx that will handle requests going to `your.server.com/flexx`
and redirect them to the flexx local port. Flexx uses websockets so redirections will be done for both 
standard requests and websockets

3. If this file is started as the main script, it will create a flask server based on gevent that will handle 
both the standart http requests and the websocket requests needed to handle the flexx application.

4. If you are integrating the blueprint into a larger app, just make sure your engine (gevent recommended) is 
handling websockets. 

## License

Based on MIT license.
