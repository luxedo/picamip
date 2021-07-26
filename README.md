# Picamip 
> Python simple Raspberry-Pi camera module web interface

[![PyPI version](https://badge.fury.io/py/picamip.svg)](https://badge.fury.io/py/picamip) 
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

This software runs on a RPi, it starts a webserver accessible via it's
IP address. The web interface has a preview screen, buttons to take 
picture, download and delete images.

![picamip UI](https://raw.githubusercontent.com/luxedo/picamip/master/doc/picamip.png)

## Installing 
Install with pip
```
pip install picamip
```

## Running
The software can be started with
```
$ picamip
```
Then go to the interface at *http://&lt;Raspberry IP address&gt;:8000*

Additional options may be passed to the program:
```bash
picamip --help
usage: picamip [-h] [-p PICTURE_DIR] [-f FILES_PREFIX] [-t FLASK_TEMPLATE]
               [-s FLASK_STATIC] [-o FLASK_OVERLOAD] [-d DEFAULT_ROUTE] [-v]
               [host] [port]

picamip: Python simple Raspberry-Pi camera module web interface

positional arguments:
  host                  Server host
  port                  Server port

optional arguments:
  -h, --help            show this help message and exit
  -p PICTURE_DIR, --picture-dir PICTURE_DIR
                        Pictures storage directory
  -f FILES_PREFIX, --files-prefix FILES_PREFIX
                        Directory to store the pictures. Default: ~/Pictures
  -t FLASK_TEMPLATE, --flask-template FLASK_TEMPLATE
                        Flask additional jinja2 templates directory,
                        overwrites defaults.
  -s FLASK_STATIC, --flask-static FLASK_STATIC
                        Flask additional static files directory, overwrites
                        defaults.
  -o FLASK_OVERLOAD, --flask-overload FLASK_OVERLOAD
                        Flask app functions overload.
  -d DEFAULT_ROUTE, --default-route DEFAULT_ROUTE
                        Default root route. Eg: index.html
  -v, --version         show program's version number and exit
```

## Customizing
It's possible to customize the frontend by specifying another static
and template directories with: `--flask-static` and `--flask-template`.

Endpoints may be customized by declaring callback functions into a
python script and using `--flask-overload`. Overload functions must
start with `overload` and they receive an instance of `flask.Flask`
(`app` ) and an instance of`picamip.StreamPiCamera` (`camera`).

## Endpoints
Default endpoints are:
* **/** - GET: root route
* **/files** - GET: Gets the current storage indexes and filenames
* **/stream** - GET: Camera preview (mjpeg)
* **/picture** - GET: Gets an image of given index
  * Query params: index (int) - picture index, download (bool)- Downloads the image
* **/picture** - POST: Takes a picture from the camera
  * Query params: download (bool)- Downloads the image
* **/downloadAll** - GET: Downloads all the images as a zip file
* **/deleteAll** - DELETE: Deletes all images
* **/delete** - DELETE: Deletes an image of given index
  * Query params: index (int) - picture index
* **/shutdown** - POST: Shuts down the Raspberry Pi

## License
> Python simple Raspberry-Pi camera module web interface
> Copyright (C) 2021 Luiz Eduardo Amaral <luizamaral306@gmail.com>
> 
> This program is free software: you can redistribute it and/or modify
> it under the terms of the GNU General Public License as published by
> the Free Software Foundation, either version 3 of the License, or
> (at your option) any later version.
> This program is distributed in the hope that it will be useful,
> but WITHOUT ANY WARRANTY; without even the implied warranty of
> MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
> GNU General Public License for more details.
> You should have received a copy of the GNU General Public License
> along with this program.  If not, see <http://www.gnu.org/licenses/>.
