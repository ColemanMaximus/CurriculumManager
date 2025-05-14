from pathlib import Path

class CurricMetaData:
    def __init__(self, parent, path: Path, curr_type: str, curr_subtype: str, index: int, state: int):
        self.__parent = parent
        self.__path = path
        self.__state = state
        self.__type = curr_type
        self.__subtype = curr_subtype
        self.__meta_childs = []
        self.__index = index

    @property
    def parent(self):
        return self.__parent

    @property
    def path(self):
        return self.__path

    @property
    def name(self):
        return _index_name_tuple(self.path.stem)[-1]

    @property
    def type(self):
        return self.__type

    @property
    def subtype(self):
        return self.__subtype

    @property
    def state(self):
        return self.__state

    @property
    def is_complete(self):
        return self.__state == 1

    @property
    def childs(self):
        if not self.__meta_childs:
            self.__init_childs()

        return self.__meta_childs

    @property
    def index(self):
        return self.__index

    def complete(self, state = 1):
        self.__state = state

        for child in self.childs:
            if state:
                child.complete()
                continue
            child.complete(0)

    def _add_child(self, child, index: int):
        self.__meta_childs.insert(index, child)
        self.__meta_childs.sort(key=lambda item: item.index)

    def __init_childs(self):
        if self.path.is_file():
            return

        for index, path in enumerate(self.path.iterdir(), 1):
            if path.name[0].isnumeric():
                index, _ = _index_name_tuple(path.name)

            child = None
            if self.subtype == "Curriculum":
                child = Curriculum(self, path, index)
            if self.subtype == "Category":
                child = CurricCategory(self, path, index)
            if self.subtype == "Lecture":
                child = CurricLecture(self, path, index)

            self._add_child(child, index - 1)

    def __eq__(self, other):
        return self.parent == other

class CurricInstructor(CurricMetaData):
    def __init__(self, path: Path, index: int):
        super().__init__(None, path, "Instructor", "Curriculum", index, 0)

    def __str__(self):
        return self.name


class Curriculum(CurricMetaData):
    def __init__(self, parent, path: Path, index: int):
        super().__init__(parent, path, "Curriculum", "Category", index, 0)

    def __str__(self):
        return self.name


class CurricCategory(CurricMetaData):
    def __init__(self, parent, path: Path, index: int):
        super().__init__(parent, path, "Category", "Lecture", index, 0)

    def __str__(self):
        return self.name


class CurricLecture(CurricMetaData):
    def __init__(self, parent, path: Path, index: int):
        super().__init__(parent, path, "Lecture", "", index, 0)

    def __str__(self):
        return self.name


def _index_name_tuple(name: str):
    try:
        splice = name.split("-")
        return int(splice[0]), splice[-1].strip()
    except ValueError:
        return 0, name


def _size_in_mb(file_bytes: int):
    return round(file_bytes / 1024 / 1024, 1)
