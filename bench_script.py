import json
import matplotlib
matplotlib.use("Agg")  # Используем бэкенд без GUI
import matplotlib.pyplot as plt
from pathlib import Path
from collections import Counter

# Загрузка JSON-файла
with open("problems_more_solutions.json", "r", encoding="utf-8") as f:
    data = json.load(f)
bench = []
for item in data:
    suf_list_st = [Path(i).suffix for i in item['statements']]
    suf_list_sol = [Path(i).suffix for i in item['solution_files']]
    task = {'name': item['name']}
    if '.tex' in suf_list_st:
        state = next((s for s in item['statements'] if s.endswith('.tex')), None)
        try:
        # Открываем файл в режиме чтения
            with open(state, 'r', encoding='utf-8') as file:
                content = file.read()
            task['statement'] = content
        
        except FileNotFoundError:
            print(f"Файл по пути {state} не найден.")
            exit(0)
        except Exception as e:
            try:
                with open(state, 'r', encoding='cp1251') as file:
                    content = file.read()
                task['statement'] = content
                
            except Exception as e1:
                print(f"Ошибка: {e1}")
                exit(0)
    else:
        continue  # no statement found
    if '.tex' in suf_list_sol:
        sol = next((s for s in item['solution_files'] if s.endswith('.tex')), None)
        try:
        # Открываем файл в режиме чтения
            with open(state, 'r', encoding='utf-8') as file:
                content = file.read()
            task['solution'] = content
        
        except FileNotFoundError:
            print(f"Файл по пути {sol} не найден.")
        except Exception as e:
            try:
                with open(sol, 'r', encoding='cp1251') as file:
                    content = file.read()
                task['solution'] = content
                
            except Exception as e1:
                print(f"Ошибка: {e1}")
                exit(0)
    for suf in ['.cpp', '.java', '.py', '.pas']:
        if suf in suf_list_sol:
            sol = next((s for s in item['solution_files'] if s.endswith(suf)), None)
            try:
                with open(sol, "r", encoding="utf-8") as file:
                    content = file.read()
                task['solution_' + suf[1:]] = content
            
            except FileNotFoundError:
                print(f"Файл по пути {sol} не найден.")
            except Exception as e:
                print(f"Ошибка: {e}")
                exit(0)
    if len(task) > 2:
        bench.append(task)
def make_unique(lst):
    unique_list = []
    for item in lst:
        if item not in unique_list:
            unique_list.append(item)
        else:
            print(item['name'])
    return unique_list

# Пример использования
ln = len(bench)  # 11
bench = make_unique(bench)
print(ln - len(bench))
with open('bench.json', "w", encoding="utf-8") as f:
        json.dump(bench, f, indent=4,ensure_ascii=False)
# with open("bench.json", "r", encoding="utf-8") as f:
#     data = json.load(f)
# for i in data[:6]:
#     print(i)   