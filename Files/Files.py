import json
from PIL import Image


if __name__ == '__main__':
    path = ''

else:
    path = 'Files/'


# подгружаем файл с расписанием
try:
    with open(f'{path}Schedule.json', encoding='utf-8') as f:
        schedule = json.load(f)

except FileNotFoundError:
    schedule = {}
    print('Не нашёл файл с расписанием\n')


try:
    alpha_0_floor = Image.open(f'{path}Rooms/0 floor alpha.png').convert('RGBA')
    alpha_1_floor = Image.open(f'{path}Rooms/1 floor alpha.png').convert('RGBA')
    alpha_2_floor = Image.open(f'{path}Rooms/2 floor alpha.png').convert('RGBA')
    alpha_3_floor = Image.open(f'{path}Rooms/3 floor alpha.png').convert('RGBA')
    alpha_4_floor = Image.open(f'{path}Rooms/4 floor alpha.png').convert('RGBA')
    alpha_5_floor = Image.open(f'{path}Rooms/5 floor alpha.png').convert('RGBA')

except FileNotFoundError:
    alpha_0_floor = None
    alpha_1_floor = None
    alpha_2_floor = None
    alpha_3_floor = None
    alpha_4_floor = None
    alpha_5_floor = None
    print('Не нашёл планы этажей с альфа-каналом\n')