from datetime import datetime
import difflib
from Scripts.Rooms import prefirst_floor_coord
from Files.Files import schedule

# while True:
#     print(difflib.get_close_matches(input('Кабинет:  ').lower(), prefirst_floor_coord, n=10))

# print('325' in schedule.keys())

temp = 65

if temp:
    print(datetime.now())