import os
import requests
import zipfile
import patoolib
from urllib.parse import urlparse

def download_and_extract(archive_url, output_folder):
    """Скачивает архив (ZIP или RAR) и разархивирует его в отдельную папку."""
    try:
        response = requests.get(archive_url, stream=True)
        response.raise_for_status()
        
        # Определяем имя файла
        parsed_url = urlparse(archive_url)
        filename = os.path.basename(parsed_url.path)
        archive_path = os.path.join(output_folder, filename)
        extract_folder = os.path.join(output_folder, os.path.splitext(filename)[0])
        
        # Сохраняем архив
        with open(archive_path, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        
        # Создаем папку для разархивирования
        os.makedirs(extract_folder, exist_ok=True)
        
        # Разархивируем в зависимости от типа файла
        if filename.endswith('.zip'):
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(extract_folder)
        elif filename.endswith('.rar'):
            patoolib.extract_archive(archive_path, outdir=str(extract_folder))
        
        # Удаляем архив после разархивирования
        os.remove(archive_path)
        print(f"Файл {filename} успешно скачан и разархивирован в {extract_folder}.")
    except Exception as e:
        print(f"Ошибка при обработке {archive_url}: {e}")


def process_links(file_with_links, output_folder):
    """Читает ссылки из файла и скачивает архивы."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    with open(file_with_links, 'r', encoding='utf-8') as file:
        links = file.readlines()
    
    for link in links:
        archive_url = link.strip()
        if archive_url:
            download_and_extract(archive_url, output_folder)

# Укажите имя файла со ссылками и папку для разархивирования
links_file = "links.txt"  # Файл с ссылками
output_dir = "unzipped_files"  # Папка для разархивирования

process_links(links_file, output_dir)
