import sqlite3
from sqlite3 import Connection
from pathlib import Path
from abc import ABC, abstractmethod
from data_handler import get_instructors, courses_path

class Database(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def connect(self):
        pass

    def __no_connection_error(self):
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
            return
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


class CurrDatabaseStore(SQLite3Database):
    def __init__(self, connection_path: str | Path):
        self.__instructors = []
        super().__init__(connection_path)
        self.connect()

    @property
    def get_instructors(self):
        if not self.is_connected:
            self.__no_connection_error()

        if self.__instructors:
            return self.__instructors

        cursor = self.execute("SELECT * FROM Instructors")
        if not cursor:
            return self.__index_instructors()

        self.__instructors = cursor.fetchall()
        return self.__instructors

    def __index_instructors(self):
        if not self.is_connected:
            self.__no_connection_error()

        instructors = [
            (instructor.index, instructor.name, str(instructor.path))
            for instructor in get_instructors()
        ]

        for instructor in instructors:
            self.connection.execute("INSERT INTO Instructors Values(?, ?, ?)", instructor)
            self.save()