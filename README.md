# flask_reverse_proxy_for_flexx
This is a working example of a reverse proxy implementation in flask to redirect web traffic to a flexx application.

### Why a reverse proxy?

Flexx is based on tornado which relies on the asyncio features of Python. This is incompatible with flask which to my knowledge cannot entertain directly an app based on asyncio calls.

### What is special about this reverse proxy?

It needs to implement bidirectional websocket connection from the client to the internal server.

### Any way to insert a Flexx app directly into flask?

Well maybe but I needed something quick and this is the best I found. If you want to try see: [https://pymotw.com/3/asyncio/executors.html](https://pymotw.com/3/asyncio/executors.html)

# Structure of the sample

## The flexx application

The flexx application in this case is a simple application based on a PyWidget that can run 
server side Python code. Any type of flexx application would do. The only requirement is that 
the flexx application is served at address http://localhost:8081 so that the reverse proxy 
can redirect requests from your server to this local address.

## The `DetachedFlexx.py` file

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

# License

Based on MIT license.
