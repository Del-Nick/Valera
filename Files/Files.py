import json

from PIL import Image


# Схемы этажей
zero_floor_alpha = Image.open(r'Files/Rooms/0 floor alpha.png').convert('RGBA')
first_floor_alpha = Image.open(r'Files/Rooms/1 floor alpha.png').convert('RGBA')
second_floor_alpha = Image.open(r'Files/Rooms/2 floor alpha.png').convert('RGBA')
third_floor_alpha = Image.open(r'Files/Rooms/3 floor alpha.png').convert('RGBA')
fourth_floor_alpha = Image.open(r'Files/Rooms/4 floor alpha.png').convert('RGBA')
fifth_floor_alpha = Image.open(r'Files/Rooms/5 floor alpha.png').convert('RGBA')


# подгружаем файл с расписанием
try:
    with open(f'Files/Schedule.json', encoding='utf-8') as f:
        schedule = json.load(f)

except FileNotFoundError:
    schedule = {}
    print('Не нашёл файл с расписанием')
