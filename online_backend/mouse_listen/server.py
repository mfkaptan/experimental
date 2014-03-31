import json
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
        self.mouse_listener = kwargs.pop('mouse_listener')
        super(_WSHandler, self).__init__(*args, **kwargs)

    def open(self):
        print "Connection opened"

    def on_message(self, message):
        # Send PNG using specified message_sender()
        if message == "PNG":
            self.write_message(self.message_sender())
        else:
            self.mouse_listener._update(message)

    def on_close(self):
        print "Connection closed"


class MouseListener():
    """MouseListener"""
    def __init__(self):
        self.x, self.y = 0, 0
        self.button = "up"
        self.isupdated = False
        self.button_isdown = False

    def _update(self, json_msg):
        msg = json.loads(json_msg)
        try:
            self._set_coord(msg)
        except:
            self._set_button(msg)

    def _set_coord(self, coord):
        self.x, self.y = int(coord["x"]), int(coord["y"])
        self.isupdated = True

    def get_coord(self):
        self.isupdated = False
        return self.x, self.y

    def _set_button(self, button):
        self.button = button["button"]
        if self.button == "down":
            self.button_isdown = True
        else:
            self.button_isdown = False

class Server(Thread):
    """Server for sending images to WebSocket (default port 9000)
    A user can specify his own message sender function
    Default message_sender is send_PNG.
    """
    def __init__(self, port=9000, message_sender=None):
        super(Server, self).__init__()
        self.PORT = port
        self.screenshot = []
        self.mouse_listener = MouseListener()
        # args
        args = {'message_sender': message_sender or self._send_PNG,
                'mouse_listener': self.mouse_listener}
        application = Application([(r'/', _WSHandler, args), ])
        self.http_server = HTTPServer(application)

    def run(self):
        self.http_server.listen(self.PORT)
        IOLoop.instance().start()

    def set_screenshot(self, screenshot):
        self.screenshot = screenshot

    # Default message sender function
    def _send_PNG(self):
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

    def get_mouse_listener(self):
        return self.mouse_listener
