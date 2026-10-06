import os
import re

REPO_DIR = "."

VIEWPORT_TAG = '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
CSS_LINK = '<link rel="stylesheet" href="/ucheba/responsive.css">'

updated_count = 0
skipped_count = 0
scanned_count = 0

for root, dirs, files in os.walk(REPO_DIR):
    if ".git" in root:
        continue

    for file in files:
        # Проверяем файлы .html, .htm в любом регистре
        if file.lower().endswith(('.html', '.htm')) and file != "index.html":
            scanned_count += 1
            filepath = os.path.join(root, file)
            
            # Считываем файл с подбором кодировки
            content = None
            encoding_used = "utf-8"
            for enc in ["utf-8", "cp1251", "windows-1251", "latin1"]:
                try:
                    with open(filepath, "r", encoding=enc) as f:
                        content = f.read()
                    encoding_used = enc
                    break
                except UnicodeDecodeError:
                    continue

            if content is None:
                print(f"⚠️ Ошибка чтения файла: {filepath}")
                continue

            modified = False

            # 1. Проверяем тег viewport
            if "viewport" not in content.lower():
                if re.search(r'<head>', content, re.IGNORECASE):
                    content = re.sub(r'(<head>)', r'\1\n  ' + VIEWPORT_TAG, content, count=1, flags=re.IGNORECASE)
                    modified = True
                elif re.search(r'<html>', content, re.IGNORECASE):
                    content = re.sub(r'(<html>)', r'\1\n<head>\n  ' + VIEWPORT_TAG + '\n</head>', content, count=1, flags=re.IGNORECASE)
                    modified = True
                else:
                    content = VIEWPORT_TAG + "\n" + content
                    modified = True

            # 2. Проверяем подключение responsive.css
            if "responsive.css" not in content:
                if re.search(r'</head>', content, re.IGNORECASE):
                    content = re.sub(r'(</head>)', f'  {CSS_LINK}\n</head>', content, count=1, flags=re.IGNORECASE)
                    modified = True
                elif re.search(r'<body', content, re.IGNORECASE):
                    content = re.sub(r'(<body[^>]*>)', r'\1\n' + CSS_LINK, content, count=1, flags=re.IGNORECASE)
                    modified = True
                else:
                    content = CSS_LINK + "\n" + content
                    modified = True

            if modified:
                with open(filepath, "w", encoding=encoding_used) as f:
                    f.write(content)
                updated_count += 1
                print(f"✅ Обновлен: {filepath}")
            else:
                skipped_count += 1

print("\n" + "="*45)
print(f"📊 ИТОГИ СКАНИРОВАНИЯ:")
print(f"Найдено HTML/HTM файлов: {scanned_count}")
print(f"Успешно обновлено:       {updated_count}")
print(f"Пропущено (уже с CSS):   {skipped_count}")
print("="*45)
