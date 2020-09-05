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
import io
import re

from setuptools import find_packages
from setuptools import setup

with open("README.md", "r") as fp:
    readme = fp.read()

with open("picamip/__init__.py", "r") as fp:
    version = (
        [line for line in fp.read().split("\n") if line.startswith("__version__")][0]
        .split("=")[1]
        .strip()
        .strip('"')
    )

setup(
    name="picamip",
    version=version,
    url="https://github.com/luxedo/picamip",
    license='BSD 3-clause "New" or "Revised License"',
    maintainer="Luiz Eduardo Amaral",
    maintainer_email="luizamaral306@gmail.com",
    description="Simple Raspberry Pi camera http server interface",
    long_description=readme,
    long_description_content_type='text/markdown',
    scripts=["bin/picamip"],
    python_requires=">=3.7",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=["picamera", "flask"],
    extras_require={"test": ["pytest", "coverage"]},
    keywords=["raspberrypi", "camera", "http"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.7",
        "Topic :: Multimedia :: Graphics :: Capture :: Digital Camera",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
    ],
)
