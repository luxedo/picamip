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
import logging
import io
from threading import Condition
from time import sleep
import typing

from picamera import *


class JpegStreamIO(io.BytesIO):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b"\xff\xd8"):
            self.truncate()
            with self.condition:
                self.frame = self.getvalue()
                self.condition.notify_all()
            self.seek(0)
        return super().write(buf)


class StreamPiCamera(PiCamera):
    """
    Wrapper class for picamera.PiCamera that extends it by adding a
    stream_generator method to yield streaming frames.
    """

    instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.instance:
            cls.instance = super().__new__(cls, *args, **kwargs)
        return cls.instance

    @property
    def stream_buffer(self) -> JpegStreamIO:
        if not hasattr(self, "_stream_buffer"):
            self._stream_buffer = JpegStreamIO()
        return self._stream_buffer

    def stream_generator(self) -> typing.Generator[bytes, None, None]:
        """
        Starts the camera and yields video stream frames
        """
        if not self.recording:
            self.start_recording(self.stream_buffer, format="mjpeg")
            sleep(1)
        while True:
            with self.stream_buffer.condition:
                self.stream_buffer.condition.wait()
                frame = self.stream_buffer.frame
            yield (
                b"--FRAME\r\n" + b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
            )

    def capture(self, filename: str) -> None:
        if self.recording:
            self.stop_recording()
        attributes = self.list_attributes()
        self.resolution = (2592, 1944)
        super().capture(filename)
        while self.recording:
            self.stop_recording()
        self.set_attributes(attributes)
        self.start_recording(self.stream_buffer, format="mjpeg")

    def list_attributes(self) -> dict:
        return {"resolution": self.resolution}

    def set_attributes(self, attributes: dict):
        for attr, value in attributes.items():
            setattr(self, attr, value)
