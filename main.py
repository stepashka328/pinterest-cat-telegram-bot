import os
import json
import time
import random
import requests
from bs4 import BeautifulSoup

# === НАСТРОЙКИ ===
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
PINTEREST_URL = 'https://www.pinterest.com/search/pins/?q=cute%20cats'
FILE_PATH = 'posted.json'

# Описание под каждым фото (ПОТОМ ИЗМЕНИТЕ)
CAPTION = """🐱 Милый котик! 

#коты #котики #cats #cute #мемы
"""

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
}

def load_posted():
    try:
        with open(FILE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_posted(posted):
    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(posted, f, ensure_ascii=False, indent=2)

def get_pinterest_images():
    """Парсит Pinterest и возвращает ссылки на картинки"""
    try:
        response = requests.get(PINTEREST_URL, headers=HEADERS, timeout=30)
        if response.status_code != 200:
            print(f"❌ Ошибка {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        images = []
        
        # Ищем все img с src
        for img in soup.find_all('img'):
            src = img.get('src')
            if src and ('i.pinimg.com' in src or 'pinimg.com' in src):
                # Берем оригинальное качество (736x или original)
                if '236x' in src:
                    src = src.replace('236x', '736x')
                elif '150x150' in src:
                    src = src.replace('150x150', '736x')
                
                if src not in images:
                    images.append(src)
        
        print(f"🔍 Найдено картинок: {len(images)}")
        return images[:10]  # Возвращаем первые 10
    
    except Exception as e:
        print(f"❌ Ошибка парсинга: {e}")
        return []

def download_image(url):
    """Скачивает картинку"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            return response.content
    except:
        pass
    return None

def send_photo_to_telegram(image_bytes, caption):
    """Отправляет фото в Telegram"""
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto'
    files = {'photo': ('cat.jpg', image_bytes, 'image/jpeg')}
    data = {
        'chat_id': TELEGRAM_CHAT_ID,
        'caption': caption,
        'parse_mode': 'HTML'
    }
    
    response = requests.post(url, files=files, data=data, timeout=30)
    return response.status_code == 200

def main():
    posted = load_posted()
    print(f"📦 Загружено {len(posted)} уже опубликованных ID")
    
    images = get_pinterest_images()
    if not images:
        print("❌ Картинки не найдены")
        return
    
    # Выбираем случайную картинку, которой еще не было
    available = [img for img in images if img not in posted]
    
    if not available:
        print("⚠️ Все картинки уже опубликованы, очищаем историю")
        posted = []
        available = images
    
    # Берем одну случайную
    selected = random.choice(available)
    print(f"📤 Публикуем: {selected[:60]}...")
    
    # Скачиваем и отправляем
    image_bytes = download_image(selected)
    if image_bytes:
        if send_photo_to_telegram(image_bytes, CAPTION):
            print("✅ Опубликовано в Telegram!")
            posted.append(selected)
            save_posted(posted[-100:])  # Храним последние 100
        else:
            print("❌ Ошибка отправки в Telegram")
    else:
        print("❌ Не удалось скачать картинку")

if __name__ == '__main__':
    main()
