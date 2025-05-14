from pathlib import Path
from curriculum import CurricInstructor

courses_path = Path(r"C:\Users\Maximus\Documents\Programming Courses")
instructors = []

def get_instructors():
    if not courses_path.is_dir():
        raise NotADirectoryError("The given path needs to be a directory.")

    if not instructors:
        _init_instructors(courses_path)

    return instructors


def _init_instructors(path: Path):
    global instructors
    instructors = [
        CurricInstructor(directory, index)
        for index, directory in enumerate(path.iterdir(), 1)
        if directory.is_dir()
    ]