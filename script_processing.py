from pathlib import Path
from typing import List, Optional
import json


def find_target_directory(start_path: Path):
    current_path = start_path

    while True:
        try:
            # Получаем список всех папок в текущей директории
            while current_path != current_path.parent:  # Проверяем, пока не достигнем корня
                folder_name = current_path.name.lower()
                if "archive" in folder_name or "ru-olymp" in folder_name:
                    return current_path  # Возвращаем путь до самой дальней подходящей папки
                current_path = current_path.parent  # Поднимаемся выше

            # Если нет папок или мы находимся в пустой папке, выходим
            # subdirs = [d for d in current_path.iterdir() if d.is_dir()]
            # if not subdirs:
            #     print("Целевая папка не найдена.")
            #     return None
            print("Целевая папка не найдена.")
            exit(0)     
            # Спускаемся в первую найденную папку (можно поменять логику, если нужно другой порядок)
            current_path = subdirs[0]
        except Exception as e:
            print('find_target_directory error:', e)
            exit(0)

class Task:
    def __init__(self, task_path: Path):
        """Инициализация объекта задачи.

        Атрибуты:
        task_path (Path): Путь к папке задачи.
        check_file (Optional[Path]): Путь к файлу check, если найден.
        statements (List[Path]): Список файлов условий (statement/problem), если найдены.
        tests_folder (Optional[Path]): Путь к папке с тестами, если найдена.
        cnt (int): Количество тестовых файлов с расширением .a.
        testmember (Optional[Path]): Путь к первому найденному тестовому файлу .a.
        solutions_folder (Optional[Path]): Путь к папке с решениями, если найдена.
        solution_files (List[Path]): Список путей к файлам решений (solution/tutorial).
        """
        self.task_path = task_path
        self.name = task_path.name
        self.check_file = self.find_check_file()
        self.statements = self.find_statements()
        self.tests_folder = self.find_tests_folder()
        self.cnt = self.count_test_answers()
        self.testmember = self.find_testmember()
        self.solutions_folder = self.find_solutions_folder()
        self.solution_files = self.find_solution_files()

    def find_file_excluding_files_dir(self, filename_stems: set, excluded_folder: str, valid_extensions=None) -> List[
        Path]:
        """Ищет файлы по их названиям, исключая папку 'files' на первом проходе."""
        found_files = []
        secondary_search = []
        # start_path = find_target_directory(self.task_path) if 'statement' in filename_stems else self.task_path

        start_path = self.task_path
        for file in start_path.rglob("*"):
            file_stem_lower = file.stem.lower()
            if file.is_file() and file.parent.name.lower() != excluded_folder.lower() and file_stem_lower in filename_stems:
                if valid_extensions is None or file.suffix.lower() not in valid_extensions:
                    found_files.append(file)
            elif file.is_file() and file.parent.name.lower() == excluded_folder.lower() and file_stem_lower in filename_stems:
                secondary_search.append(file)
        if 'statement' in filename_stems:
            filename_stems = [self.name]
            # print('find_file_excluding_files_dir: ', self.task_path)
            for file in Path(find_target_directory(self.task_path)).rglob("*"):
                # print('tf')
                file_stem_lower = file.stem.lower()
                if file.is_file() and file.parent.name.lower() != excluded_folder.lower() and file_stem_lower in filename_stems:
                    if valid_extensions is None or file.suffix.lower() not in valid_extensions:
                        found_files.append(file)
                elif file.is_file() and file.parent.name.lower() == excluded_folder.lower() and file_stem_lower in filename_stems:
                    secondary_search.append(file)
        if 'solution' in filename_stems:
            filename_stems = [self.name + '_as']
            # print('find_file_excluding_files_dir: ', self.task_path)
            for file in Path(find_target_directory(self.task_path)).rglob("*"):
                # print('tf')
                file_stem_lower = file.stem.lower()
                if file.is_file() and file.parent.name.lower() != excluded_folder.lower() and file_stem_lower in filename_stems:
                    if valid_extensions is None or file.suffix.lower() not in valid_extensions:
                        found_files.append(file)
                elif file.is_file() and file.parent.name.lower() == excluded_folder.lower() and file_stem_lower in filename_stems:
                    secondary_search.append(file)
        
        return found_files if found_files else secondary_search

    def find_check_file(self) -> Optional[Path]:
        """Ищет файл с названием 'check' только в корневой директории задачи."""
        for file in self.task_path.iterdir():
            if file.is_file() and file.stem.lower() == "check" and file.suffix.lower() != '.jar':
                return file
        return None

    def find_statements(self) -> List[Path]:
        """Ищет файлы условий задачи с названиями 'statement' или 'problem', игнорируя XML-файлы, избегая папки 'files' сначала."""
        return self.find_file_excluding_files_dir({"statement", "problem", self.name}, "files", {".xml"})

    def find_tests_folder(self) -> Optional[Path]:
        """Сначала ищет папку tests в корне, если не находит, то рекурсивно, избегая files сначала."""
        direct_path = self.task_path / "tests"
        if direct_path.exists() and direct_path.is_dir():
            return direct_path

        secondary_search = None
        for folder in self.task_path.rglob("tests"):
            if folder.is_dir() and folder.parent.name.lower() != "files":
                return folder
            elif folder.is_dir() and folder.parent.name.lower() == "files":
                secondary_search = folder

        return secondary_search

    def count_test_answers(self) -> int:
        """Подсчитывает количество файлов ответов (.a) в папке с тестами."""
        if self.tests_folder is None:
            return 0
        return sum(1 for file in self.tests_folder.rglob("*.a") if file.stem.isdigit())

    def find_testmember(self) -> Optional[Path]:
        """Находит первый файл с расширением .a, если такой существует."""
        if self.tests_folder is None:
            return None
        for file in self.tests_folder.rglob("*.a"):
            if file.stem.isdigit():
                return file
        return None

    def find_solutions_folder(self) -> Optional[Path]:
        """Ищет папку с решениями, которая может называться 'solution' или 'solutions'."""
        for folder_name in ("solution", "solutions"):
            folder_path = self.task_path / folder_name
            if folder_path.exists() and folder_path.is_dir():
                return folder_path
        return None

    def find_solution_files(self) -> List[Path]:
        """Ищет файлы с решением, содержащие 'solution' или 'tutorial' в названии, избегая 'files' на первом этапе."""
        found_files = []
        secondary_search = []

        for file in self.task_path.rglob("*"):
            file_stem_lower = file.stem.lower()
            if file.is_file() and file.parent.name.lower() != "files" and (
                    "solution" in file_stem_lower or "tutorial" in file_stem_lower):
                found_files.append(file)
        for file in find_target_directory(self.task_path).rglob('*'):
            file_stem_lower = file.stem.lower()
            if file.is_file() and file.parent.name.lower() != "files" and (
                    (self.name.lower() + '_as') in file_stem_lower or (file.name in [self.name + '.cpp', self.name + '.java', self.name + '.pas', self.name + '.py'])):
                found_files.append(file)
        return found_files if found_files else secondary_search

    def __repr__(self):
        """Возвращает строковое представление объекта Task."""
        return (f"Task({self.task_path})\n"
                f"  Check file: {self.check_file}\n"
                f"  Statements: {self.statements}\n"
                f"  Name of task: {self.name}"
                f"  Tests folder: {self.tests_folder}\n"
                f"  Number of .a files: {self.cnt}\n"
                f"  Test member: {self.testmember}\n"
                f"  Solutions folder: {self.solutions_folder}\n"
                f"  Solution files: {self.solution_files}")

    def to_dict(self):
        return {
            "task_path": str(self.task_path),
            "name": self.name,
            "check_file": str(self.check_file) if self.check_file else None,
            "statements": [str(p) for p in self.statements],
            "tests_folder": str(self.tests_folder) if self.tests_folder else None,
            "cnt": self.cnt,
            "testmember": str(self.testmember) if self.testmember else None,
            "solutions_folder": str(self.solutions_folder) if self.solutions_folder else None,
            "solution_files": [str(p) for p in self.solution_files],
        }

    @classmethod
    def from_dict(cls, data):
        task = cls(Path(data["task_path"]))
        task.check_file = Path(data["check_file"]) if data["check_file"] else None
        task.statements = [Path(p) for p in data["statements"]]
        task.tests_folder = Path(data["tests_folder"]) if data["tests_folder"] else None
        task.cnt = data["cnt"]
        task.testmember = Path(data["testmember"]) if data["testmember"] else None
        task.solutions_folder = Path(data["solutions_folder"]) if data["solutions_folder"] else None
        task.solution_files = [Path(p) for p in data["solution_files"]]
        return task


def save_tasks_to_json(tasks: List[Task], filename: str):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump([task.to_dict() for task in tasks], f, indent=4)


def load_tasks_from_json(filename: str) -> List[Task]:
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
        return [Task.from_dict(item) for item in data]


# Пример использования:
# tasks = [Task(Path("task1")), Task(Path("task2"))]
# save_tasks_to_json(tasks, "tasks.json")
# loaded_tasks = load_tasks_from_json("tasks.json")

def find_tasks(root_path: Path) -> List[Task]:
    """Рекурсивно ищет папки задач в указанной директории, но не заходит внутрь найденных задач."""
    tasks = []
    visited = set()
    num = 0

    for path in root_path.rglob("*"):
        if any(parent in visited for parent in path.parents):
            continue
        # Проверяем, является ли папка задачей (по наличию файла check.* только в её корне)
        if path.is_dir() and any(f.stem.lower() == "check" for f in path.iterdir() if f.is_file()):
            try:
                print(f"Task num: {num}")
                num += 1
                tasks.append(Task(path))
                visited.add(path)
                print(f"Task {tasks[-1].name} processed succesfully")
            except Exception as e:
              print(e)
              exit(0)

    return tasks


def main():
    """Точка входа в программу. Запрашивает путь у пользователя."""
    root_path = Path(input("Введите путь к директории: ").strip())
    if not root_path.exists() or not root_path.is_dir():
        print("Invalid path")
        return

    tasks = find_tasks(root_path)
    save_tasks_to_json(tasks, "problems_more_solutions.json")
    # for task in tasks:
        # print(task)


if __name__ == "__main__":
    main()