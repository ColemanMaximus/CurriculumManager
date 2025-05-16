import sqlite3
from sqlite3 import Connection
from pathlib import Path
from abc import ABC, abstractmethod
from typing import List

from curriculum import CurricMetaData
from data_handler import get_instructors, courses_path

class Database(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def connect(self):
        pass

    def _no_connection_error(self):
        raise ConnectionError("Connection to the database hasn't been established.")


class SQLite3Database(Database):
    def __init__(self, connection_path: str | Path):
        self.__connection_path = connection_path
        self.__connection = None
        super().__init__()

    def connect(self):
        self.__connection = sqlite3.connect(self.__connection_path)

    @property
    def connection(self) -> Connection | None:
        if not self.is_connected:
            return None
        return self.__connection

    def execute(self, command: str, *params):
        if not self.is_connected:
            self._no_connection_error()
        return self.connection.execute(command, params)

    def save(self):
        if not self.is_connected:
            return
        self.__connection.commit()

    @property
    def is_connected(self) -> bool:
        if self.__connection:
            return True
        return False


class CurricDatabaseStore(SQLite3Database):
    def __init__(self, connection_path: str | Path):
        self.__instructors = []
        super().__init__(connection_path)
        self.connect()

    @property
    def get_instructors(self):
        if not self.is_connected:
            self._no_connection_error()

        if self.__instructors:
            return self.__instructors

        self.__index_metadata_all()
        return self.__instructors

    def __index_metadata_all(self):
        if not self.is_connected:
            self._no_connection_error()

        for instructor in get_instructors():
            self.__index_metadata(instructor)

            if instructor.childs:
                self.__index_metadata_rchilds(instructor.childs)

    def __index_metadata_rchilds(self, childs: List[CurricMetaData]):
        for child in childs:
            self.__index_metadata(child)

            if child.childs:
                self.__index_metadata_rchilds(child.childs)

    def __index_metadata(self, metadata: CurricMetaData):
        meta_type = metadata.subtype if metadata.parent else metadata.type

        command_values = "(?, ?, ?, ?)" \
            if metadata.parent else "(?, ?, ?)"
        command = f"INSERT INTO {meta_type}s VALUES{command_values}"

        self.execute(command)
        self.save()