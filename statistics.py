import json
import matplotlib
matplotlib.use("Agg")  # Используем бэкенд без GUI
import matplotlib.pyplot as plt
from pathlib import Path
from collections import Counter

# Загрузка JSON-файла
with open("problems_more_statements.json", "r", encoding="utf-8") as f:
    data = json.load(f)
print(len(data))
# # График 1: Распределение cnt
cnt_over_100 =  0
for item in data:
    if item['cnt'] >= 100:
        print(item['task_path'])
        cnt_over_100 += 1
cnt_values = [item["cnt"] for item in data]
cnt_counts = Counter(cnt_values)

plt.figure(figsize=(8, 5))
plt.bar(cnt_counts.keys(), cnt_counts.values(), color="skyblue", edgecolor="black")
plt.xlabel("cnt (количество тестов)")
plt.ylabel("Количество задач")
plt.title("Распределение количества тестов")
plt.xticks(sorted(cnt_counts.keys()))
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.savefig("graph_1.png")  # Сохранение в файл
plt.close()

# График 2: Количество словарей, где statements содержит .tex файлы
count_tex = sum(
    any(Path(statement).suffix == ".tex" for statement in item["statements"])
    for item in data
)

# График 3: Количество словарей, где statements не пустой
count_statements = sum(bool(item["statements"]) for item in data)

# Столбчатая диаграмма
plt.figure(figsize=(6, 5))
plt.bar(["С .tex", "С statements"], [count_tex, count_statements], color=["blue", "green"])
plt.ylabel("Количество задач")
plt.title("Количество задач с statements и .tex")
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.savefig("graph_2.png")  # Сохранение в файл
plt.close()

print("Графики сохранены как graph_1.png и graph_2.png")

# Загрузка JSON-файла
pon = sum([int('.tex' in [Path(item).suffix for item in i['statements']]) for i in data])
print(sum([int('.tex' in [Path(item).suffix for item in i['statements']]) for i in data]))
s = 0
for i in data:
    if '.tex' not in [Path(item).suffix for item in i['statements']]:
        print(i['task_path'])
        continue
    s += int('.tex' in [Path(item).suffix for item in i['solution_files']])
print(s, s / pon)
# Подсчет количества файлов check по расширениям



cnt_not_tex = 0
cnt_tex = 0
cnt_interact = 0
for item in data:
    suf_list = [Path(i).suffix for i in item['statements']]
    if '.tex' in suf_list:
        state = next((s for s in item['statements'] if s.endswith('.tex')), None)
        try:
        # Открываем файл в режиме чтения
            with open(state, 'r', encoding='utf-8') as file:
                content = file.read()
            # Проверяем наличие подстроки "интеракт"
            if "интеракт" in content:
                cnt_interact += 1
                print(state)
                print("Подстрока 'интеракт' найдена в файле.")
            # else:
            #     print("Подстрока 'интеракт' не найдена в файле.")
        
        except FileNotFoundError:
            print(f"Файл по пути {state} не найден.")
        except Exception as e:
            try:
                with open(state, 'r', encoding='cp1251') as file:
                    content = file.read()
                # Проверяем наличие подстроки "интеракт"
                if "интеракт" in content:
                    cnt_interact += 1
                    print(state)
                    print("Подстрока 'интеракт' найдена в файле.")
                # print(f"Произошла ошибка: {e}")
                # print(state)
                # exit(0  )
            except Exception as e1:
                print(f"Ошибка: {e1}")
                exit(0)

    # else:
    #     cnt_not_tex += 1
    elif '.pdf' in suf_list or '.doc' in suf_list or '.html' in suf_list:
        cnt_not_tex += 1
print(cnt_not_tex, cnt_tex, cnt_interact)




check_extensions = [
    Path(i).suffix for item in data for i in item['check_file']
]

# # Подсчет количества вхождений каждого расширения
ext_counts = Counter(check_extensions)
print(len(data))
# Вывод статистики
print("Статистика по расширениям файлов statement:")
for ext, count in sorted(ext_counts.items(), key=lambda x: -x[1]):
    print(f"{ext or '[без расширения]'}: {count}")
# print(cnt_over_100)