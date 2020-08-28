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
from threading import Condition
from os import path
import os

import picamera


ROOT = path.basename(__file__)


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


class StreamingHandler(http.server.CGIHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.routes = {
            "/": self.root_route,
            "/stream": self.stream_route,
        }
        self.static_dir = "./piremotecam/static"
        self.static = os.listdir(self.static_dir)
        super().__init__(*args, **kwargs)

    def do_GET(self):
        req_path = self.path.lstrip("/").split("?")[0] 
        if self.path in self.routes:
            self.routes[self.path]()
        elif req_path in self.static:
            self.static_route(req_path)
        else:
            self.send_error(404)
            self.end_headers()
    
    def static_route(self, filename):
        with open(path.join(self.static_dir, filename), "rb") as fp:
            content = fp.read()
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.send_header('Content-Length', len(content))
        self.end_headers()
        self.wfile.write(content)

    def root_route(self):
        self.send_response(301)
        self.send_header('Location', 'index.html')
        self.end_headers()

    def stream_route(self):
        self.send_response(200)
        self.send_header("Age", 0)
        self.send_header("Cache-Control", "no-cache, private")
        self.send_header("Pragma", "no-cache")
        self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=FRAME")
        self.end_headers()
        try:
            while True:
                with self.camera_output.condition:
                    self.camera_output.condition.wait()
                    frame = self.camera_output.frame
                self.wfile.write(b"--FRAME\r\n")
                self.send_header("Content-Type", "image/jpeg")
                self.send_header("Content-Length", len(frame))
                self.end_headers()
                self.wfile.write(frame)
                self.wfile.write(b"\r\n")
        except Exception as e:
            logging.warning(
                "Removed streaming client %s: %s", self.client_address, str(e)
            )


class StreamingServer(http.server.ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, server_address, RequestHandlerClass, camera_output):
        RequestHandlerClass.camera_output = camera_output
        super().__init__(server_address, RequestHandlerClass)


def run(address):
    with picamera.PiCamera(resolution="640x480", framerate=24) as camera:
        camera_output = StreamingOutput()
        camera.start_recording(camera_output, format="mjpeg")
        try:
            server = StreamingServer(address, StreamingHandler, camera_output)
            server.serve_forever()
        finally:
            camera.stop_recording()
