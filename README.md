# Picamip 
> Python simple Raspberry-Pi camera module web interface

[![PyPI version](https://badge.fury.io/py/picamip.svg)](https://badge.fury.io/py/picamip) 
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

This software runs on a RPi, it starts a webserver accessible via it's
IP address. The web interface has a preview screen, buttons to take 
picture, download and delete images.

![picamip UI](doc/picamip.png)

# Installing 
Install with pip
```
pip install picamip
```

# Running
The software can be started with
```
$ picamip
```
Then go to the interface at http://<Raspberry IP address>:8000

Additional options may be passed to the program:
```bash
picamip --help
usage: picamip [-h] [-p PICTURE_DIR] [-f FILES_PREFIX] [-t FLASK_TEMPLATE]
               [-s FLASK_STATIC] [-d DEFAULT_ROUTE] [-v]
               [host] [port]

picamip: Raspberry Pi IP Camera

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
                        Flask additional jinja2 templates directory
  -s FLASK_STATIC, --flask-static FLASK_STATIC
                        Flask additional static files directory
  -d DEFAULT_ROUTE, --default-route DEFAULT_ROUTE
                        Default root route. Eg: index.html
  -v, --version         show program's version number and exit
```

# License
> Python simple Raspberry-Pi camera module web interface
> Copyright (C) 2020 Luiz Eduardo Amaral <luizamaral306@gmail.com>
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
