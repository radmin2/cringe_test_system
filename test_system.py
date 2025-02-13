#!/usr/bin/env python3

import json
import subprocess
import os
import pathlib
import shlex
from typing import Optional, List, Dict

TIME_LIMIT_MS = 2000  # Установленный лимит времени выполнения в миллисекундах

PATH_TO_RU_IFMO_TESTLIB = "C:\\libs"
PATH_TO_TESTLIB_H = "C:\\libs"
PATH_TO_TESTLIB_PAS = "C:\\libs"

class Task:
    def __init__(self, data: Dict):
        self.task_path = pathlib.Path(data["task_path"])
        self.check_file = pathlib.Path(data["check_file"]) if data.get("check_file") else None
        self.tests_folder = pathlib.Path(data["tests_folder"]) if data.get("tests_folder") else None
        self.cnt = int(data["cnt"])
        self.name = self.task_path.name  # Название задачи — последняя директория пути

    def __repr__(self):
        return (f"Task({self.task_path})\n"
                f"  Check file: {self.check_file}\n"
                f"  Tests folder: {self.tests_folder}\n"
                f"  Number of tests: {self.cnt}")


def compile_source(source_path: pathlib.Path) -> Optional[pathlib.Path]:
    """Компилирует исходный код в зависимости от его расширения и возвращает путь к исполняемому файлу."""
    ext = source_path.suffix
    if ext == '.exe' or ext == '.class':
        return source_path
    exec_path = source_path.with_suffix(".out")

    if ext == ".cpp":
        cmd = f'g++ -lm -fno-stack-limit -std=c++20 -I {shlex.quote(PATH_TO_TESTLIB_H)} -O2 -std=c++17 ' + str(source_path) + ' -o ' + str(exec_path)
    elif ext == ".java":
        cmd = f'javac -cp {shlex.quote(PATH_TO_RU_IFMO_TESTLIB)} ' + str(source_path)
        exec_path = source_path.with_suffix(".class")
    elif ext == ".pas":
        cmd = f"fpc -Fu {shlex.quote(PATH_TO_TESTLIB_PAS)}" + str(source_path) + ' -o ' + str(exec_path)
    else:
        print(f"Неизвестный тип файла: {source_path}")
        exit(0)
        return None
    result = subprocess.run(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print(result.stderr)
        print(f"Ошибка компиляции {source_path}:", result.stderr.decode())
        exit(0)
        return None

    return exec_path


def run_solution(exec_path: pathlib.Path, test_input: pathlib.Path, time_limit: int) -> Optional[str]:
    """Запускает исполняемый файл с входными данными теста и возвращает его вывод."""
    try:
        with open(test_input, "r") as inp:
            result = subprocess.run(
                [str(exec_path)], stdin=inp, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=time_limit / 1000
            )
            return result.stdout.decode().strip()
    except subprocess.TimeoutExpired:
        print(f"Тест {test_input} превысил лимит времени")
        exit(0)
        return None
    except Exception as e:
        print(f"Ошибка выполнения на тесте {test_input}: {e}")
        exit(0)
        return None


def check_output(checker: pathlib.Path, test_input: pathlib.Path, user_output: str, jury_output: pathlib.Path) -> int:
    """Запускает проверяющую программу и возвращает оценку за тест."""
    try:
        result = subprocess.run(
            ["wine", str(checker), str(test_input), "user_output.txt", str(jury_output)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        ) if checker.suffix == '.exe' else subprocess.run(
            [str(checker), str(test_input), "user_output.txt", str(jury_output)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        verdict = result.stderr.decode().strip()

        if result.returncode == 0:
            # print("tf")
            return 100
        else:
            print(verdict)
            return 0
            # if verdict == "_wa" or verdict == "_pe":
            #     return 0
            # elif verdict.startswith("_pc("):
            #     try:
            #         return int(verdict[4:-1]) * 100 // 200
            #     except ValueError:
            #         return 0
            # else:
            #     return 0
    except Exception as e:
        print(f"Ошибка проверки: {e}")
        exit(0)
        return 0


def load_tasks_from_json(json_path: str) -> Dict[str, Task]:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return {pathlib.Path(v["task_path"]).name: Task(v) for v in data}


def main(json_path: str, user_code: str = None):
    tasks = load_tasks_from_json(json_path)
    total_score = 0

    for task_name, task in tasks.items():
        print(f"Запуск проверки для задачи: {task_name}")

        if task.check_file:
            checker_exec = compile_source(task.check_file)
            if not checker_exec:
                print(f"Ошибка компиляции чекера для {task_name}.")
                continue
        else:
            print(f"Файл чекера не найден для {task_name}.")
            continue

        user_exec = compile_source(pathlib.Path(user_code))
        if not user_exec:
            print(f"Ошибка компиляции пользовательского кода для {task_name}.")
            continue

        task_score = 0

        if task.cnt == 0:
            print(f"No tests on task: {task_name}")
            exit(1)

        for i in range(1, task.cnt + 1):
            test_name = f"{i:02}"
            test_input = task.tests_folder / test_name
            test_output = task.tests_folder / f"{test_name}.a"

            if not test_input.exists() or not test_output.exists():
                print(f"Пропущен тест {test_name} для {task_name}.")
                continue

            user_output = run_solution(user_exec, test_input, TIME_LIMIT_MS)
            if user_output is None:
                print(f"Ошибка выполнения на тесте {test_name} для {task_name}.")
                continue

            with open("user_output.txt", "w") as f:
                f.write(user_output)
            print(f"test {i:02}: ", end='')
            score = check_output(checker_exec, test_input, user_output, test_output)
            task_score += score
        task_score /= task.cnt
        print(f"Баллы за задачу {task_name}: {task_score}")
        total_score += task_score

    print(f"Общий итоговый балл: {total_score}")

try:
    subprocess.run(["wine", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
except FileNotFoundError:
    print("Ошибка: Wine не установлен. Установите его с помощью 'sudo apt install wine' (для Debian/Ubuntu) или через пакетный менеджер вашей ОС.")
    exit(1)

if __name__ == "__main__":
    import sys

    if len(sys.argv) == 3:
        json_path, user_code = sys.argv[1], sys.argv[2]
    else:
        json_path = input("Введите путь к JSON-файлу с задачами: ").strip()
        json_path = "C:\\Users\\User\PycharmProjects\Lectures\\03.09.2024\pythonProject2\.venv\Lib\site-packages\problems.json"
        # C:\Users\User\PycharmProjects\Lectures\03.09.2024\pythonProject2\.venv\Lib\site-packages\problems.json
        user_code = input("Введите путь к файлу кода участника: ").strip()
        # user_code = "C:\\Users\\User\PycharmProjects\Lectures\\03.09.2024\pythonProject2\.venv\Lib\site-packages\\a.cpp"
        # C:\Users\User\PycharmProjects\Lectures\03.09.2024\pythonProject2\.venv\Lib\site-packages\a.cpp

    main(json_path)# , user_code)


# '''
# C:\\Users\\User\PycharmProjects\Lectures\03.09.2024\pythonProject2\.venv\Lib\site-packages\problems.json
# C:\\Users\\User\PycharmProjects\Lectures\03.09.2024\pythonProject2\.venv\Lib\site-packages\a.cpp
# '''