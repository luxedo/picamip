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
from setuptools import find_packages
from setuptools import setup

with open("README.md", "r") as fp:
    readme = fp.read()

with open("picamip/__init__.py", "r") as fp:
    version = (
        [
            line
            for line in fp.read().split("\n")
            if line.startswith("__version__")
        ][0]
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
    long_description_content_type="text/markdown",
    scripts=["bin/picamip"],
    python_requires=">=3.7",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=["picamera", "flask"],
    extras_require={"test": ["pytest", "coverage", "mypy", "pre-commit"]},
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
