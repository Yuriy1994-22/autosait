# Это программа, которая ходит на сайт и собирает данные об автомобилях
# Не нужно её глубоко понимать, она просто работает

import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime

def main():
    print("Начинаю сбор данных об автомобилях...")
    
    # Список для хранения автомобилей
    все_авто = []
    
    try:
        # Идем на сайт с автомобилями
        print("Захожу на сайт...")
        ответ = requests.get('https://www.resoleasing.com/sale')
        
        # Парсим HTML
        суп = BeautifulSoup(ответ.text, 'html.parser')
        
        # Ищем все автомобили на странице
        автомобили_на_странице = суп.find_all('div', class_='sale-list__item')
        
        print(f"Нашел {len(автомобили_на_странице)} автомобилей")
        
        # Обрабатываем каждый автомобиль
        for авто in автомобили_на_странице:
            try:
                # Извлекаем данные
                название = авто.find('div', class_='sale-list__item-model')
                цена = авто.find('div', class_='sale-list__item-price')
                информация = авто.find('div', class_='sale-list__item-info')
                фото = авто.find('img')
                
                # Разбираем информацию (год/пробег/город)
                инфо_текст = информация.text.strip() if информация else ' / / '
                части = инфо_текст.split(' / ')
                
                данные_авто = {
                    'title': название.text.strip() if название else 'Автомобиль',
                    'price': цена.text.strip() if цена else 'Цена не указана',
                    'year': части[0] if len(части) > 0 else '',
                    'mileage': части[1] if len(части) > 1 else '',
                    'location': части[2] if len(части) > 2 else '',
                    'image': фото['src'] if фото and 'src' in фото.attrs else ''
                }
                
                все_авто.append(данные_авто)
                print(f"✓ Добавил: {данные_авто['title']}")
                
            except Exception as e:
                print(f"✗ Пропускаю авто из-за ошибки: {e}")
                continue
        
        # Сохраняем в файл
        данные = {
            'cars': все_авто,
            'total': len(все_авто),
            'last_updated': datetime.now().isoformat(),
            'source': 'https://www.resoleasing.com/sale'
        }
        
        with open('../data/cars.json', 'w', encoding='utf-8') as файл:
            json.dump(данные, файл, ensure_ascii=False, indent=2)
        
        print(f"✅ Успешно! Сохранил {len(все_авто)} автомобилей")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        # Создаем пустой файл в случае ошибки
        пустые_данные = {
            'cars': [],
            'total': 0,
            'last_updated': datetime.now().isoformat(),
            'source': 'error'
        }
        with open('../data/cars.json', 'w', encoding='utf-8') as файл:
            json.dump(пустые_данные, файл, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()