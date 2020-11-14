import asyncio
import base64, tempfile, mmap
from flexx import app, ui, flx, event
import myui
import flexx
import io
import os, sys
import threading


class TheApp(ui.PyWidget):

    def init(self):
        content = open("instructions.md", encoding='utf-8').read()
        myui.Markdown(title='Instructions', style='background:#EAECFF;overflow-y: scroll;', content=content)


if __name__ == '__main__':
    import platform, sys, os
    from tornado.web import StaticFileHandler
    
    flexx.config.debug = True
    tornado_app = app.create_server(host="localhost", port=8081).app
    # Make use of Tornado's static file handler
    tornado_app.add_handlers(r".*", [(r"/theapp/img/(.*)", StaticFileHandler, {"path": "static/img"}), ])

    comp = flx.App(TheApp)
    comp.serve('theapp')
    app.start()

