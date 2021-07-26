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
import asyncio
import importlib
import os
from os import path
import json
import subprocess
from tempfile import TemporaryDirectory
import time
import shutil

import flask
from werkzeug.exceptions import NotFound

from . import picamera, storage


ROOT = path.dirname(__file__)
BAD_REQUEST_MSG = "Could not process request"
NOT_FOUND_MSG = "File not found"
PICTURE_SUFFIX = ".jpg"
INDEX_DIGITS = 4

# flake8: noqa: C901
def build_app(
    camera: picamera.StreamPiCamera,
    picture_dir: str,
    files_prefix: str,
    flask_template: str,
    flask_static: str,
    flask_overload: str,
    default_route: str = "index.html",
) -> flask.Flask:
    """
    Builds flask app for picamip

    Args:
        camera (picamip.picamera.StreamPiCamera)
        picture_dir (str): Directory to store the pictures
        files_prefix (str): Stored pictures prefix
        flask_template (str): Additional templates directory
        flask_static (str): Additional static files directory
        flask_overload (str): Flask app functions overload
        default_route (str): Default root route. Eg: index.html
    Returns:
        app (flask.Flask): Picamip flaksk app
    """
    pictures_storage = storage.IndexedFilesStorage(
        picture_dir, files_prefix, PICTURE_SUFFIX, INDEX_DIGITS
    )
    app = flask.Flask(
        "picamip",
        template_folder=flask_template,
        static_folder=flask_static,
        static_url_path="/static",
    )

    # Run overloads
    if flask_overload is not None:
        if not path.isfile(flask_overload):
            raise ImportError(f"Module {flask_overload} not found")
        spec = importlib.util.spec_from_file_location(  # type: ignore
            "overload", flask_overload
        )
        overloads = importlib.util.module_from_spec(spec)  # type: ignore
        spec.loader.exec_module(overloads)
        overload_functions = {
            fname: overloads.__dict__[fname]
            for fname in dir(overloads)
            if fname.startswith("overload")
            and callable(overloads.__dict__[fname])
        }
        if len(overload_functions) == 0:
            raise ImportError(
                f"Module {flask_overload} has no overload functions"
            )
        for fn in overload_functions.values():
            fn(app, camera)
    urls = app.url_map.bind("localhost", "/")

    def try_route(r, methods=["GET", "POST"]):
        def wrap(fn):
            try:
                urls.match(r)
                app.logger.warning(
                    f"route '{r}' already overloaded. Skipping default"
                )
            except NotFound:
                app.add_url_rule(r, methods=methods, view_func=fn)

        return wrap

    # Declare default routes
    @try_route("/", methods=["GET"])
    def index():
        return flask.render_template(
            default_route,
            files=list(sorted(pictures_storage, key=lambda x: -x[0])),
        )

    @try_route("/files", methods=["GET"])
    def files():
        return flask.make_response(
            json.dumps(list(sorted(pictures_storage, key=lambda x: x[0])))
        )

    @try_route("/stream", methods=["GET"])
    def stream():
        resp = flask.Response(camera.stream_generator())
        resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers["Age"] = 0
        resp.headers["Cache-Control"] = "no-cache, private"
        resp.headers["Pragma"] = "no-cache"
        resp.headers[
            "Content-Type"
        ] = "multipart/x-mixed-replace; boundary=FRAME"
        return resp

    def _picture_get():
        index = flask.request.args.get("index")
        download = flask.request.args.get("download", "false").lower()
        as_attachment = download in ["true", "1"]
        if index == "-1":
            index = pictures_storage.last_index
        try:
            index = int(index)
        except TypeError:
            return flask.make_response(BAD_REQUEST_MSG, 400)
        if index not in pictures_storage:
            return flask.make_response(NOT_FOUND_MSG, 404)
        basename = path.basename(pictures_storage.make_filename(index))
        return flask.send_from_directory(
            picture_dir, basename, as_attachment=as_attachment
        )

    def _picture_post():
        filename = pictures_storage.next_filename
        try:
            camera.capture(filename)
        except picamera.exc.PiCameraValueError:
            app.logger.warning("To many clicks! Ignoring request...")
        except picamera.exc.PiCameraAlreadyRecording:
            app.logger.info("Ok! Camera already recording")
        return flask.redirect("/")

    @try_route("/picture", methods=["GET", "POST"])
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
            response = _picture_get()
        else:
            response = _picture_post()
        return response

    @try_route("/downloadAll", methods=["GET"])
    def downloadAll():
        with TemporaryDirectory() as tmpdir:
            zipfile = f"{files_prefix}.zip"
            pictures_storage.zip(path.join(tmpdir, zipfile))
            return flask.send_from_directory(
                tmpdir, zipfile, as_attachment=True
            )

    @try_route("/deleteAll", methods=["DELETE"])
    def deleteAll():
        try:
            pictures_storage.delete_all()
            return flask.make_response()
        except Exception:
            return flask.make_response("Unexpected Error", 500)

    @try_route("/delete", methods=["DELETE"])
    def deleteIndex():
        index = flask.request.args.get("index")
        try:
            index = int(index)
        except ValueError:
            return flask.make_response(BAD_REQUEST_MSG, 400)
        pictures_storage.delete_index(index)
        return flask.make_response()

    @try_route("/brewCoffee")
    def brewCoffee():
        return flask.make_response("I'm a teapot", 418)

    @try_route("/shutdown", methods=["POST"])
    def shutdown():
        sleep_then_shutdown(10)
        return flask.render_template("shutdown.html")

    def sleep_then_shutdown(timeout: int):
        def _shutdown():
            time.sleep(timeout)
            app.logger.warning("Shutting down!")
            subprocess.run(["sudo", "poweroff"])

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_in_executor(None, _shutdown)

    return app


def _linktree(src, dst):
    for f in os.listdir(src):
        _dst = path.join(dst, f)
        if path.exists(_dst):
            os.remove(_dst)
        os.symlink(path.join(src, f), _dst)


def run(
    host: str,
    port: int,
    picture_dir: str = "~/Pictures",
    files_prefix: str = "Picamip_",
    flask_template: str = None,
    flask_static: str = None,
    flask_overload: str = None,
    default_route: str = "index.html",
) -> None:
    """
    Builds and starts the flask app for picamip

    Args:
        host (str): RPi host
        port (int): host port
        picture_dir (str): Directory to store the pictures
        files_prefix (str): Stored pictures prefix
        flask_template (str): Additional templates directory
        flask_static (str): Additional static files directory
        flask_overload (str): Flask app functions overload
        default_route (str): Default root route. Eg: index.html
    """
    with picamera.StreamPiCamera() as camera, TemporaryDirectory() as template_tmp, TemporaryDirectory() as static_tmp:

        base_template = path.join(ROOT, "template")
        _linktree(base_template, template_tmp)
        if flask_template is not None:
            _linktree(path.abspath(flask_template), template_tmp)

        base_static = path.join(ROOT, "static")
        _linktree(base_static, static_tmp)
        if flask_static is not None:
            _linktree(path.abspath(flask_static), static_tmp)

        app = build_app(
            camera,
            picture_dir,
            files_prefix,
            template_tmp,
            static_tmp,
            flask_overload,
            default_route,
        )

        try:
            app.run(host=host, port=port, use_reloader=False)
        finally:
            if camera.recording:
                camera.stop_recording()
