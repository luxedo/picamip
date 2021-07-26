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
from os import path
import os
import re
import typing
from zipfile import ZipFile


class IndexedFilesStorage:
    """
    Manages a file storage at `directory` with indexed files.
    The files names will match {prefix}{index}{suffix}, where `index`
    is a zero paded number with `number_digits` digits.
    Args:
        directory (str)
        prefix (str)
        suffix (str)
        index_digits (int): Number of digits to match
    """

    SANE_PREFIX_RE = r"^[a-zA-Z0-9\-_\(\).]+$"
    SANE_SUFFIX_RE = r"^[a-zA-Z0-9\-_\(\).]*$"

    def __init__(
        self,
        directory: str,
        prefix: str = "",
        suffix: str = "",
        index_digits: int = 4,
    ):
        if not path.isdir(directory):
            raise NotADirectoryError(
                f"directory {directory} for storage not found."
            )
        if not re.match(self.SANE_PREFIX_RE, prefix):
            raise ValueError(
                f"prefix '{prefix}' is not sane (doesn't match"
                + f" {self.SANE_PREFIX_RE})"
            )
        if not re.match(self.SANE_SUFFIX_RE, suffix):
            raise ValueError(
                f"suffix '{suffix}' is not sane (doesn't match "
                + f"{self.SANE_SUFFIX_RE})"
            )
        self.directory = directory
        self.prefix = prefix
        self.suffix = suffix
        self.index_digits = index_digits

    def __getitem__(self, index):
        return self.files[index]

    def __iter__(self):
        yield from self.files.items()

    def __contains__(self, index):
        return index in dict(self)

    def __len__(self):
        return len(self.files)

    def __repr__(self):
        return (
            "IndexedFileStorage(\n"
            + f"    directory='{self.directory}',\n"
            + f"    prefix='{self.directory}',\n"
            + f"    suffix='{self.suffix}',\n"
            + f"    index_digits={self.index_digits},\n"
            + ")"
        )

    @property
    def files(self) -> typing.Dict[int, str]:
        """
        Returns:
            files (list[tuple[int, str]]): List of tuples of the indexes
                as integers and the files
        """
        file_re = (
            rf"^{self.prefix}([0-9]{{{self.index_digits}}}){self.suffix}$"
        )
        files = {
            int(match[1]): match[0]
            for match in [
                re.match(file_re, f) for f in os.listdir(self.directory)
            ]
            if match is not None
        }
        return files

    @property
    def last_index(self) -> int:
        """
        Returns:
            last_index (int): Last (largest) index
            last_index_filename (int): Last (largest) filename
        """
        indexes = self.files.keys()
        if len(indexes) == 0:
            return 0
        return max(indexes)

    @property
    def next_filename(self) -> str:
        """
        Returns:
            next_filename (str): The filename with the next avaliable index
        """
        return self.make_filename(self.last_index + 1)

    def make_filename(self, index) -> str:
        """
        Args:
            index (int)
        Returns:
            filename (str): Absolute filename for given index
        """
        if len(str(index)) > self.index_digits:
            raise IndexError(
                f"Index out of range {self.prefix}(index){self.suffix}."
                + f" Index {index}, max index: {'9'*self.index_digits}"
            )
        return path.join(
            self.directory,
            f"{self.prefix}{str(index).zfill(self.index_digits)}{self.suffix}",
        )

    def zip(self, output: str) -> None:
        """
        Zips all files in the storage and writes to `output`

        Args:
            output (str): Target zip file
        """
        with ZipFile(output, "w") as zip_out:
            for filename in self.files.values():
                zip_out.write(
                    path.join(self.directory, filename), arcname=filename
                )

    def delete_index(self, index) -> bool:
        """
        Deletes the filename that has matching `index`

        Args:
            index (int)
        Returns:
            deleted (bool): True if the file was deleted successfully
                and False if the file doesn't exists
        """
        try:
            os.remove(path.join(self.directory, self.make_filename(index)))
            return True
        except FileNotFoundError:
            return False

    def delete_all(self) -> int:
        """
        Deletes all the files in the storage

        Returns:
            deleted (int): Number of deleted files
        """
        fileindexes = dict(self).keys()
        for index in fileindexes:
            self.delete_index(index)
        return len(fileindexes)
