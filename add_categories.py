import os
import django
import sys

project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'techno_work.settings')
django.setup()

from career_app.models import Category


def create_categories():
    # Сначала создаем основные категории
    main_categories = [
        {'name': 'IT и технологии', 'description': 'Технологии и программирование'},
        {'name': 'Дизайн и творчество', 'description': 'Дизайн, искусство и творческие профессии'},
        {'name': 'Маркетинг и продажи', 'description': 'Маркетинг, реклама и продажи'},
        {'name': 'Менеджмент', 'description': 'Управление и администрирование'},
        {'name': 'Финансы и бухгалтерия', 'description': 'Финансы, бухгалтерия и экономика'},
        {'name': 'Образование и наука', 'description': 'Образование, наука и исследования'},
        {'name': 'Медицина и здоровье', 'description': 'Медицина, фармацевтика и здоровье'},
        {'name': 'Транспорт и логистика', 'description': 'Транспорт, логистика и доставка'},
        {'name': 'Производство и строительство', 'description': 'Производство, строительство и инженерия'},
        {'name': 'Сфера услуг', 'description': 'Услуги, туризм и гостеприимство'},
        {'name': 'Другие профессии', 'description': 'Другие профессиональные области'},
    ]

    # Словарь для хранения созданных основных категорий
    main_cats = {}

    print("🚀 Создание основных категорий...")
    for cat_data in main_categories:
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults={
                'description': cat_data['description'],
                'is_main': True
            }
        )
        main_cats[cat_data['name']] = category
        if created:
            print(f"✅ Создана основная категория: {cat_data['name']}")

    # Теперь создаем подкатегории
    subcategories = {
        'IT и технологии': [
            {'name': 'Программирование', 'description': 'Разработка программного обеспечения'},
            {'name': 'Веб-разработка', 'description': 'Создание веб-сайтов и приложений'},
            {'name': 'Мобильная разработка', 'description': 'Разработка мобильных приложений'},
            {'name': 'Data Science', 'description': 'Анализ данных и машинное обучение'},
            {'name': 'DevOps', 'description': 'Администрирование и автоматизация'},
            {'name': 'Тестирование (QA)', 'description': 'Тестирование программного обеспечения'},
            {'name': 'Кибербезопасность', 'description': 'Защита информационных систем'},
            {'name': 'Техническая поддержка', 'description': 'Поддержка пользователей'},
        ],
        'Дизайн и творчество': [
            {'name': 'Веб-дизайн', 'description': 'Дизайн интерфейсов и сайтов'},
            {'name': 'Графический дизайн', 'description': 'Создание графики и иллюстраций'},
            {'name': 'UI/UX дизайн', 'description': 'Дизайн пользовательских интерфейсов'},
            {'name': '3D-дизайн', 'description': 'Трехмерное моделирование'},
            {'name': 'Моушн-дизайн', 'description': 'Создание анимации'},
        ],
        'Маркетинг и продажи': [
            {'name': 'Цифровой маркетинг', 'description': 'Продвижение в интернете'},
            {'name': 'SMM', 'description': 'Продвижение в социальных сетях'},
            {'name': 'Контент-маркетинг', 'description': 'Создание и продвижение контента'},
            {'name': 'SEO', 'description': 'Поисковая оптимизация'},
            {'name': 'Продажи', 'description': 'Продажа товаров и услуг'},
            {'name': 'Торговый персонал', 'description': 'Работа с клиентами'},
        ],
        'Менеджмент': [
            {'name': 'Проектный менеджмент', 'description': 'Управление проектами'},
            {'name': 'Продуктовый менеджмент', 'description': 'Управление продуктом'},
            {'name': 'Офис-менеджмент', 'description': 'Административная работа'},
            {'name': 'HR', 'description': 'Подбор и управление персоналом'},
            {'name': 'Операционный менеджмент', 'description': 'Управление операциями'},
        ],
        'Финансы и бухгалтерия': [
            {'name': 'Бухгалтерия', 'description': 'Ведение бухгалтерского учета'},
            {'name': 'Финансовый анализ', 'description': 'Анализ финансовых показателей'},
            {'name': 'Экономика', 'description': 'Экономический анализ'},
            {'name': 'Аудит', 'description': 'Проверка финансовой отчетности'},
        ],
        'Образование и наука': [
            {'name': 'Преподавание', 'description': 'Обучение и преподавание'},
            {'name': 'Научные исследования', 'description': 'Научные исследования'},
            {'name': 'Репетиторство', 'description': 'Индивидуальное обучение'},
        ],
        'Медицина и здоровье': [
            {'name': 'Медицина', 'description': 'Медицинская практика'},
            {'name': 'Фармацевтика', 'description': 'Работа в аптеке'},
            {'name': 'Психология', 'description': 'Психологическая помощь'},
        ],
        'Транспорт и логистика': [
            {'name': 'Логистика', 'description': 'Организация перевозок'},
            {'name': 'Водители', 'description': 'Управление транспортными средствами'},
            {'name': 'Курьерские услуги', 'description': 'Доставка товаров'},
        ],
        'Производство и строительство': [
            {'name': 'Инженерия', 'description': 'Инженерные работы'},
            {'name': 'Строительство', 'description': 'Строительные работы'},
            {'name': 'Архитектура', 'description': 'Проектирование зданий'},
            {'name': 'Производство', 'description': 'Работа на производстве'},
        ],
        'Сфера услуг': [
            {'name': 'Ресторанный бизнес', 'description': 'Работа в ресторанах'},
            {'name': 'Гостиничный бизнес', 'description': 'Работа в отелях'},
            {'name': 'Туризм', 'description': 'Туристические услуги'},
            {'name': 'Красота и здоровье', 'description': 'Салоны красоты'},
        ],
        'Другие профессии': [
            {'name': 'Юриспруденция', 'description': 'Юридические услуги'},
            {'name': 'Переводы', 'description': 'Перевод текстов'},
            {'name': 'Журналистика', 'description': 'Создание новостного контента'},
            {'name': 'Фотография', 'description': 'Фотосъемка'},
            {'name': 'Видеопроизводство', 'description': 'Видеосъемка и монтаж'},
            {'name': 'Консультирование', 'description': 'Консультационные услуги'},
        ],
    }

    print("\n🚀 Создание подкатегорий...")
    for main_cat_name, subcats in subcategories.items():
        main_cat = main_cats.get(main_cat_name)
        if main_cat:
            for subcat_data in subcats:
                subcategory, created = Category.objects.get_or_create(
                    name=subcat_data['name'],
                    defaults={
                        'description': subcat_data['description'],
                        'parent': main_cat,
                        'is_main': False
                    }
                )
                if created:
                    print(f"   ✅ Создана подкатегория: {subcat_data['name']}")

    print(f"\n🎯 Всего основных категорий: {Category.objects.filter(is_main=True).count()}")
    print(f"🎯 Всего подкатегорий: {Category.objects.filter(is_main=False).count()}")
    print(f"🎯 Всего категорий: {Category.objects.count()}")


if __name__ == '__main__':
    create_categories()