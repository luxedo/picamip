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
from os import path
import os
import re
from tempfile import TemporaryDirectory
import typing

import flask

from . import picamera, storage


ROOT = path.dirname(__file__)
BAD_REQUEST_MSG = "Could not process request"
NOT_FOUND_MSG = "File not found"
PICTURE_SUFFIX = ".jpg"
INDEX_DIGITS = 4


def build_app(
    camera: picamera.StreamPiCamera,
    pictures_dir: str,
    videos_dir: str,
    files_prefix: str,
) -> flask.Flask:
    """
    Builds flask app for piremotecam

    Args:
        camera (piremotecam.picamera.StreamPiCamera)
        pictures_dir (str): Directory to store the pictures
        videos_dir (str): Directory to store the videos
        files_prefix (str): Stored pictures/videos prefix
    Returns:
        app (flask.Flask): Piremotecam flaksk app
    """
    app = flask.Flask(__name__, template_folder=path.join(ROOT, "template"))
    pictures_storage = storage.IndexedFilesStorage(
        pictures_dir, files_prefix, PICTURE_SUFFIX, INDEX_DIGITS
    )

    @app.route("/")
    def index():
        return flask.render_template(
            "index.html",
            files=sorted(
                [(index, name) for index, name in pictures_storage.files.items()],
                key=lambda x: x[0],
            ),
        )

    @app.route("/stream")
    def stream():
        resp = flask.Response(camera.stream_generator())
        resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers["Age"] = 0
        resp.headers["Cache-Control"] = "no-cache, private"
        resp.headers["Pragma"] = "no-cache"
        resp.headers["Content-Type"] = "multipart/x-mixed-replace; boundary=FRAME"
        return resp

    def _picture():
        """
        Takes a picture

        Returns:
            filename (str): Picture file name, None if any error
        """
        filename = pictures_storage.next_filename
        try:
            camera.capture(filename)
            return filename
        except picamera.exc.PiCameraValueError:
            app.logger.warning("To many clicks! Ignoring request...")
        except picamrea.exc.PiCameraAlreadyRecording:
            app.logger.info("Ok! Camera already recording")

    def _picture_get():
        index = flask.request.args.get("index")
        try:
            index = int(index)
        except:
            return flask.make_response(BAD_REQUEST_MSG, 400)
        if not index in pictures_storage:
            return flask.make_response(NOT_FOUND_MSG, 404)
        basename = path.basename(pictures_storage.make_filename(index))
        return flask.send_from_directory(pictures_dir, basename, as_attachment=True)

    def _picture_post():
        filename = _picture()
        if filename is not None:
            download = flask.request.args.get("download")
            if download is not None:
                if download == "":
                    basename = path.basename(filename)
                    return flask.send_from_directory(
                        pictures_dir, basename, as_attachment=True
                    )
                return flask.make_response(BAD_REQUEST_MSG, 400)
            download = flask.request.args.get("download")
            return flask.redirect("/")
        else:
            return flask.make_response("Could not take a picture", 500)

    @app.route("/picture", methods=["GET", "POST"])
    def picture():
        """
        GET:
            Gets a stored picture

            Query parameters
                index (int): Index of the picture

        POST:
            Takes a picture and stores it.

            Query parameters:
                download: Download the file (optional)
        """
        if flask.request.method == "GET":
            return _picture_get()
        else:
            return _picture_post()

    @app.route("/downloadAll", methods=["GET"])
    def downloadAll():
        with TemporaryDirectory() as tmpdir:
            zipfile = f"{files_prefix}.zip"
            pictures_storage.zip(path.join(tmpdir, zipfile))
            return flask.send_from_directory(tmpdir, zipfile, as_attachment=True)

    @app.route("/deleteAll", methods=["DELETE"])
    def deleteAll():
        try:
            pictures_storage.delete_all()
            return flask.make_response()
        except:
            return flask.make_response("Unexpected Error", 500)

    @app.route("/delete", methods=["DELETE"])
    def deleteIndex():
        index = flask.request.args.get("index")
        try:
            index = int(index)
        except:
            return flask.make_response(BAD_REQUEST_MSG, 400)
        try:
            pictures_storage.delete_index(index)
            return flask.make_response()
        except:
            return flask.make_response("Unexpected Error", 500)

    @app.route("/brewCoffee")
    def brewCoffee():
        return flask.make_response("I'm a teapot", 418)

    return app


def run(
    host: str,
    port: int,
    pictures_dir: str = "~/Pictures",
    videos_dir: str = "~/Videos",
    files_prefix: str = "Piremotecam",
) -> None:
    """
    Builds and starts the flask app for piremotecam

    Args:
        host (str): RPi host
        port (int): host port
        camera (piremotecam.picamera.StreamPiCamera)
        pictures_dir (str): Directory to store the pictures
        videos_dir (str): Directory to store the videos
        files_prefix (str): Stored pictures/videos prefix
    """
    # storages = ("internal", "download")
    # if storage not in storages:
    #     raise ValueError(f"storage must be {'or '.join(storages)}, got {storage}")

    with picamera.StreamPiCamera() as camera:
        app = build_app(camera, pictures_dir, videos_dir, files_prefix)
        try:
            app.run(host=host, port=port, use_reloader=False)
        finally:
            if camera.recording:
                camera.stop_recording()
