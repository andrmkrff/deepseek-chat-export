#!/usr/bin/env python3
import json
import html as html_module
import re
import os
import sys
import glob
import time
from datetime import datetime
from collections import deque

def find_json_files():
    """Поиск JSON файлов в текущей директории"""
    json_files = glob.glob("*.json")
    
    excluded = ['package.json', 'tsconfig.json', 'node_modules']
    json_files = [f for f in json_files if not any(ex in f.lower() for ex in excluded)]
    
    return json_files

def select_json_file():
    """Интерактивный выбор JSON файла"""
    json_files = find_json_files()
    
    if not json_files:
        print("❌ JSON файлы не найдены в текущей директории!")
        print("Поместите файл conversations.json в ту же папку, где находится скрипт.")
        return None
    
    if len(json_files) == 1:
        print(f"✅ Найден файл: {json_files[0]}")
        return json_files[0]
    
    print("📁 Найдено несколько JSON файлов:")
    for i, filename in enumerate(json_files, 1):
        size = os.path.getsize(filename)
        print(f"  {i}. {filename} ({size:,} байт)")
    
    print(f"  {len(json_files) + 1}. Ввести имя файла вручную")
    print(f"  {len(json_files) + 2}. Отмена")
    
    while True:
        try:
            choice = input("\nВыберите файл (номер): ").strip()
            
            if not choice:
                continue
                
            if choice.isdigit():
                choice_num = int(choice)
                
                if 1 <= choice_num <= len(json_files):
                    selected_file = json_files[choice_num - 1]
                    print(f"✅ Выбран файл: {selected_file}")
                    return selected_file
                elif choice_num == len(json_files) + 1:
                    manual_file = input("Введите имя файла: ").strip()
                    if os.path.exists(manual_file):
                        print(f"✅ Файл найден: {manual_file}")
                        return manual_file
                    else:
                        print(f"❌ Файл не найден: {manual_file}")
                elif choice_num == len(json_files) + 2:
                    print("🚫 Отмена.")
                    return None
                else:
                    print(f"❌ Неверный номер. Введите от 1 до {len(json_files) + 2}")
            else:
                if os.path.exists(choice):
                    print(f"✅ Файл найден: {choice}")
                    return choice
                else:
                    print(f"❌ Файл не найден: {choice}")
                    
        except KeyboardInterrupt:
            print("\n🚫 Прервано пользователем.")
            return None
        except Exception as e:
            print(f"❌ Ошибка: {e}")

def export_with_full_markdown():
    """Экспорт с полной поддержкой Markdown и ветвлений"""
    
    json_file = select_json_file()
    if not json_file:
        return
    
    print(f"\n📖 Загрузка данных из {json_file}...")
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            chats = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка чтения JSON файла: {e}")
        print("Файл поврежден или имеет неверный формат.")
        return
    except Exception as e:
        print(f"❌ Ошибка загрузки файла: {e}")
        return
    
    if not isinstance(chats, list):
        chats = [chats]
    
    print(f"✅ Загружено чатов: {len(chats)}")
    
    base_name = os.path.splitext(json_file)[0]
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"{base_name}_export_{timestamp}.html"
    
    print(f"⚙️  Создание HTML с аккордеоном для веток...")
    
    try:
        # Используем timestamp для предотвращения кэширования
        cache_buster = str(int(time.time()))
        html = create_html_full_markdown(chats, json_file, timestamp, cache_buster)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"\n🎉 Файл успешно создан!")
        print(f"📄 Имя файла: {output_file}")
        print(f"📊 Чатов экспортировано: {len(chats)}")
        print(f"🔄 Cache buster: {cache_buster}")
        
        # Инструкция по очистке кэша
        print("\n🔧 Если не видите изменений в браузере:")
        print("   1. Нажмите Ctrl+F5 (Windows/Linux) или Cmd+Shift+R (Mac)")
        print("   2. Или откройте консоль разработчика (F12) и:")
        print("      - Перейдите на вкладку Network")
        print("      - Поставьте галочку 'Disable cache'")
        print("      - Перезагрузите страницу")
        
        if input("\n📂 Открыть файл сейчас? (y/n): ").lower() == 'y':
            open_in_browser(output_file)
            
    except Exception as e:
        print(f"❌ Ошибка при создании HTML: {e}")
        import traceback
        traceback.print_exc()

def open_in_browser(filename):
    """Открытие файла в браузере"""
    try:
        import webbrowser
        # Добавляем параметр для предотвращения кэширования
        full_path = os.path.abspath(filename)
        webbrowser.open(f'file://{full_path}')
        print("🌐 Открываю в браузере...")
    except Exception as e:
        print(f"⚠️ Не удалось открыть в браузере: {e}")
        print(f"   Откройте файл вручную: {filename}")

def extract_all_branches(chat):
    """Извлечение всех веток из чата"""
    mapping = chat.get('mapping', {})
    root = mapping.get('root', {})
    
    # Начинаем с детей root
    start_nodes = root.get('children', [])
    
    if not start_nodes:
        return []
    
    # Собираем все ветки
    all_branches = []
    
    for start_node in start_nodes:
        # Для каждого стартового узла находим все возможные пути
        branches_from_start = find_all_paths(mapping, start_node)
        all_branches.extend(branches_from_start)
    
    # Убираем дубликаты (если ветки пересекаются)
    unique_branches = []
    seen = set()
    
    for branch in all_branches:
        # Создаем ключ для сравнения веток
        branch_key = '|'.join([str(msg.get('node_id', '')) for msg in branch])
        if branch_key not in seen:
            seen.add(branch_key)
            unique_branches.append(branch)
    
    return unique_branches

def find_all_paths(mapping, start_node_id):
    """Нахождение всех возможных путей от начального узла"""
    if start_node_id not in mapping:
        return []
    
    all_paths = []
    
    # Используем DFS для обхода всех веток
    stack = [(start_node_id, [])]
    
    while stack:
        current_id, current_path = stack.pop()
        
        if current_id not in mapping:
            continue
        
        node = mapping[current_id]
        
        # Извлекаем сообщение из текущего узла
        message_data = extract_message_with_node_id(node, current_id)
        if message_data:
            new_path = current_path + [message_data]
        else:
            new_path = current_path
        
        # Получаем детей текущего узла
        children = node.get('children', [])
        
        if not children:
            # Дошли до конца ветки
            all_paths.append(new_path)
        else:
            # Продолжаем обход для каждого ребенка
            for child_id in children:
                stack.append((child_id, new_path.copy()))
    
    return all_paths

def extract_message_with_node_id(node, node_id):
    """Извлечение сообщения с добавлением ID узла"""
    message = node.get('message', {})
    if not isinstance(message, dict):
        return None
    
    # Определяем роль по содержимому или структуре
    role = determine_role(message, node_id)
    
    # Извлекаем контент
    content = extract_content_from_fragments(message)
    
    if not content:
        return None
    
    return {
        'node_id': node_id,
        'role': role,
        'content': content,
        'parent': node.get('parent'),
        'children': node.get('children', [])
    }

def determine_role(message, node_id):
    """Определение роли сообщения - улучшенная версия"""
    # Пробуем получить роль из author
    author = message.get('author', {})
    if isinstance(author, dict):
        role = author.get('role', '')
        if role:
            return role
    
    # Пробуем определить по содержимому модели
    model = message.get('model', '')
    if model:
        model_lower = model.lower()
        if any(x in model_lower for x in ['gpt', 'assistant', 'deepseek', 'claude']):
            return 'assistant'
        elif any(x in model_lower for x in ['user', 'human']):
            return 'user'
    
    # Пробуем определить по порядковому номеру узла
    # В DeepSeek обычно: нечетные узлы (1, 3, 5) - пользователь, четные (2, 4, 6) - ассистент
    try:
        node_num = int(node_id) if node_id.isdigit() else 0
        if node_num > 0:
            return 'user' if node_num % 2 == 1 else 'assistant'
    except:
        pass
    
    # Если не определили, вернем unknown
    return 'unknown'

def extract_content_from_fragments(message_data):
    """Извлечение контента из fragments"""
    fragments = message_data.get('fragments', [])
    
    if not isinstance(fragments, list):
        return ""
    
    content_parts = []
    
    for fragment in fragments:
        if isinstance(fragment, dict):
            if fragment.get('type') == 'text' and 'content' in fragment:
                content_parts.append(str(fragment['content']))
            elif 'text' in fragment:
                content_parts.append(str(fragment['text']))
            elif 'content' in fragment:
                content_parts.append(str(fragment['content']))
        elif isinstance(fragment, str):
            content_parts.append(fragment)
    
    return '\n'.join(content_parts).strip()

def organize_branches_by_depth(branches):
    """Организация веток по глубине/поколению"""
    if not branches:
        return []
    
    # Группируем ветки по первому сообщению
    grouped = {}
    
    for branch in branches:
        if not branch:
            continue
        
        first_msg = branch[0]
        first_node_id = first_msg.get('node_id', '')
        
        if first_node_id not in grouped:
            grouped[first_node_id] = []
        
        grouped[first_node_id].append(branch)
    
    # Сортируем ветки по количеству сообщений (самые длинные первые)
    result = []
    for first_node_id, branch_list in grouped.items():
        sorted_branches = sorted(branch_list, key=len, reverse=True)
        result.extend(sorted_branches)
    
    return result

def create_html_full_markdown(chats, source_filename, timestamp, cache_buster):
    """HTML с полной поддержкой Markdown и аккордеоном для веток"""
    
    total_chats = len(chats)
    export_time = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
    source_name = os.path.basename(source_filename)
    
    html = f'''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Экспорт чатов DeepSeek - {total_chats} диалогов</title>
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <style>
        /* Cache buster: {cache_buster} */
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f8f9fa;
            color: #333;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }}
        
        .header-info {{
            font-size: 0.9em;
            opacity: 0.9;
            margin-top: 10px;
        }}
        
        .cache-warning {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
            color: #856404;
            font-size: 0.9em;
        }}
        
        /* ОГЛАВЛЕНИЕ */
        .toc {{
            background: white;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 3px 15px rgba(0,0,0,0.08);
        }}
        
        .toc h2 {{
            color: #667eea;
            margin-top: 0;
            margin-bottom: 20px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        
        .toc-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 15px;
        }}
        
        .toc-item {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        
        .toc-item:hover {{
            background: #eef2ff;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        .toc-title {{
            font-weight: bold;
            margin-bottom: 5px;
            color: #2d3748;
        }}
        
        .toc-meta {{
            font-size: 0.85em;
            color: #718096;
            display: flex;
            justify-content: space-between;
        }}
        
        /* ЧАТЫ */
        .chat {{
            background: white;
            border-radius: 10px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 3px 15px rgba(0,0,0,0.08);
            scroll-margin-top: 20px;
        }}
        
        .chat-info {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            border-left: 4px solid #6c757d;
        }}
        
        /* УПРАВЛЕНИЕ ВЕТКАМИ */
        .branches-controls {{
            display: flex;
            gap: 10px;
            margin: 20px 0;
            flex-wrap: wrap;
            align-items: center;
        }}
        
        .branch-btn {{
            background: #667eea;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.9em;
            transition: all 0.3s ease;
        }}
        
        .branch-btn:hover {{
            background: #5a67d8;
            transform: translateY(-1px);
        }}
        
        .branch-btn.secondary {{
            background: #6c757d;
        }}
        
        .branch-btn.secondary:hover {{
            background: #5a6268;
        }}
        
        .branches-info {{
            margin-left: auto;
            font-size: 0.9em;
            color: #666;
        }}
        
        /* АККОРДЕОН ДЛЯ ВЕТОК - НОВЫЙ СТИЛЬ */
        .accordion-container {{
            margin: 25px 0;
        }}
        
        .accordion-item {{
            margin-bottom: 10px;
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid #e0e7ff;
            background: white;
        }}
        
        .accordion-header {{
            background: #f8f9ff;
            padding: 15px 20px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-weight: 500;
            transition: all 0.3s ease;
            border-bottom: 1px solid transparent;
            user-select: none;
        }}
        
        .accordion-header:hover {{
            background: #eef2ff;
        }}
        
        .accordion-header.active {{
            background: #667eea;
            color: white;
            border-bottom-color: #5566cc;
        }}
        
        .accordion-indicator {{
            font-size: 1.2em;
            transition: transform 0.3s ease;
        }}
        
        .accordion-header.active .accordion-indicator {{
            transform: rotate(180deg);
        }}
        
        .branch-info {{
            display: flex;
            align-items: center;
            gap: 15px;
        }}
        
        .branch-number {{
            background: #667eea;
            color: white;
            width: 32px;
            height: 32px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 0.9em;
        }}
        
        .accordion-header.active .branch-number {{
            background: white;
            color: #667eea;
        }}
        
        .branch-stats {{
            font-size: 0.85em;
            color: #718096;
            display: flex;
            gap: 10px;
        }}
        
        .accordion-header.active .branch-stats {{
            color: rgba(255, 255, 255, 0.9);
        }}
        
        .accordion-content {{
            padding: 0;
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease, padding 0.3s ease;
            background: white;
        }}
        
        .accordion-content.active {{
            padding: 20px;
            max-height: 5000px;
        }}
        
        /* СООБЩЕНИЯ */
        .message {{
            margin: 15px 0;
            padding: 18px;
            border-radius: 10px;
            background: linear-gradient(to right, #f8f9fa, #ffffff);
            border: 1px solid #e9ecef;
            border-left: 6px solid #6c757d;
            position: relative;
        }}
        
        .user {{
            border-left-color: #007bff;
            background: linear-gradient(to right, #e3f2fd, #ffffff);
        }}
        
        .assistant {{
            border-left-color: #28a745;
            background: linear-gradient(to right, #d4edda, #ffffff);
        }}
        
        .unknown {{
            border-left-color: #ffc107;
            background: linear-gradient(to right, #fff3cd, #ffffff);
        }}
        
        .message-header {{
            font-weight: bold;
            margin-bottom: 10px;
            font-size: 1.05em;
            color: #495057;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .message-role {{
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        
        .message-id {{
            font-size: 0.8em;
            color: #999;
            background: #f5f5f5;
            padding: 2px 8px;
            border-radius: 12px;
            font-family: monospace;
        }}
        
        .message-content {{
            line-height: 1.7;
        }}
        
        /* Стили для Markdown элементов */
        strong, b {{
            font-weight: 700;
            color: #1a1a1a;
        }}
        
        em, i {{
            font-style: italic;
        }}
        
        code {{
            font-family: 'Consolas', 'Monaco', monospace;
            background: #f5f5f5;
            padding: 2px 6px;
            border-radius: 4px;
            color: #d63384;
            border: 1px solid #e0e0e0;
            font-size: 0.9em;
        }}
        
        pre {{
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
            margin: 15px 0;
            border: 1px solid #555;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 0.95em;
            line-height: 1.5;
        }}
        
        pre code {{
            background: transparent;
            color: inherit;
            padding: 0;
            border: none;
        }}
        
        /* Стили для подзаголовков */
        .message-content h3,
        .message-content h4,
        .message-content h5 {{
            margin: 20px 0 15px 0;
            color: #2d3748;
            font-weight: 600;
        }}
        
        .message-content h3 {{
            font-size: 1.3em;
            border-bottom: 2px solid #667eea;
            padding-bottom: 8px;
            margin-top: 25px;
        }}
        
        .message-content h4 {{
            font-size: 1.15em;
            border-bottom: 1px solid #e2e8f0;
            padding-bottom: 6px;
            margin-top: 20px;
        }}
        
        .message-content h5 {{
            font-size: 1.05em;
            color: #4a5568;
            margin-top: 18px;
        }}
        
        /* Стили для списков */
        .message-content ul,
        .message-content ol {{
            margin: 15px 0 15px 20px;
            padding-left: 15px;
        }}
        
        .message-content li {{
            margin: 8px 0;
            line-height: 1.6;
        }}
        
        .message-content ul li {{
            list-style-type: disc;
        }}
        
        .message-content ol li {{
            list-style-type: decimal;
        }}
        
        .message-content ul li::marker {{
            color: #667eea;
        }}
        
        .message-content ol li::marker {{
            color: #667eea;
            font-weight: 600;
        }}
        
        /* Стили для блоков кода с кнопкой копирования */
        .code-block-container {{
            margin: 20px 0;
            border-radius: 10px;
            overflow: hidden;
            border: 1px solid #dee2e6;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }}
        
        .code-block-header {{
            background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
            color: white;
            padding: 12px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.95em;
        }}
        
        .code-block-title {{
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .code-block-copy {{
            background: rgba(255, 255, 255, 0.2);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.3);
            padding: 6px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.85em;
            transition: all 0.2s ease;
        }}
        
        .code-block-copy:hover {{
            background: rgba(255, 255, 255, 0.3);
        }}
        
        .code-block-content {{
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 0;
            overflow-x: auto;
        }}
        
        .code-block-content pre {{
            margin: 0;
            padding: 20px;
            border: none;
            border-radius: 0;
        }}
        
        /* Стили для таблиц */
        .markdown-table-container {{
            margin: 20px 0;
            overflow-x: auto;
            border-radius: 10px;
            border: 1px solid #dee2e6;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            background: white;
        }}
        
        .markdown-table {{
            width: 100%;
            border-collapse: collapse;
            min-width: 600px;
        }}
        
        .markdown-table thead {{
            background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
        }}
        
        .markdown-table th {{
            color: white;
            font-weight: 600;
            padding: 16px 20px;
            text-align: left;
            border-bottom: 3px solid #4a6fc1;
            font-size: 1.05em;
        }}
        
        .markdown-table tbody tr {{
            border-bottom: 1px solid #e9ecef;
        }}
        
        .markdown-table tbody tr:nth-child(even) {{
            background: #f8f9fa;
        }}
        
        .markdown-table td {{
            padding: 14px 20px;
            border-right: 1px solid #e9ecef;
            vertical-align: top;
            line-height: 1.6;
        }}
        
        .markdown-table td:last-child {{
            border-right: none;
        }}
        
        /* Анимация для новых веток */
        @keyframes highlightBranch {{
            from {{ background-color: rgba(102, 126, 234, 0.1); }}
            to {{ background-color: transparent; }}
        }}
        
        .accordion-item.highlight {{
            animation: highlightBranch 2s ease;
        }}
        
        /* Адаптивность */
        @media (max-width: 768px) {{
            .branches-controls {{
                flex-direction: column;
                align-items: stretch;
            }}
            
            .branch-btn {{
                width: 100%;
                text-align: center;
            }}
            
            .branches-info {{
                margin-left: 0;
                margin-top: 10px;
                text-align: center;
            }}
            
            .branch-info {{
                flex-direction: column;
                align-items: flex-start;
                gap: 5px;
            }}
            
            .branch-stats {{
                flex-wrap: wrap;
            }}
        }}
        
        /* Стили для горизонтальной линии */
        hr {{
            border: none;
            height: 1px;
            background: linear-gradient(to right, transparent, #667eea, transparent);
            margin: 25px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Экспорт чатов DeepSeek</h1>
            <div class="header-info">
                <div>📊 Всего диалогов: {total_chats} | 📁 {source_name}</div>
                <div>📅 Экспорт: {export_time} | 🆔 {timestamp}</div>
                <div>🎯 Режим: <strong>Аккордеон веток</strong> (кликайте по заголовкам)</div>
            </div>
        </div>
        
        <div class="cache-warning" id="cacheWarning">
            ⚠️ Если не видите аккордеон для веток: 
            <button onclick="hardReload()" style="margin-left: 10px; padding: 5px 10px; background: #dc3545; color: white; border: none; border-radius: 3px; cursor: pointer;">
                Принудительная перезагрузка
            </button>
            <span style="margin-left: 10px; font-size: 0.9em;">Или нажмите Ctrl+F5 / Cmd+Shift+R</span>
        </div>
        
        <div class="toc" id="toc">
            <h2>📑 Оглавление</h2>
            <div class="toc-grid">
'''
    
    # Добавляем оглавление
    for i, chat in enumerate(chats, 1):
        title = html_module.escape(chat.get('title', f'Чат {i}'))
        date_str = ""
        inserted = chat.get('inserted_at', '')
        if inserted:
            try:
                date_obj = datetime.fromisoformat(inserted.replace('Z', '+00:00'))
                date_str = date_obj.strftime('%d.%m.%Y')
            except:
                date_str = inserted[:10] if len(inserted) >= 10 else inserted
        
        # Извлекаем все ветки для подсчета
        all_branches = extract_all_branches(chat)
        branches_count = len(all_branches)
        total_messages = sum(len(branch) for branch in all_branches)
        
        # Подсчет сообщений по ролям
        role_stats = {'user': 0, 'assistant': 0, 'unknown': 0}
        for branch in all_branches:
            for msg in branch:
                role = msg.get('role', 'unknown')
                role_stats[role] = role_stats.get(role, 0) + 1
        
        html += f'''
                <div class="toc-item" data-chat="{i}">
                    <div class="toc-title">{title}</div>
                    <div class="toc-meta">
                        <span>#{i}</span>
                        <span>📅 {date_str}</span>
                        <span>🌿 {branches_count}</span>
                        <span>💬 {total_messages}</span>
                    </div>
                </div>
'''
    
    html += '''
            </div>
        </div>
'''
    
    # Добавляем чаты с ветвлениями
    for i, chat in enumerate(chats, 1):
        html += create_chat_with_accordion(i, chat)
    
    # Кнопка "Наверх" и JavaScript - ФИКСИРОВАННАЯ ЧАСТЬ
    html += f'''
    <a href="#toc" class="back-to-top" id="backToTop">↑</a>
    
    <script>
        // Cache buster: {cache_buster}
        
        // Принудительная перезагрузка с очисткой кэша
        function hardReload() {{
            console.log('Принудительная перезагрузка...');
            localStorage.setItem('forceReload', '{cache_buster}');
            window.location.reload(true);
        }}
        
        // Проверяем, нужна ли принудительная перезагрузка
        if (localStorage.getItem('forceReload') !== '{cache_buster}') {{
            localStorage.setItem('forceReload', '{cache_buster}');
        }}
        
        // Функция для копирования кода
        function copyCode(button) {{
            const codeBlock = button.closest('.code-block-container').querySelector('pre code');
            const textToCopy = codeBlock.textContent;
            
            navigator.clipboard.writeText(textToCopy).then(() => {{
                const originalText = button.textContent;
                button.textContent = 'Скопировано!';
                button.style.background = '#28a745';
                
                setTimeout(() => {{
                    button.textContent = originalText;
                    button.style.background = 'rgba(255, 255, 255, 0.2)';
                }}, 2000);
            }}).catch(err => {{
                console.error('Ошибка копирования:', err);
                button.textContent = 'Ошибка';
                button.style.background = '#dc3545';
            }});
        }}
        
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('Документ загружен. Cache buster: {cache_buster}');
            
            // Скрываем предупреждение о кэше после загрузки
            setTimeout(() => {{
                const warning = document.getElementById('cacheWarning');
                if (warning) {{
                    warning.style.display = 'none';
                }}
            }}, 5000);
            
            // Плавная прокрутка к чату при клике на элемент оглавления
            const tocItems = document.querySelectorAll('.toc-item');
            
            tocItems.forEach(item => {{
                item.addEventListener('click', function() {{
                    const chatNumber = this.getAttribute('data-chat');
                    const chatElement = document.getElementById('chat-' + chatNumber);
                    
                    if (chatElement) {{
                        chatElement.scrollIntoView({{
                            behavior: 'smooth',
                            block: 'start'
                        }});
                        
                        // Подсветка чата
                        chatElement.style.boxShadow = '0 0 0 3px rgba(102, 126, 234, 0.3)';
                        setTimeout(() => {{
                            chatElement.style.boxShadow = '';
                        }}, 2000);
                    }}
                }});
            }});
            
            // Кнопка "Наверх"
            const backToTop = document.getElementById('backToTop');
            window.addEventListener('scroll', () => {{
                if (window.scrollY > 300) {{
                    backToTop.classList.add('visible');
                }} else {{
                    backToTop.classList.remove('visible');
                }}
            }});
            
            backToTop.addEventListener('click', function(e) {{
                e.preventDefault();
                document.getElementById('toc').scrollIntoView({{
                    behavior: 'smooth',
                    block: 'start'
                }});
            }});
            
            // Управление аккордеоном веток
            const accordionHeaders = document.querySelectorAll('.accordion-header');
            console.log('Найдено элементов аккордеона:', accordionHeaders.length);
            
            accordionHeaders.forEach(header => {{
                header.addEventListener('click', function() {{
                    console.log('Клик по аккордеону:', this.textContent);
                    const content = this.nextElementSibling;
                    const isActive = this.classList.contains('active');
                    
                    // Закрываем все аккордеоны в этой группе
                    const parent = this.closest('.accordion-container');
                    const allHeaders = parent.querySelectorAll('.accordion-header');
                    const allContents = parent.querySelectorAll('.accordion-content');
                    
                    allHeaders.forEach(h => h.classList.remove('active'));
                    allContents.forEach(c => {{
                        c.classList.remove('active');
                        c.style.maxHeight = null;
                    }});
                    
                    // Открываем текущий, если был закрыт
                    if (!isActive) {{
                        this.classList.add('active');
                        content.classList.add('active');
                        content.style.maxHeight = content.scrollHeight + "px";
                        
                        // Подсветка открытой ветки
                        this.parentElement.classList.add('highlight');
                        setTimeout(() => {{
                            this.parentElement.classList.remove('highlight');
                        }}, 2000);
                    }}
                }});
            }});
            
            // Кнопки управления ветками
            const expandAllBtns = document.querySelectorAll('.expand-all');
            expandAllBtns.forEach(btn => {{
                btn.addEventListener('click', function() {{
                    const chatId = this.getAttribute('data-chat');
                    const contents = document.querySelectorAll('#chat-' + chatId + ' .accordion-content');
                    const headers = document.querySelectorAll('#chat-' + chatId + ' .accordion-header');
                    
                    contents.forEach(content => {{
                        content.classList.add('active');
                        content.style.maxHeight = content.scrollHeight + "px";
                    }});
                    headers.forEach(header => header.classList.add('active'));
                    
                    console.log('Развернуты все ветки в чате', chatId);
                }});
            }});
            
            const collapseAllBtns = document.querySelectorAll('.collapse-all');
            collapseAllBtns.forEach(btn => {{
                btn.addEventListener('click', function() {{
                    const chatId = this.getAttribute('data-chat');
                    const contents = document.querySelectorAll('#chat-' + chatId + ' .accordion-content');
                    const headers = document.querySelectorAll('#chat-' + chatId + ' .accordion-header');
                    
                    contents.forEach(content => {{
                        content.classList.remove('active');
                        content.style.maxHeight = null;
                    }});
                    headers.forEach(header => header.classList.remove('active'));
                    
                    console.log('Свернуты все ветки в чате', chatId);
                }});
            }});
            
            // По умолчанию открываем первую ветку в каждом чате
            const firstAccordions = document.querySelectorAll('.accordion-container .accordion-header:first-child');
            console.log('Открываем первые ветки:', firstAccordions.length);
            
            firstAccordions.forEach(header => {{
                if (!header.classList.contains('active')) {{
                    setTimeout(() => {{
                        header.click();
                    }}, 100);
                }}
            }});
            
            // Проверяем, работает ли аккордеон
            setTimeout(() => {{
                const activeAccordions = document.querySelectorAll('.accordion-header.active');
                console.log('Активных аккордеонов:', activeAccordions.length);
                
                if (activeAccordions.length === 0) {{
                    console.warn('⚠️ Аккордеон не работает! Возможно проблема с кэшем.');
                    document.getElementById('cacheWarning').style.display = 'block';
                }}
            }}, 500);
        }});
    </script>
</body>
</html>'''
    
    return html

def create_chat_with_accordion(index, chat):
    """Создание чата с аккордеоном для веток"""
    title = html_module.escape(chat.get('title', f'Чат {index}'))
    
    # Извлекаем все ветки
    all_branches = extract_all_branches(chat)
    organized_branches = organize_branches_by_depth(all_branches)
    
    branches_count = len(organized_branches)
    total_messages = sum(len(branch) for branch in organized_branches)
    
    # Статистика по ролям
    role_stats = {'user': 0, 'assistant': 0, 'unknown': 0}
    for branch in organized_branches:
        for msg in branch:
            role = msg.get('role', 'unknown')
            role_stats[role] = role_stats.get(role, 0) + 1
    
    html = f'''
    <div class="chat" id="chat-{index}">
        <h2>{title}</h2>
        
        <div class="chat-info">
            <div><strong>📊 Статистика чата:</strong></div>
            <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 10px; margin-top: 10px;">
                <div>🌿 Всего веток: <strong>{branches_count}</strong></div>
                <div>💬 Всего сообщений: <strong>{total_messages}</strong></div>
                <div>👤 Сообщений пользователя: <strong>{role_stats.get('user', 0)}</strong></div>
                <div>🤖 Ответов DeepSeek: <strong>{role_stats.get('assistant', 0)}</strong></div>
                <div>❓ Других: <strong>{role_stats.get('unknown', 0)}</strong></div>
            </div>
        </div>
        
        <div class="branches-controls">
            <button class="branch-btn expand-all" data-chat="{index}">📖 Развернуть все ветки</button>
            <button class="branch-btn secondary collapse-all" data-chat="{index}">📕 Свернуть все ветки</button>
            <div class="branches-info">
                ⚡ <strong>Кликайте по заголовкам веток ниже</strong> для просмотра сообщений
            </div>
        </div>
'''
    
    # Аккордеон для веток
    html += f'''
        <div class="accordion-container">
'''
    
    for branch_num, branch in enumerate(organized_branches, 1):
        branch_length = len(branch)
        
        # Статистика по ветке
        user_messages = sum(1 for msg in branch if msg.get('role') == 'user')
        assistant_messages = sum(1 for msg in branch if msg.get('role') == 'assistant')
        unknown_messages = branch_length - user_messages - assistant_messages
        
        # Первые слова первого сообщения для заголовка
        first_message_preview = ""
        if branch and branch[0].get('content'):
            first_words = branch[0]['content'][:80]
            if len(branch[0]['content']) > 80:
                first_words += "..."
            first_message_preview = html_module.escape(first_words)
        
        html += f'''
            <div class="accordion-item">
                <div class="accordion-header">
                    <div class="branch-info">
                        <div class="branch-number">{branch_num}</div>
                        <div>
                            <div style="font-weight: bold;">Ветка #{branch_num}</div>
                            <div class="branch-stats">
                                <span title="Всего сообщений">📝 {branch_length}</span>
                                <span title="Сообщений пользователя">👤 {user_messages}</span>
                                <span title="Ответов DeepSeek">🤖 {assistant_messages}</span>
                                {f'<span title="Других сообщений">❓ {unknown_messages}</span>' if unknown_messages > 0 else ''}
                            </div>
                        </div>
                    </div>
                    <div class="accordion-indicator">▼</div>
                </div>
                <div class="accordion-content">
'''
        
        if first_message_preview:
            html += f'''
                    <div style="margin-bottom: 15px; padding: 10px; background: #f8f9fa; border-radius: 5px; font-size: 0.9em; color: #666;">
                        <strong>Начало ветки:</strong> {first_message_preview}
                    </div>
'''
        
        for j, msg in enumerate(branch, 1):
            role = msg.get('role', 'unknown')
            content = format_full_markdown(msg.get('content', ''))
            node_id = msg.get('node_id', '')
            
            # Определяем отображение роли на основе реальных данных
            role_display = {
                'user': '👤 Вы',
                'assistant': '🤖 DeepSeek',
                'unknown': '❓ Неизвестно'
            }.get(role, '❓ Неизвестно')
            
            role_class = role
            
            html += f'''
                    <div class="message {role_class}">
                        <div class="message-header">
                            <div class="message-role">
                                <span>{role_display}</span>
                                <span class="message-id">#{j} (узел: {node_id})</span>
                            </div>
                        </div>
                        <div class="message-content">{content}</div>
                    </div>
'''
        
        html += '''
                </div>
            </div>
'''
    
    html += '''
        </div>
    </div>
    '''
    
    return html

def format_full_markdown(content):
    """Полная обработка Markdown с поддержкой таблиц, подзаголовков и фрагментов кода"""
    if not content:
        return ""
    
    # 1. Заменяем переносы строк на <br> для сохранения структуры
    content = content.replace('\n', '<br>')
    
    # 2. Обрабатываем блоки кода с языком
    content = re.sub(
        r'```(\w+)?<br>([\s\S]*?)<br>```',
        lambda m: create_code_block(m.group(2), m.group(1)),
        content
    )
    
    # 3. Обрабатываем блоки кода без указания языка
    content = re.sub(
        r'```<br>([\s\S]*?)<br>```',
        lambda m: create_code_block(m.group(1), ''),
        content
    )
    
    # 4. Обрабатываем инлайн код
    content = re.sub(r'`([^`]+)`', r'<code>\1</code>', content)
    
    # 5. Обрабатываем заголовки
    content = re.sub(r'###\s+(.+?)(?:<br>|$)', r'<h5>\1</h5>', content)
    content = re.sub(r'##\s+(.+?)(?:<br>|$)', r'<h4>\1</h4>', content)
    content = re.sub(r'#\s+(.+?)(?:<br>|$)', r'<h3>\1</h3>', content)
    
    # 6. Обрабатываем жирный текст
    content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
    content = re.sub(r'__(.+?)__', r'<strong>\1</strong>', content)
    
    # 7. Обрабатываем курсив
    content = re.sub(r'\*(.+?)\*', r'<em>\1</em>', content)
    content = re.sub(r'_(.+?)_', r'<em>\1</em>', content)
    
    # 8. Обрабатываем зачеркнутый текст
    content = re.sub(r'~~(.+?)~~', r'<del>\1</del>', content)
    
    # 9. Обрабатываем ссылки
    content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank">\1</a>', content)
    
    # 10. Обрабатываем списки (упрощенная версия)
    content = process_lists_simple(content)
    
    # 11. Обрабатываем таблицы
    content = process_markdown_tables_simple(content)
    
    # 12. Обрабатываем горизонтальные линии
    content = content.replace('---', '<hr>')
    content = content.replace('***', '<hr>')
    
    return content

def create_code_block(code, language):
    """Создание блока кода с кнопкой копирования"""
    # Восстанавливаем переносы строк
    code = code.replace('<br>', '\n')
    
    # Определяем язык для отображения
    lang_display = {
        'python': 'Python',
        'javascript': 'JavaScript',
        'js': 'JavaScript',
        'typescript': 'TypeScript',
        'ts': 'TypeScript',
        'java': 'Java',
        'cpp': 'C++',
        'c': 'C',
        'csharp': 'C#',
        'cs': 'C#',
        'go': 'Go',
        'rust': 'Rust',
        'php': 'PHP',
        'ruby': 'Ruby',
        'swift': 'Swift',
        'kotlin': 'Kotlin',
        'html': 'HTML',
        'css': 'CSS',
        'sql': 'SQL',
        'bash': 'Bash',
        'shell': 'Shell',
        'json': 'JSON',
        'xml': 'XML',
        'yaml': 'YAML',
        'markdown': 'Markdown',
        'md': 'Markdown'
    }.get(language.lower() if language else '', language.capitalize() if language else 'Код')
    
    # Экранируем HTML в коде
    escaped_code = html_module.escape(code)
    
    return f'''
    <div class="code-block-container">
        <div class="code-block-header">
            <div class="code-block-title">
                <span>📋</span>
                <span>{lang_display}</span>
            </div>
            <button class="code-block-copy" onclick="copyCode(this)">Копировать</button>
        </div>
        <div class="code-block-content">
            <pre><code class="{language}">{escaped_code}</code></pre>
        </div>
    </div>
    '''

def process_lists_simple(content):
    """Упрощенная обработка списков"""
    lines = content.split('<br>')
    result = []
    in_list = False
    list_type = None  # 'ul' или 'ol'
    list_items = []
    
    for line in lines:
        line_stripped = line.strip()
        
        # Проверяем маркированный список
        if line_stripped.startswith(('* ', '- ', '+ ')):
            if not in_list:
                in_list = True
                list_type = 'ul'
            # Извлекаем содержимое элемента
            item_content = line_stripped[2:].strip()
            list_items.append(f'<li>{item_content}</li>')
        
        # Проверяем нумерованный список
        elif re.match(r'^\d+\.\s+', line_stripped):
            if not in_list:
                in_list = True
                list_type = 'ol'
            # Извлекаем содержимое элемента
            item_content = re.sub(r'^\d+\.\s+', '', line_stripped)
            list_items.append(f'<li>{item_content}</li>')
        
        else:
            # Если мы были в списке, закрываем его
            if in_list:
                result.append(f'<{list_type}>' + ''.join(list_items) + f'</{list_type}>')
                in_list = False
                list_type = None
                list_items = []
            
            result.append(line)
    
    # Если остался незакрытый список
    if in_list:
        result.append(f'<{list_type}>' + ''.join(list_items) + f'</{list_type}>')
    
    return '<br>'.join(result)

def process_markdown_tables_simple(content):
    """Упрощенная обработка Markdown таблиц"""
    lines = content.split('<br>')
    result = []
    i = 0
    
    while i < len(lines):
        # Проверяем, является ли текущая строка началом таблицы
        if '|' in lines[i] and i + 1 < len(lines) and '|' in lines[i + 1]:
            # Проверяем, является ли следующая строка разделителем
            next_line = lines[i + 1]
            if re.search(r'[-:|]', next_line):
                # Нашли таблицу
                table_start = i
                # Ищем конец таблицы
                table_end = i + 1
                while table_end < len(lines) and '|' in lines[table_end]:
                    table_end += 1
                
                # Извлекаем строки таблицы
                table_lines = lines[table_start:table_end]
                table_html = convert_table_simple(table_lines)
                result.append(table_html)
                i = table_end
                continue
        
        result.append(lines[i])
        i += 1
    
    return '<br>'.join(result)

def convert_table_simple(table_lines):
    """Конвертация простой таблицы"""
    if len(table_lines) < 2:
        return ""
    
    # Парсим строки
    parsed_rows = []
    for line in table_lines:
        # Убираем начальные и конечные '|'
        cleaned = line.strip().strip('|')
        # Разделяем на ячейки
        cells = [cell.strip() for cell in cleaned.split('|')]
        parsed_rows.append(cells)
    
    # Определяем выравнивание на основе разделительной строки
    alignments = []
    if len(parsed_rows) >= 2:
        separator_row = parsed_rows[1]
        for cell in separator_row:
            if cell.startswith(':') and cell.endswith(':'):
                alignments.append('center')
            elif cell.endswith(':'):
                alignments.append('right')
            else:
                alignments.append('left')
    
    html = '<div class="markdown-table-container"><table class="markdown-table"><thead><tr>'
    
    # Заголовки (первая строка)
    headers = parsed_rows[0]
    for j, header in enumerate(headers):
        align = alignments[j] if j < len(alignments) else 'left'
        html += f'<th style="text-align: {align}">{header}</th>'
    
    html += '</tr></thead><tbody>'
    
    # Данные (начиная с третьей строки)
    for k in range(2, len(parsed_rows)):
        cells = parsed_rows[k]
        html += '<tr>'
        
        for j in range(len(headers)):
            cell = cells[j] if j < len(cells) else ''
            align = alignments[j] if j < len(alignments) else 'left'
            html += f'<td style="text-align: {align}">{cell}</td>'
        
        html += '</tr>'
    
    html += '</tbody></table></div>'
    
    return html

if __name__ == "__main__":
    print("=" * 70)
    print("🤖 Экспортер чатов DeepSeek в HTML (с аккордеоном для веток)")
    print("=" * 70)
    print("ℹ️  Новые функции: аккордеон для веток, улучшенное определение ролей")
    print("   Поддержка: подзаголовков, списков, блоков кода с кнопкой копирования")
    print("   Упрощенная обработка Markdown для лучшей совместимости")
    print("⚠️  Если не видите изменений, используйте принудительную перезагрузку")
    print("-" * 70)
    
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        if os.path.exists(input_file):
            print(f"📂 Используется файл из аргументов: {input_file}")
        else:
            print(f"❌ Файл не найден: {input_file}")
            print("Будет предложен выбор файла...")
    
    export_with_full_markdown()