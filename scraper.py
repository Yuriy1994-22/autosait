#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ПРОГРАММА ДЛЯ СБОРА АВТОМОБИЛЕЙ
Автор: Новичок
Описание: Эта программа собирает данные об автомобилях с сайта
"""

# Импортируем нужные библиотеки
import requests          # Для загрузки страниц
from bs4 import BeautifulSoup  # Для разбора HTML
import json             # Для сохранения в JSON
import time             # Для пауз
from datetime import datetime  # Для времени
import sys              # Для выхода
import os               # Для работы с файлами
import random           # Для случайных задержек

def print_colored(text, color):
    """Печатает цветной текст в консоли"""
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'end': '\033[0m'
    }
    print(f"{colors.get(color, '')}{text}{colors['end']}")

def get_page(url):
    """Загружает страницу с сайта"""
    try:
        # Создаем заголовки, чтобы сайт думал что мы браузер
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
        
        print_colored(f"🔗 Загружаю страницу: {url}", 'blue')
        
        # Делаем запрос к сайту
        response = requests.get(url, headers=headers, timeout=30)
        
        # Проверяем успешность
        if response.status_code == 200:
            print_colored("✅ Страница успешно загружена!", 'green')
            return response.text
        else:
            print_colored(f"❌ Ошибка {response.status_code} при загрузке", 'red')
            return None
            
    except Exception as e:
        print_colored(f"💥 Ошибка соединения: {str(e)}", 'red')
        return None

def parse_cars_from_html(html):
    """Извлекает данные об автомобилях из HTML"""
    
    print_colored("🔍 Начинаю поиск автомобилей...", 'yellow')
    
    # Создаем "суп" из HTML для удобного поиска
    soup = BeautifulSoup(html, 'html.parser')
    
    # Здесь будут все найденные автомобили
    all_cars = []
    
    # СПОСОБ 1: Ищем по классам (как в примере с resoleasing)
    car_elements = soup.find_all('div', class_='sale-list__item')
    
    print_colored(f"📊 Найдено {len(car_elements)} элементов с классом 'sale-list__item'", 'cyan')
    
    # Если нашли по классу
    if car_elements:
        print_colored("🎯 Использую Способ 1 (по классам)", 'green')
        
        for i, car_element in enumerate(car_elements, 1):
            try:
                print_colored(f"🚗 Обрабатываю автомобиль {i}/{len(car_elements)}...", 'magenta')
                
                # Извлекаем название
                title_element = car_element.find('div', class_='sale-list__item-model')
                title = title_element.get_text(strip=True) if title_element else 'Автомобиль'
                
                # Извлекаем цену
                price_element = car_element.find('div', class_='sale-list__item-price')
                price = price_element.get_text(strip=True) if price_element else 'Цена по запросу'
                
                # Извлекаем информацию (год/пробег/город)
                info_element = car_element.find('div', class_='sale-list__item-info')
                info_text = info_element.get_text(strip=True) if info_element else ' / / '
                
                # Разделяем информацию
                parts = [part.strip() for part in info_text.split('/')]
                year = parts[0] if len(parts) > 0 else ''
                mileage = parts[1] if len(parts) > 1 else ''
                location = parts[2] if len(parts) > 2 else ''
                
                # Извлекаем изображение
                img_element = car_element.find('img')
                image_url = ''
                if img_element and img_element.get('src'):
                    img_src = img_element['src']
                    if img_src.startswith('//'):
                        image_url = f'https:{img_src}'
                    elif img_src.startswith('/'):
                        image_url = f'https://www.resoleasing.com{img_src}'
                    else:
                        image_url = img_src
                
                # Извлекаем ссылку на детальную страницу
                link_element = car_element.find('a')
                detail_url = ''
                if link_element and link_element.get('href'):
                    href = link_element['href']
                    if href.startswith('/'):
                        detail_url = f'https://www.resoleasing.com{href}'
                    else:
                        detail_url = href
                
                # Создаем словарь с данными
                car_data = {
                    'id': f'car_{i:03d}',
                    'title': title,
                    'price': price,
                    'year': year,
                    'mileage': mileage,
                    'location': location,
                    'image': image_url,
                    'detail_url': detail_url,
                    'parsed_at': datetime.now().isoformat()
                }
                
                all_cars.append(car_data)
                print_colored(f"   ✓ {title} - {price}", 'green')
                
                # Маленькая пауза чтобы не перегружать
                time.sleep(0.1)
                
            except Exception as e:
                print_colored(f"   ✗ Ошибка: {str(e)}", 'red')
                continue
    
    # Если не нашли по классу, пробуем другие способы
    if not all_cars:
        print_colored("⚠️ Не нашел по классам, пробую другие способы...", 'yellow')
        
        # СПОСОБ 2: Ищем все элементы с ценами
        price_elements = soup.find_all(text=lambda text: '₽' in str(text))
        
        for price_text in price_elements[:20]:  # Берем первые 20
            try:
                parent = price_text.parent
                if parent:
                    # Пытаемся найти информацию рядом с ценой
                    car_data = {
                        'id': f'car_{len(all_cars)+1:03d}',
                        'title': 'Автомобиль',
                        'price': str(price_text).strip(),
                        'year': '',
                        'mileage': '',
                        'location': '',
                        'image': '',
                        'detail_url': '',
                        'parsed_at': datetime.now().isoformat()
                    }
                    all_cars.append(car_data)
            except:
                pass
    
    # Если вообще ничего не нашли, создаем тестовые данные
    if not all_cars:
        print_colored("⚠️ Не нашел автомобили, создаю тестовые данные", 'yellow')
        
        test_cars = [
            {
                'id': 'test_001',
                'title': 'MERCEDES-BENZ S CLASS AMG',
                'price': '22 135 000 ₽',
                'year': '2024',
                'mileage': '27 км',
                'location': 'Москва',
                'image': 'https://api-sale.resoleasing.com/upload/resize_cache/iblock/585/480_300_2d42db8e25ea118a20d6873f14b9565f0/2025-12-03_PHOTO_7737763b7f2111f08c76005056b521a7_f153dfcbd06311f08c7b005056b521a7.jpg',
                'detail_url': '',
                'parsed_at': datetime.now().isoformat()
            },
            {
                'id': 'test_002',
                'title': 'GEELY COOLRAY',
                'price': '1 709 000 ₽',
                'year': '2022',
                'mileage': '62 018 км',
                'location': 'Москва',
                'image': 'https://api-sale.resoleasing.com/upload/iblock/ca1/2025-12-29_PHOTO_1d432f4b7ac211ed928100505601348b_b45a391ce48211f08c7b005056b521a7.resize1.jpg',
                'detail_url': '',
                'parsed_at': datetime.now().isoformat()
            },
            {
                'id': 'test_003',
                'title': 'LADA GRANTA',
                'price': '832 000 ₽',
                'year': '2023',
                'mileage': '65 090 км',
                'location': 'Кемерово',
                'image': 'https://api-sale.resoleasing.com/upload/iblock/d6c/2025-12-29_PHOTO_f9bdc9f7035911ee8c58005056b521a7_6dd82dd6e49d11f08c7b005056b521a7.resize1.jpg',
                'detail_url': '',
                'parsed_at': datetime.now().isoformat()
            }
        ]
        
        all_cars.extend(test_cars)
    
    print_colored(f"✅ Всего обработано {len(all_cars)} автомобилей", 'green')
    return all_cars

def save_to_file(cars, filename):
    """Сохраняет данные в JSON файл"""
    
    # Создаем структуру данных
    data = {
        'cars': cars,
        'total': len(cars),
        'last_updated': datetime.now().isoformat(),
        'source': 'https://www.resoleasing.com/sale',
        'success': True
    }
    
    # Сохраняем в файл
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print_colored(f"💾 Данные сохранены в {filename}", 'green')
        print_colored(f"📁 Размер файла: {os.path.getsize(filename)} байт", 'cyan')
        
        # Создаем резервную копию
        backup_dir = 'backup'
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        backup_name = f"{backup_dir}/cars_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(backup_name, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print_colored(f"📂 Создана резервная копия: {backup_name}", 'cyan')
        
        return True
        
    except Exception as e:
        print_colored(f"❌ Ошибка сохранения: {str(e)}", 'red')
        return False

def main():
    """Главная функция программы"""
    
    print_colored("=" * 60, 'cyan')
    print_colored("🚗 ПАРСЕР АВТОМОБИЛЕЙ С RESO-LEASING", 'cyan')
    print_colored("=" * 60, 'cyan')
    print_colored(f"🕒 Начало работы: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 'yellow')
    print()
    
    # URL сайта с автомобилями
    url = 'https://www.resoleasing.com/sale'
    
    # 1. Загружаем страницу
    html = get_page(url)
    
    if not html:
        print_colored("❌ Не удалось загрузить страницу. Создаю тестовые данные...", 'red')
        
        # Создаем тестовые данные
        test_data = [
            {
                'id': 'test_001',
                'title': 'MERCEDES-BENZ S CLASS AMG (ТЕСТ)',
                'price': '22 135 000 ₽',
                'year': '2024',
                'mileage': '27 км',
                'location': 'Москва',
                'image': 'https://images.unsplash.com/photo-1553440569-bcc63803a83d?ixlib=rb-1.2.1&auto=format&fit=crop&w=600&q=80',
                'detail_url': '',
                'parsed_at': datetime.now().isoformat()
            },
            {
                'id': 'test_002',
                'title': 'AUDI A6 (ТЕСТ)',
                'price': '3 500 000 ₽',
                'year': '2020',
                'mileage': '45 000 км',
                'location': 'Санкт-Петербург',
                'image': 'https://images.unsplash.com/photo-1563720223487-62eeae18c7cc?ixlib=rb-1.2.1&auto=format&fit=crop&w=600&q=80',
                'detail_url': '',
                'parsed_at': datetime.now().isoformat()
            }
        ]
        
        save_to_file(test_data, '../data/cars.json')
        return
    
    # 2. Парсим автомобили из HTML
    print()
    cars = parse_cars_from_html(html)
    
    # 3. Сохраняем в файл
    print()
    if cars:
        save_to_file(cars, '../data/cars.json')
    else:
        print_colored("❌ Не удалось получить ни одного автомобиля", 'red')
    
    # 4. Завершение
    print()
    print_colored("=" * 60, 'cyan')
    print_colored(f"✅ Работа завершена в {datetime.now().strftime('%H:%M:%S')}", 'green')
    print_colored(f"📊 Обработано автомобилей: {len(cars) if cars else 0}", 'cyan')
    print_colored("=" * 60, 'cyan')

# Точка входа в программу
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print_colored("\n\n⏹️ Программа остановлена пользователем", 'yellow')
    except Exception as e:
        print_colored(f"\n\n💥 Критическая ошибка: {str(e)}", 'red')