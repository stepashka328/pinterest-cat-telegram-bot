import os
import json
import requests

# === НАСТРОЙКИ ===
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Описание под фото (МОЖЕТЕ ИЗМЕНИТЬ)
CAPTION = """🐱 Случайный котик дня!

#коты #котики #cats #cute #мемы
"""

# Память опубликованных ссылок (защита от повторов)
FILE_PATH = 'posted.json'

def load_posted():
    try:
        with open(FILE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_posted(posted):
    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(posted, f, ensure_ascii=False, indent=2)

def get_cat_image_url():
    """Получает ссылку на случайное фото кота"""
    try:
        # API возвращает JSON с полем "url"
        response = requests.get('https://api.thecatapi.com/v1/images/search', timeout=10)
        data = response.json()
        return data[0]['url']
    except Exception as e:
        print(f"❌ Ошибка API: {e}")
        return None

def download_image(url):
    """Скачивает картинку в память"""
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            return response.content
    except:
        pass
    return None

def send_photo(image_bytes, caption):
    """Отправляет фото в Telegram"""
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto'
    files = {'photo': ('cat.jpg', image_bytes, 'image/jpeg')}
    data = {'chat_id': TELEGRAM_CHAT_ID, 'caption': caption, 'parse_mode': 'HTML'}
    
    resp = requests.post(url, files=files, data=data, timeout=30)
    return resp.status_code == 200

def main():
    posted = load_posted()
    print(f"📦 В памяти {len(posted)} фото")
    
    # Пробуем получить уникальное фото (макс 3 попытки)
    for _ in range(3):
        img_url = get_cat_image_url()
        if img_url and img_url not in posted:
            break
    else:
        print("⚠️ Не удалось найти новое фото, очищаю историю")
        posted = []
        img_url = get_cat_image_url()
    
    if not img_url:
        print("❌ Не получен URL картинки")
        return
        
    print(f"📥 Скачиваю: {img_url}")
    image_bytes = download_image(img_url)
    
    if image_bytes and send_photo(image_bytes, CAPTION):
        print("✅ Фото опубликовано!")
        posted.append(img_url)
        save_posted(posted[-50:])  # Храним последние 50, чтобы файл не рос
    else:
        print("❌ Ошибка отправки или скачивания")

if __name__ == '__main__':
    main()
