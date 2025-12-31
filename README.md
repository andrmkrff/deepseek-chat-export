# 🚀 DeepSeek Chat Export Tool

**Экспорт чатов DeepSeek в красивый HTML с поддержкой ветвлений, Markdown и аккордеонами**

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![DeepSeek](https://img.shields.io/badge/DeepSeek-Chat%20Export-green.svg)](https://www.deepseek.com)

<div align="center">
  <img src="https://img.shields.io/badge/Features-🚀-orange" alt="Features">
  <img src="https://img.shields.io/badge/HTML-Export-ff69b4" alt="HTML Export">
  <img src="https://img.shields.io/badge/Markdown-Full%20Support-blueviolet" alt="Markdown Support">
</div>

## 🌟 Особенности

### 📊 **Визуализация ветвлений**
- 🔄 **Аккордеон-интерфейс** для всех веток диалога
- 📈 **Статистика** по каждой ветке: сообщения пользователя, ответы AI, общее количество
- 🎯 **Интерактивное оглавление** с быстрой навигацией

### 🎨 **Полная поддержка Markdown**
- 📝 **Заголовки** всех уровней (H1-H5)
- 📋 **Списки** (нумерованные и маркированные)
- 🏗️ **Таблицы** с адаптивным дизайном
- 💻 **Блоки кода** с подсветкой синтаксиса и кнопкой копирования
- 🔗 **Ссылки**, **жирный текст**, *курсив*, ~~зачеркнутый~~
- 📐 **Горизонтальные линии**

### 🛠️ **Удобный интерфейс**
- 🖥️ **Автоматический поиск** JSON файлов
- 🎮 **Интерактивный выбор** файла для экспорта
- 🌐 **Автооткрытие** в браузере после экспорта
- 🎨 **Адаптивный дизайн** для всех устройств

## 📦 Установка

### Требования
- Python 3.7 или выше
- Стандартные библиотеки Python (не требует дополнительных зависимостей)

### Быстрый старт

1. **Скачайте скрипт:**
```bash
git clone https://github.com/andrmkrff/deepseek-chat-export.git
cd deepseek-chat-export
```
2. **Подготовьте файлы экспорта из DeepSeek:**

В веб-версии DeepSeek: Настройки → Данные → Экспорт данных → Скачать

Получите файл conversations.json

3. **Переместите файл/файлы чата conversations.json в папку со скриптом и запустите скрипт:**
```bash
bash
python deepseek_export.py
```

**🚀 Использование**
***Базовое использование***

```bash
# Запуск с интерактивным выбором файла
python deepseek_export.py

# Запуск с указанием конкретного файла
python deepseek_export.py path/to/your/conversations.json
```

***Пошаговый процесс***

1. Скрипт автоматически найдет все JSON файлы в текущей директории

2. Выберите нужный файл из списка или укажите путь вручную

3. Скрипт создаст HTML файл с именем: имяфайла_export_дата время.html

4. Файл автоматически откроется в вашем браузере

**📊 Пример экспорта**
***Входные данные (JSON от DeepSeek):***
```json
{
  "title": "Обсуждение философии",
  "mapping": {
    "node_1": {
      "message": {
        "content": "### 1. Досократики\n* Фалес: вода как первоначало",
        "author": {"role": "user"}
      },
      "children": ["node_2"]
    }
  }
}
```
***Результат (HTML):***
https://via.placeholder.com/800x400.png?text=DeepSeek+Export+Example

**🎨 Возможности интерфейса**

***🪟 Аккордеон веток***

```text
📖 Ветка #1 [4 сообщения]
├─ 👤 Вы: "Расскажи о философии..."
├─ 🤖 DeepSeek: "### 1. Досократики..."
├─ 👤 Вы: "А что насчет Платона?"
└─ 🤖 DeepSeek: "Платон развил идеи Сократа..."
```

***📑 Оглавление***

- Быстрая навигация по всем чатам
- Статистика для каждого чата
- Кликабельные элементы для прокрутки

***💾 Управление кэшем***
- Автоматическая очистка кэша браузера
- Кнопка "Принудительная перезагрузка"
- Инструкции для разных браузеров

**⚙️ Конфигурация**
Создайте файл config.json для настройки:

```json
{
  "exclude_files": ["package.json", "tsconfig.json"],
  "default_open_in_browser": true,
  "auto_expand_first_branch": true,
  "theme": {
    "primary_color": "#667eea",
    "secondary_color": "#764ba2"
  }
}
```
**🔧 Расширенные возможности**
***Экспорт нескольких файлов***

```bash
# Экспорт всех JSON файлов в директории
for file in *.json; do
  python deepseek_export.py "$file"
done 
```
**Интеграция с другими инструментами**
``` python
# Использование как модуль
from deepseek_export import export_chat

export_chat("conversations.json", output_file="my_chat.html")
```
**🐛 Устранение неполадок**

***Проблема: Не видно аккордеона***
Решение: Нажмите кнопку "Принудительная перезагрузка" или Ctrl+F5

***Проблема: JSON файл не распознается***
Решение: Убедитесь, что файл имеет правильный формат экспорта DeepSeek

***Проблема: Не открывается в браузере***
Решение: Откройте файл вручную или проверьте настройки браузера

**📁 Структура проекта**
```text
deepseek-chat-export/
├── README.md                    # Основная документация
├── LICENSE                      # Лицензия MIT (отдельный файл)
├── requirements.txt             # Зависимости
├── deepseek_export.py          # Основной скрипт
├── config.json                 # Пример конфигурации
├── .gitignore                  # Git ignore файл
└── examples/
    └── sample_conversation.json # Пример данных
```

**🤝 Как помочь проекту**

***Сообщить об ошибке***
- Проверьте существующие Issues
- Создайте новое Issue с описанием проблемы
- Приложите пример JSON файла (без приватных данных)

***Предложить улучшение***
- Форкните репозиторий
- Создайте ветку для вашего фича
- Сделайте Pull Request с описанием изменений

***Распространить информацию***
- ⭐ Поставьте звезду на GitHub
- 🐦 Расскажите в Twitter
- 💬 Поделитесь в чатах разработчиков

**📄 Лицензия**
Этот проект распространяется под лицензией MIT. См. файл LICENSE для подробностей.

**🙏 Благодарности**
- Команде DeepSeek за отличный AI ассистент
- Сообществу open-source за вдохновение
- Вам за использование этого инструмента! ❤️

```markdown
<div align="center">
  <p>
    <strong>Сделано с ❤️ для сообщества DeepSeek</strong>
  </p>
  <p>
    <a href="https://github.com/andrmkrff/deepseek-chat-export">GitHub</a> •
    <a href="https://www.deepseek.com">DeepSeek</a> •
    <a href="https://github.com/andrmkrff/deepseek-chat-export/issues">Issues</a>
  </p>
</div>
```