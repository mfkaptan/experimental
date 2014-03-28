import json
import base64
import cStringIO
from tornado.websocket import WebSocketHandler
from tornado.web import Application
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from PIL import Image
from threading import Thread


class _WSHandler(WebSocketHandler):
    def __init__(self, *args, **kwargs):
        self.message_sender = kwargs.pop('message_sender')
        super(_WSHandler, self).__init__(*args, **kwargs)

    def open(self):
        print "Connection opened"

    def on_message(self, message):
        # Send PNG using specified message_sender() on every message
        self.write_message(self.message_sender())

    def on_close(self):
        print "Connection closed"


class Server(Thread):
    """Server for sending images to WebSocket (default port 9000)
    A user can specify his own message sender function
    Default message_sender is send_PNG.
    """
    def __init__(self, port=9000, message_sender=None):
        super(Server, self).__init__()
        self.PORT = port
        self.screenshot = []
        # Message sender arg
        arg = {'message_sender': message_sender or self.send_PNG}
        application = Application([(r'/', _WSHandler, arg), ])
        self.http_server = HTTPServer(application)

    def run(self):
        self.http_server.listen(self.PORT)
        IOLoop.instance().start()

    def set_screenshot(self, screenshot):
        self.screenshot = screenshot

    def send_PNG(self):
        """
        Default message_sender function
        Returns base64 encoded PNG image in json
        """
        img = Image.fromarray(self.screenshot)

        # Save the image onto buffer
        buf = cStringIO.StringIO()
        img.save(buf, "PNG")
        # Open it again and encode with base64
        base64_PNG = buf.getvalue().encode("base64")
        buf.close()

        return json.dumps({"image": base64_PNG})
