"""
Python simple Raspberry-Pi camera module web interface
Copyright (C) 2021 Luiz Eduardo Amaral <luizamaral306@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import io
from threading import Condition
from time import sleep
import typing

from picamera import PiCamera  # type: ignore


class JpegStreamIO(io.BytesIO):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.frame = None
        self.condition = Condition()

    def write(self, buf: bytes):
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
                b"--FRAME\r\n"
                + b"Content-Type: image/jpeg\r\n\r\n"
                + frame
                + b"\r\n"
            )

    def capture(self, filename: str) -> None:
        if self.recording:
            self.stop_recording()
        attributes = self.list_attributes()
        self.resolution = (2592, 1944)
        self.start_preview()
        sleep(2)
        super().capture(filename)
        self.stop_preview()
        while self.recording:
            self.stop_recording()
        self.set_attributes(attributes)
        self.start_recording(self.stream_buffer, format="mjpeg")

    def list_attributes(self) -> dict:
        return {"resolution": self.resolution}

    def set_attributes(self, attributes: dict):
        for attr, value in attributes.items():
            setattr(self, attr, value)
