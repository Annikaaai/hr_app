from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Возвращает элемент из словаря по ключу"""
    if hasattr(dictionary, 'get'):
        return dictionary.get(key)
    return None

@register.filter
def dictsort(queryset, attribute):
    """Сортирует queryset и преобразует в словарь"""
    return {getattr(obj, 'id'): obj for obj in queryset}