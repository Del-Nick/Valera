from vkbottle import Keyboard, KeyboardButtonColor, Text
from Server.MainDatabase import update_all_users_data, get_all_users_data
from Server.SettingsDatabase import get_all_settings, update_all_settings
from Handlers.Keyboards import *
from Handlers.Registration import add_user_group
from Scripts.Arrays import groups


async def change_time(info_vk, info_bd, settings, message):
    if 'Отмена' in message.text:
        await message.answer('Возвращаюсь к настройкам',
                             keyboard=settings_keyboard(settings, info_bd.time_new_schedule))
        update_all_users_data(info_vk.id, 'action', 'Start')
    else:
        time_trans = message.text.split(':')
        if len(time_trans) == 2:
            time_trans[0] = int(time_trans[0])
            time_trans[1] = int(time_trans[1])
            if 0 <= time_trans[0] < 24:
                if 0 <= time_trans[1] < 60:
                    update_all_users_data(info_vk.id, ['action', 'time_new_schedule'], ['Settings', message.text])
                    info_bd = get_all_users_data(info_vk.id)
                    await message.answer(f'Теперь после {info_bd.time_new_schedule} я буду присылать расписание на '
                                         f'следующий день',
                                         keyboard=settings_keyboard(settings, info_bd.time_new_schedule))
                else:
                    await message.answer('Не могу распознать минуты. Они должен быть в диапазоне [00, 60)',
                                         keyboard=Keyboard(one_time=True).add(Text('Отмена'),
                                                                              color=KeyboardButtonColor.NEGATIVE))
            else:
                await message.answer('Не могу распознать час. Он должен быть в диапазоне [00, 24)',
                                     keyboard=Keyboard(one_time=True).add(Text('Отмена'),
                                                                          color=KeyboardButtonColor.NEGATIVE))
        else:
            await message.answer('Проверь правильность ввода. Напоминаю, что формат должен быть ЧЧ:ММ',
                                 keyboard=Keyboard(one_time=True).add(Text('Отмена'),
                                                                      color=KeyboardButtonColor.NEGATIVE))


async def change_main_group(info_vk, info_bd, settings, message):
    if message.text in groups:
        user_groups = info_bd.group_user.split(', ')
        user_groups[0] = message.text
        update_all_users_data(info_vk.id, 'group_user', ', '.join(user_groups))
        await message.answer(f'Отлично, {info_bd.first_name}! Я запомнил, что ты из группы {user_groups[0]}. Этот '
                             f'параметр можно будет изменить в настройках. Теперь я буду искать информацию для тебя '
                             f'персонально',
                             keyboard=settings_keyboard(settings, info_bd.time_new_schedule))
    else:
        await message.answer(
            'Не могу отыскать такую группу в своей базе. Проверь, нет ли ошибки. Я брал назваия с официального сайта с '
            'расписанием: http://ras.phys.msu.ru')


async def delete_group(info_vk, info_bd, settings, message):
    if 'Отмена' in message.text:
        await message.answer('Возвращаюсь к настройкам', keyboard=settings_keyboard(settings, info_bd.time_new_schedule))
        update_all_users_data(info_vk.id, 'action', 'Settings')
    else:
        user_groups = info_bd.group_user.split(', ')
        if message.text in user_groups[0]:
            await message.answer(
                'Ты не можешь удалить группу, которая в моей памяти обозначена как твоя. Если ты указал её '
                'неправильно, смени её в настройках. Введи номер группы, которую нужно удалить',
                keyboard=Keyboard(one_time=True).add(Text('Отмена'), color=KeyboardButtonColor.NEGATIVE))
        elif message.text not in user_groups:
            await message.answer(
                'Не могу отыскать такую группу в своей базе. Проверь, нет ли ошибки. Список своих групп ты можешь '
                'посмотреть в настройках',
                keyboard=Keyboard(one_time=True).add(Text('Отмена'), color=KeyboardButtonColor.NEGATIVE))
        elif message.text in user_groups:
            user_groups.remove(message.text)
            update_all_users_data(info_vk.id, 'group_user', ', '.join(user_groups))
            info_bd = get_all_users_data(info_vk.id)

            if len(info_bd.group_user.split(', ')) == 1:
                answer = f'ID: {info_vk.id}\n' \
                         f'Имя: {info_bd.first_name}\n' \
                         f'Фамилия: {info_bd.last_name}\n' \
                         f'Группа: {info_bd.group_user}\n' \
                         f'Расписание на следующий день после: {info_bd.time_new_schedule}'
            else:
                groups = info_bd.group_user.split(',')
                answer = f'ID: {info_vk.id}\n' \
                         f'Имя: {info_bd.first_name}\n' \
                         f'Фамилия: {info_bd.last_name}\n' \
                         f'Группа: {groups[0]}\n' \
                         f'Доп. группы: {", ".join(groups[1:])}\n' \
                         f'Расписание на следующий день после: {info_bd.time_new_schedule}'

            await message.answer(f'Группа {message.text} удалена')
            await message.answer(answer, keyboard=settings_keyboard(settings, info_bd.time_new_schedule))
            update_all_users_data(info_vk.id, 'action', 'Settings')
        else:
            await message.answer(
                'Не могу отыскать такую группу в своей базе. Проверь, нет ли ошибки. Список своих групп ты можешь '
                'посмотреть в настройках',
                keyboard=Keyboard(one_time=True).add(Text('Отмена'), color=KeyboardButtonColor.NEGATIVE))


async def choose_time_schedule_seller(info_vk, info_bd, settings, message):
    if 'Отмена' in message.text:
        update_all_settings(info_vk.id, 'schedule_seller')
        settings = get_all_settings(info_vk.id)
        await message.answer('Возвращаюсь к настройкам',
                             keyboard=settings_keyboard(settings, info_bd.time_new_schedule))
        update_all_users_data(info_vk.id, 'action', 'Settings')
    else:
        time_trans = message.text.split(':')
        if len(time_trans) == 2:
            time_trans[0] = int(time_trans[0])
            time_trans[1] = int(time_trans[1])
            if 0 <= time_trans[0] < 24:
                if 0 <= time_trans[1] < 60:
                    update_all_settings(info_vk.id, 'time_schedule_seller', message.text)
                    settings = get_all_settings(info_vk.id)
                    await message.answer(f'Теперь в {message.text} я буду присылать расписание на день',
                                         keyboard=settings_keyboard(settings, info_bd.time_new_schedule))
                    update_all_users_data(info_vk.id, 'action', 'Settings')
                else:
                    await message.answer('Не могу распознать минуты. Они должен быть в диапазоне [00, 60)',
                                         keyboard=Keyboard(one_time=True).add(Text('Отмена'),
                                                                              color=KeyboardButtonColor.NEGATIVE))
            else:
                await message.answer('Не могу распознать час. Он должен быть в диапазоне [00, 24)',
                                     keyboard=Keyboard(one_time=True).add(Text('Отмена'),
                                                                          color=KeyboardButtonColor.NEGATIVE))
        else:
            await message.answer('Проверь правильность ввода. Напоминаю, что формат должен быть ЧЧ:ММ',
                                 keyboard=Keyboard(one_time=True).add(Text('Отмена'),
                                                                      color=KeyboardButtonColor.NEGATIVE))


async def settings_handler(info_vk, info_bd, settings, message):
    if 'Время' in message.text:
        await message.answer(f'После {info_bd.time_new_schedule} я присылаю тебе расписание на следующий день. '
                             f'Чтобы изменить этот параметр, введи время в том же формате:',
                             keyboard=Keyboard(one_time=True).add(Text('Отмена'), color=KeyboardButtonColor.NEGATIVE))
        update_all_users_data(info_vk.id, 'action', 'Settings_change_time')

    elif 'change_time' in info_bd.action:
        await change_time(info_vk, info_bd, settings, message)

    elif 'Сменить группу' in message.text:
        if settings.headman and not settings.admin:
            await message.answer(
                'Староста не может менять группу. Староста, как капитан: покидает корабль последним',
                keyboard=settings_keyboard(settings, info_bd.time_new_schedule))
        else:
            update_all_users_data(info_vk.id, 'action', 'Settings_change_main_group')
            await message.answer('Введи новый номер твоей группы, которая будет считаться основной')

    elif 'change_main_group' in info_bd.action:
        await change_main_group(info_vk, info_bd, settings, message)

    elif 'Добавить группу' in message.text:
        if len(info_bd.group_user.split(', ')) < 3:
            await message.answer('Введи номер группы, которую ты хочешь добавить',
                                 keyboard=Keyboard(one_time=True).add(Text('Отмена'),
                                                                      color=KeyboardButtonColor.NEGATIVE))
            update_all_users_data(info_vk.id, 'action', 'Settings_add_group')

        else:
            await message.answer(
                'Ты не можешь добавить больше 3 групп. Чтобы добавить новую, удали одну из старых в настройках',
                keyboard=settings_keyboard(settings, info_bd.time_new_schedule))

    elif 'add_group' in info_bd.action:
        await add_user_group(info_vk, info_bd, message)

    elif 'Удалить группу' in message.text:
        await message.answer('Введи номер группы, которую ты хочешь удалить',
                             keyboard=Keyboard(one_time=True).add(Text('Отмена'),
                                                                  color=KeyboardButtonColor.NEGATIVE))
        update_all_users_data(info_vk.id, 'action', 'Settings_delete_group')

    elif 'delete_group' in info_bd.action:
        await delete_group(info_vk, info_bd, settings, message)

    elif 'Полное расписание' in message.text:
        update_all_settings(info_vk.id, 'full_schedule')
        settings = get_all_settings(info_vk.id)
        if settings.full_schedule:
            await message.answer('Добавил преподавателей к выводу расписания',
                                 keyboard=settings_keyboard(settings, info_bd.time_new_schedule))
        else:
            await message.answer('Больше не буду отображать преподавателей в расписании',
                                 keyboard=settings_keyboard(settings, info_bd.time_new_schedule))

    elif 'Уведомления' in message.text:
        update_all_settings(info_vk.id, 'notifications')
        settings = get_all_settings(info_vk.id)
        if settings.notifications:
            await message.answer('Включил уведомления о новых ДЗ и учебниках',
                                 keyboard=settings_keyboard(settings, info_bd.time_new_schedule))
        else:
            await message.answer('Уведомления отключены',
                                 keyboard=settings_keyboard(settings, info_bd.time_new_schedule))

    elif 'Присылать расписание' in message.text:
        update_all_settings(info_vk.id, 'schedule_seller')
        settings = get_all_settings(info_vk.id)
        if settings.schedule_seller:
            await message.answer('Укажи время, в которое я буду автоматически присылать тебе расписание на день в формате '
                                 'HH:MM',
                                 keyboard=Keyboard(one_time=True).add(Text('Отмена'),
                                                                  color=KeyboardButtonColor.NEGATIVE))
            update_all_users_data(info_vk.id, 'action', 'Settings_choose_time_schedule_seller')
        else:
            await message.answer('Больше не буду присылать расписание автоматически',
                                 keyboard=settings_keyboard(settings, info_bd.time_new_schedule))

    elif 'choose_time_schedule_seller' in info_bd.action:
        await choose_time_schedule_seller(info_vk, info_bd, settings, message)

    elif 'Помощь' in message.text:
        await message.answer('Скоро здесь появится навигатор по функциям Валеры',
                             keyboard=settings_keyboard(settings, info_bd.time_new_schedule))

    elif 'Вернуться назад' in message.text:
        await message.answer('Возвращаюсь в главное меню',
                             keyboard=standard_keyboard(settings.headman, info_bd))
        update_all_users_data(info_vk.id, 'action', 'Start')

    else:
        return False
