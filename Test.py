from Server.DB import User
from vkbottle.bot import Message

user = User(vk_id=299407304, message=Message)

print(user.vk_name, user.telegram_name)

user.full_schedule = True

user.update()

user = User(vk_id=299407304, message=Message)

print(user.full_schedule)

user.full_schedule = False

user.update()