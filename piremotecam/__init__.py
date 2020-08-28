"""
Python simple Raspberry-Pi camera module web interface
Copyright (c) 2020 Luiz Eduardo Amaral <luizamaral306@gmail.com>

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the copyright holder nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""
import http.server
import io
import logging
import flask
from threading import Condition
from os import path
import os

import picamera


ROOT = path.dirname(__file__)


class StreamingOutput(io.BytesIO):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b"\xff\xd8"):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.truncate()
            with self.condition:
                self.frame = self.getvalue()
                self.condition.notify_all()
            self.seek(0)
        return super().write(buf)


class StreamingServer(http.server.ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, server_address, RequestHandlerClass, camera_output):
        RequestHandlerClass.camera_output = camera_output
        super().__init__(server_address, RequestHandlerClass)


def build_app(camera_output):
    # static_folder = path.join(ROOT, "static/")
    template_folder = path.join(ROOT, "template")
    app = flask.Flask(
        __name__, template_folder=template_folder
    )

    @app.route("/")
    def index():
        return flask.render_template("index.html")
    
    def stream_generator(camera_output):
        try:
            while True:
                with camera_output.condition:
                    camera_output.condition.wait()
                    frame = camera_output.frame
                yield (b"--FRAME\r\n" + 
                    b"Content-Type: image/jpeg\r\n\r\n" + 
                    frame + 
                    b"\r\n"
                )
        except Exception as e:
            logging.warning(
                "Removed streaming client %s: %s", self.client_address, str(e)
            )

    @app.route("/stream")
    def stream():
        resp = flask.Response(stream_generator(camera_output))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.headers["Age"] = 0
        resp.headers["Cache-Control"] = "no-cache, private"
        resp.headers["Pragma"] = "no-cache"
        resp.headers["Content-Type"] = "multipart/x-mixed-replace; boundary=FRAME"
        return resp
    return app


class PiCameraSingleton:
    instance = None
    def __new__(cls, *args, **kwargs):
        if not cls.instance:
            cls.instance = picamera.PiCamera(*args, **kwargs) 
        return cls.instance
    

def run(host, port):
    with PiCameraSingleton(resolution="640x480", framerate=24) as camera:
        camera_output = StreamingOutput()
        camera.start_recording(camera_output, format="mjpeg")
        app = build_app(camera_output)
        try:
            app.run(host=host, port=port, use_reloader=False)
        finally:
            camera.stop_recording()
