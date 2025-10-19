# TechTalentHub

![Django](https://img.shields.io/badge/Django-4.2.7-green.svg)
![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Supported-blue.svg)

## 🎯 О проекте

**TechTalentHub** — это инновационная система управления карьерными сервисами для технологического кластера. Платформа объединяет компании, учебные заведения и соискателей в единой автоматизированной экосистеме с использованием искусственного интеллекта для оптимизации процессов подбора.

### ✨ Ключевые особенности

- 🤖 **ИИ-ассистент** для интеллектуального подбора кандидатов и вакансий
- 💬 **Встроенная система чатов** для прямого общения между участниками
- 📊 **Расширенная аналитика** с визуализацией данных
- 🎓 **Интеграция стажировок** с учебными заведениями
- 👥 **Многофункциональные личные кабинеты** для разных ролей пользователей
- 📄 **Генерация отчетов** в PDF и Excel форматах

## 🚀 Быстрый старт

### Предварительные требования

- Python 3.8 или выше
- PostgreSQL 12+
- pip (менеджер пакетов Python)

### Установка и запуск

1. **Клонирование репозитория**
```bash
git clone <repository-url>
cd techtalenthub

python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows

pip install -r requirements.txt


python manage.py migrate
python manage.py createsuperuser

python manage.py runserver
