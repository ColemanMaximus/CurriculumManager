from os import system
from curriculum import CurricMetaData
from data_handler import get_instructors

vlc_path = r"C:\Applications\VideoLAN\VLC\vlc.exe"

class CurricDisplayWindow:
    def __init__(self, metadata: CurricMetaData = None, home_window = False):
        self.__metadata = metadata
        self.__home_window = home_window

    @property
    def metadata(self):
        return self.__metadata

    @property
    def is_home(self):
        return self.__home_window

    @property
    def curriculum(self):
        if self.__home_window:
            return None
        return _get_toplevel_parent(self.metadata)

    @property
    def header(self):
        if self.is_home:
            return "Curriculum Manager"

        header = self.metadata.name
        if self.metadata.parent and (self.metadata.name != self.metadata.parent.name):
            curric_name = self.curriculum
            curric_base_name = self.metadata.parent.name
            header += f" in {curric_name}/{curric_base_name}" \
                if curric_base_name != curric_name \
                else f" in {curric_name}"

        return header

    def display(self):
        system("cls")
        print(f"Viewing {self.header}")

        items = self.metadata
        if self.is_home:
            items = get_instructors()

            for index, instructor in enumerate(items, 1):
                print(f"- [{index}] {instructor} ({len(instructor.childs)} Curriculums)")
            return

        for child in items.childs:
            child_info = self.__progress(child) if child.subtype else ""
            print(f"- [{child.index}] {self.__status_icon(child)} {child} {child_info}")

        print(f"\nChoose a {self.metadata.subtype.lower()} to navigate by ID")
        print(_divider_ui())

    @staticmethod
    def __progress(child):
        completed = len([*filter(lambda child: child.is_complete, child.childs)])
        total = len(child.childs)
        percentage = round((completed / total) * 100)

        return f"({completed}/{total} {child.subtype}s) {percentage}%"

    @staticmethod
    def __status_icon(item):
        return _display_symbol_status(item.state)


class InteractiveDisplay:
    commands = ["q", "back", "complete", "uncomplete", "play"]

    def __init__(self, display: CurricDisplayWindow):
        self.__display = display
        self.run()

    @property
    def metadata(self):
        return self.__display.metadata

    def run(self):
        self.__display.display()
        while True:
            command = input("> ").lower().strip()

            if self.__is_command(command):
                parts = command.split(" ")
                cmd = parts[0]
                arg = parts[1] if len(parts) > 1 else None
                self.__process_command(cmd, arg)
                break

            childs = get_instructors() if self.__display.is_home else self.metadata.childs
            self.__display = CurricDisplayWindow(childs[int(command) - 1])
            break

        self.run()

    def __is_command(self, arg):
        return arg.lower().split(" ")[0] in self.commands

    def __process_command(self, cmd, arg):
        new_display = lambda metadata, home: CurricDisplayWindow(metadata, home)
        invalid_args = "Missing/Invalid ID in command arguments."

        if cmd == "back":
            if self.__display.is_home or not self.metadata.parent:
                self.__display = new_display(None, True)
                return

            self.__display = new_display(self.metadata.parent, False)
            return

        if cmd == "complete" or "uncomplete":
            state = 1 if cmd == "complete" else 0
            if not arg or not arg.isnumeric():
                print(invalid_args)
                return
            self.metadata.childs[int(arg) - 1].complete(state)

        if cmd == "play":
            if not arg or not arg.isnumeric():
                print(invalid_args)
                return

            system(f"{vlc_path} --fullscreen \"{self.metadata.childs[int(arg) - 1].path}\"")

def _get_toplevel_parent(metadata: CurricMetaData):
    if not metadata.parent:
        return metadata

    return _get_toplevel_parent(metadata.parent)


def _init_display():
    InteractiveDisplay(CurricDisplayWindow(None, True))


def _display_symbol_status(state: int):
    if state == 1:
        return "☒"
    return "☐"


def _divider_ui(length: int = 35):
    return "-" * length
