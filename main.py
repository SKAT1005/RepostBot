import asyncio
import datetime
import os
import threading
import time
import time as tm
from asgiref.sync import sync_to_async
import django
import telethon
import random
from django.utils import timezone
from telethon import events
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.functions.channels import JoinChannelRequest
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,  # Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),  # Запись в файл bot.log
        logging.StreamHandler()  # Вывод в консоль
    ]
)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RepostBot.settings')

django.setup()

from app.models import Tasks, Messages, SendMessageTask, GlobalNumber, Channel

client = telethon.TelegramClient('User', api_id=21546643, api_hash='54194901b3ff3a879cb371f6293a6422',
                                 system_version="4.16.30-vxCUSTOM")


async def add_channel(to_channel):
    for channel_id in to_channel.split(','):
        try:
            channel = await sync_to_async(Channel.objects.get_or_create)(channel_id=channel_id)
            last_id = list(await client.get_messages(int(channel_id), 1))
            channel, _ = channel
            if last_id:
                last_id = last_id[0].id
                channel.last_message_id = last_id
                await sync_to_async(channel.save)(update_fields=['last_message_id'])
        except Exception as e:
            logging.error(f"Ошибка при создании канала: {e}")


async def create_task(message):
    """Создает задачу на основе сообщения.
    """
    try:
        tasks = message.text.split('\n')
        first = tasks[0].split()
        if first[0].lower() == 'add':
            n = ' '.join(first[1:]).split('"')
            if len(n) >= 2:
                description = n[1]
            else:
                description = None
            start_date, end_date = n[0].split('-')
            end_date = end_date[:-1]
            if start_date == '0':
                start_date = timezone.now()
            else:
                start_date = datetime.datetime.strptime(start_date, "%d.%m.%Y %H:%M")
            if end_date == '0':
                end_date = None
            else:
                end_date = datetime.datetime.strptime(end_date, "%d.%m.%Y %H:%M")
            global_task_id = await sync_to_async(GlobalNumber.objects.create)(
                description=description,
                start_date=start_date,
                end_date=end_date
            )
            await message.reply(f'✅ Задача {global_task_id.id} успешно создана')
            for task in tasks[1:]:
                task_list = task.split('"')[0].split()
                task_type = task_list[0].lower()
                if task_type == 'r':
                    try:
                        from_channel = task_list[1]
                        to_channel = ','.join(task_list[2:])
                        await add_channel(from_channel)
                        await sync_to_async(Tasks.objects.create)(
                            type=task_type,
                            global_task_id=global_task_id,
                            to_channel=to_channel,
                            from_channel=from_channel,
                        )

                    except Exception as e:
                        logging.error(f"Ошибка при создании задачи 'repost': {e}")
                        await message.reply(f'Не получилось создать задачу, неверный формат ввода:\n {task}')
                elif task_type == 'rr':
                    try:
                        from_channel = task_list[1]
                        to_channel = ','.join(task_list[2:-1])
                        chance = task_list[-1]
                        await add_channel(from_channel)
                        await sync_to_async(Tasks.objects.create)(
                            type=task_type,
                            global_task_id=global_task_id,
                            to_channel=to_channel,
                            from_channel=from_channel,
                            chance=chance,
                        )

                    except Exception as e:
                        logging.error(f"Ошибка при создании задачи 'randomrepost': {e}")
                        await message.reply(f'Не получилось создать задачу, неверный формат ввода:\n {task}')
                elif task_type in ['pr', 'ppr', 'pppr']:
                    try:
                        from_channel = task_list[1]
                        to_channel = ','.join(task_list[2:])
                        await add_channel(from_channel)
                        await sync_to_async(Tasks.objects.create)(
                            type=task_type,
                            global_task_id=global_task_id,
                            to_channel=to_channel,
                            from_channel=from_channel,
                        )

                    except Exception as e:
                        logging.error(f"Ошибка при создании задачи 'previousrepost': {e}")
                        await message.reply(f'Не получилось создать задачу, неверный формат ввода:\n {task}')
                elif task_type == 'rm':
                    try:
                        from_channel = task_list[1]
                        to_channel = ','.join(task_list[2:-1])
                        minutes = int(task_list[-1])
                        await add_channel(from_channel)
                        await sync_to_async(Tasks.objects.create)(
                            type=task_type,
                            global_task_id=global_task_id,
                            to_channel=to_channel,
                            from_channel=from_channel,
                            time=minutes,
                        )

                    except Exception as e:
                        logging.error(f"Ошибка при создании задачи 'repostminutes': {e}")
                        await message.reply(f'Не получилось создать задачу, неверный формат ввода:\n {task}')
                elif task_type == 'rrm':
                    try:
                        from_channel = task_list[1]
                        to_channel = ','.join(task_list[2:-2])
                        chance = task_list[-2]
                        minutes = int(task_list[-1])
                        await add_channel(from_channel)
                        await sync_to_async(Tasks.objects.create)(
                            type=task_type,
                            chance=chance,
                            global_task_id=global_task_id,
                            to_channel=to_channel,
                            from_channel=from_channel,
                            time=minutes,
                        )

                    except Exception as e:
                        logging.error(f"Ошибка при создании задачи 'randomrepostminutes': {e}")
                        await message.reply(f'Не получилось создать задачу, неверный формат ввода:\n {task}')
                elif task_type in ['prrm', 'pprrm', 'ppprrm']:
                    try:
                        from_channel = task_list[1]
                        to_channel = ','.join(task_list[2:-2])
                        chance = task_list[-2]
                        minutes = int(task_list[-1])
                        await add_channel(from_channel)
                        await sync_to_async(Tasks.objects.create)(
                            type=task_type,
                            chance=chance,
                            global_task_id=global_task_id,
                            to_channel=to_channel,
                            from_channel=from_channel,
                            time=minutes,
                        )
                    except Exception as e:
                        logging.error(f"Ошибка при создании задачи 'previousrepostrandomrepostminutes': {e}")
                        await message.reply(f'Не получилось создать задачу, неверный формат ввода:\n {task}')
                else:
                    logging.warning(f"Неизвестный тип задачи: {task_type}")
                    await message.reply(f'Не удалось создать {task} т.к неизвестный тип задачи')
        elif first[0].lower() == 'list':
            global_task_ids = await sync_to_async(list)(GlobalNumber.objects.all())
            text = ''
            for n, task_id in enumerate(global_task_ids, start=1):
                text += f'<b><i>{task_id.id} | {task_id.description}</b></i>\n' \
                        f'{task_id.start_date_str()} — {task_id.end_date_str()}\n'
                for task in await sync_to_async(list)(task_id.tasks.all()):
                    text += f'{task.task_str()}\n'
                text += '\n=========================\n'
            try:
                await message.reply(text, parse_mode='HTML')
            except Exception as e:
                await message.reply('Задач пока нет')
        elif first[0].lower() == 'del':
            try:
                id = first[1]
                global_task = await sync_to_async(GlobalNumber.objects.get)(id=id)
                await sync_to_async(global_task.delete)()
                await message.reply(f'🗑 Задача номер {id} удалена')
            except Exception as e:
                await message.reply('Неверный ID задачи')
        elif first[0].lower() == 'stop':
            try:
                id = first[1]
                task = await sync_to_async(Tasks.objects.get)(id=id)
                await sync_to_async(task.delete)()
                await message.reply(f'🗑 Подзадача номер {id} удалена')
            except Exception as e:
                await message.reply('Неверный ID задачи')
        elif first[0].lower() == 'pause':
            try:
                id = first[1]
                task = await sync_to_async(Tasks.objects.get)(id=id)
                task.is_pause = True
                await sync_to_async(task.save)()
                await message.reply(f'⏸️ Подзадача номер {id} поставлена на паузу')
            except Exception as e:
                await message.reply('Неверный ID задачи')
        elif first[0].lower() == 'play':
            try:
                id = first[1]
                task = await sync_to_async(Tasks.objects.get)(id=id)
                task.is_pause = False
                await sync_to_async(task.save)()
                await message.reply(f'▶️️ Подзадача номер {id} снята с паузы')
            except Exception as e:
                await message.reply('Неверный ID задачи')
        elif first[0].startswith('https'):
            try:
                if '/+' in first[0]:
                    link = first[0].split('/+')[1]
                    n = await client(ImportChatInviteRequest(link))
                else:
                    n = await client(JoinChannelRequest(first[0]))
                await message.reply(f'✅Подписка успешна {n.chats[0].id}')

            except Exception as e:
                logging.error(f"Не удалось подписаться на канал: {e}")
                await message.reply('❌Не удалось подписаться, выполните действие вручную')
        elif first[0].lower() == 'help':
            text = ('Общие команды: \n'
                    '• <b>help</b> — <u>Список команд</u>\n'
                    '• <b>list</b> — <u>Список задач</u>\n'
                    '• <b>add</b> <ДД.ММ.ГГГГ ЧЧ:ММ или 0>-<ДД.ММ.ГГГГ ЧЧ:ММ или 0> <"Комментарий"> — <u>Создать задачу</u>\n'
                    '• <b>del</b> <Номер задачи> — <u>Удалить задачу</u>\n'
                    '• <b>pause</b> <Номер подзадачи> — <u>Пауза для подзадачи</u>\n'
                    '• <b>play</b> <Номер подзадачи> — <u>Старт для подзадачи</u>\n'
                    '• <b>stop</b> <Номер подзадачи> — <u>Удалить подзадачу</u>\n\n'
                    'Репосты:\n'
                    '• <b>r</b> <id источника ><id получателей через пробел> — <u>Простой репост</u>\n'
                    '• <b>rr</b> <id источника ><id получателей через пробел> <шанс репоста> — <u>Репост с вероятностью</u>\n'
                    '• <b>pr</b> <id источника ><id получателей через пробел> — <u>Репост предыдущего поста</u>\n'
                    '• <b>ppr</b> <id источника ><id получателей через пробел> — <u>Репост пред-предыдущего поста</u>\n'
                    '• <b>pppr</b> <id источника ><id получателей через пробел> — <u>Репост пред-пред-предыдущего поста</u>\n'
                    '• <b>rm</b> <id источника ><id получателей через пробел> <задержка в минутах> — <u>Репост с задержкой</u>\n'
                    '• <b>rrm</b> <id источника ><id получателей через пробел> <шанс репоста> <задержка в минутах> — <u>Рандомный репост с задержкой</u>\n'
                    '• <b>prrm</b> <id источника ><id получателей через пробел> <шанс репоста> <задержка в минутах> — <u>Рандомный репост предыдущего поста с задержкой</u>\n'
                    '• <b>pprrm</b> <id источника ><id получателей через пробел> <шанс репоста> <задержка в минутах> — <u>Рандомный репост пред-предыдущего поста с задержкой</u>\n'
                    '• <b>ppprrm</b> <id источника ><id получателей через пробел> <шанс репоста> <задержка в минутах> — <u>Рандомный репост пред-пред-предыдущего поста с задержкой</u>')
            await message.reply(text, parse_mode='HTML')
    except Exception as e:
        logging.exception("Произошла ошибка в create_task:")


async def send_message_group(messages, task):
    """Отправляет группу сообщений в канал.
    """
    try:
        message = list(map(int, messages.messages_id.split(',')))
        for to_channel_id in task.to_channel.split(','):
            try:
                while True:
                    try:
                        await client.forward_messages(int(to_channel_id), message, int(messages.channel_id))
                        time.sleep(2)
                        break
                    except telethon.errors.FloodWaitError:
                        time.sleep(3)
            except Exception as e:
                logging.error(f'⭕️ Не удалось переслать сообщение!\n'
                              f'Подзадача {task.id}')
    except Exception as e:
        logging.exception("Произошла ошибка в send_message_group:")


async def create_or_ad_message(channel_id, message_id, grouped_id):
    """Создает или добавляет ID сообщения в существующую запись.
    """
    try:
        msg = await sync_to_async(list)(
            Messages.objects.filter(channel_id=channel_id, grouped_id=grouped_id, messages_id__contains=message_id))
        if not msg:
            messages = await sync_to_async(list)(Messages.objects.filter(channel_id=channel_id, grouped_id=grouped_id))
            message = messages[0] if messages else None  # Исправлено для обработки пустого списка
            if message and grouped_id:
                message.messages_id += f',{message_id}'
                await sync_to_async(message.save)(update_fields=['messages_id'])
            else:
                message = await sync_to_async(Messages.objects.create)(channel_id=channel_id, grouped_id=grouped_id,
                                                                       messages_id=f'{message_id}')
            return message
        return msg[0]
    except Exception as e:
        logging.exception("Произошла ошибка в create_or_ad_message:")


async def channel_check(message, album=False):
    """Проверяет сообщения в канале и выполняет задачи.
    """
    try:
        channel_id = message.message.peer_id.channel_id
        tasks = await sync_to_async(list)(Tasks.objects.filter(from_channel__icontains=channel_id))
        grouped_id = message.grouped_id
        message_id = message.id
        while True:
            try:
                channel = await sync_to_async(Channel.objects.get)(channel_id=channel_id)
                if message_id == 1:
                    break
                elif str(message_id - 1) == channel.last_message_id:
                    break
                tm.sleep(0.01)
            except Exception as e:
                logging.error(f'Не смог найти канал {channel_id}: {e}')
        for task in tasks:
            global_task = await sync_to_async(GlobalNumber.objects.get)(tasks=task)
            now_time = timezone.now() + datetime.timedelta(hours=3)
            if (global_task.start_date and now_time < global_task.start_date) or (
                    global_task.end_date and now_time >= global_task.end_date):
                task.is_active = False
                await sync_to_async(task.save)(update_fields=['is_active'])
            elif (global_task.start_date and timezone.now() >= global_task.start_date) or (
                    global_task.end_date and timezone.now() < global_task.end_date):
                task.is_active = True
                await sync_to_async(task.save)(update_fields=['is_active'])

            if task.is_active and not task.is_pause:
                if task.type == 'r':
                    for to_channel_id in task.to_channel.split(','):
                        try:
                            while True:
                                try:
                                    if album:
                                        await client.forward_messages(int(to_channel_id), album, channel_id)
                                    else:
                                        await client.forward_messages(int(to_channel_id), message_id, channel_id)
                                    break
                                except telethon.errors.FloodWaitError:
                                    tm.sleep(3)
                            if album:
                                for msg in album:
                                    await create_or_ad_message(channel_id=channel_id, message_id=msg.id,
                                                               grouped_id=grouped_id)
                            else:
                                await create_or_ad_message(channel_id=channel_id, message_id=message_id,
                                                           grouped_id=grouped_id)
                        except Exception as e:
                            logging.error(f'Ошибка при пересылке сообщения из {channel_id}: {e}')
                elif task.type == 'rr':
                    if random.randint(1, 100) <= task.chance:
                        for to_channel_id in task.to_channel.split(','):
                            try:
                                if album:
                                    await client.forward_messages(int(to_channel_id), album, channel_id)
                                else:
                                    await client.forward_messages(int(to_channel_id), message_id, channel_id)
                                break
                            except telethon.errors.FloodWaitError:
                                tm.sleep(3)
                    if album:
                        for msg in album:
                            await create_or_ad_message(channel_id=channel_id, message_id=msg.id,
                                                       grouped_id=grouped_id)
                    else:
                        await create_or_ad_message(channel_id=channel_id, message_id=message_id,
                                                   grouped_id=grouped_id)
                elif task.type == 'pr':
                    if not grouped_id or not await sync_to_async(list)(Messages.objects.filter(grouped_id=grouped_id)):
                        messages = await sync_to_async(list)(
                            Messages.objects.filter(channel_id=channel_id, is_send=False))
                        if messages:
                            for message in messages[::-1]:
                                if str(message_id) not in message.messages_id:
                                    await send_message_group(message, task)
                                    break

                        else:
                            logging.warning("Нет предыдущих сообщений для отправки (previousrepost)")

                    if album:
                        for msg in album:
                            await create_or_ad_message(channel_id=channel_id, message_id=msg.id,
                                                       grouped_id=grouped_id)
                    else:
                        await create_or_ad_message(channel_id=channel_id, message_id=message_id,
                                                   grouped_id=grouped_id)
                elif task.type == 'ppr':
                    if not grouped_id or not await sync_to_async(list)(Messages.objects.filter(grouped_id=grouped_id)):
                        messages = await sync_to_async(list)(
                            Messages.objects.filter(channel_id=channel_id, is_send=False))
                        if messages:
                            n = 1
                            for message in messages[::-1]:
                                if str(message_id) not in message.messages_id:
                                    if n == 0:
                                        await send_message_group(message, task)
                                        break
                                    n -= 1

                        else:
                            logging.warning("Нет предыдущих сообщений для отправки (previousrepost)")

                    if album:
                        for msg in album:
                            await create_or_ad_message(channel_id=channel_id, message_id=msg.id,
                                                       grouped_id=grouped_id)
                    else:
                        await create_or_ad_message(channel_id=channel_id, message_id=message_id,
                                                   grouped_id=grouped_id)
                elif task.type == 'pppr':
                    if not grouped_id or not await sync_to_async(list)(Messages.objects.filter(grouped_id=grouped_id)):
                        messages = await sync_to_async(list)(
                            Messages.objects.filter(channel_id=channel_id, is_send=False))
                        if messages:
                            n = 2
                            for message in messages[::-1]:
                                if str(message_id) not in message.messages_id:
                                    if n == 0:
                                        await send_message_group(message, task)
                                        break
                                    n -= 1

                        else:
                            logging.warning("Нет предыдущих сообщений для отправки (previousrepost)")

                    if album:
                        for msg in album:
                            await create_or_ad_message(channel_id=channel_id, message_id=msg.id,
                                                       grouped_id=grouped_id)
                    else:
                        await create_or_ad_message(channel_id=channel_id, message_id=message_id,
                                                   grouped_id=grouped_id)

                elif task.type == 'rm':
                    if not grouped_id or not await sync_to_async(list)(Messages.objects.filter(grouped_id=grouped_id)):
                        time = timezone.now() + datetime.timedelta(minutes=task.time)
                        if album:
                            for msg in album:
                                need_mesage = await create_or_ad_message(channel_id=channel_id, message_id=msg.id,
                                                           grouped_id=grouped_id)
                        else:
                            need_mesage = await create_or_ad_message(channel_id=channel_id, message_id=message_id,
                                                       grouped_id=grouped_id)
                        await sync_to_async(SendMessageTask.objects.create)(task=task, message=need_mesage, time=time)

                    await create_or_ad_message(channel_id=channel_id, message_id=message_id, grouped_id=grouped_id)
                elif task.type == 'rrm':
                    if random.randint(1, 100) <= task.chance and (
                            not grouped_id or not await sync_to_async(list)(
                        Messages.objects.filter(grouped_id=grouped_id))):
                        time = timezone.now() + datetime.timedelta(minutes=task.time)
                        if album:
                            for msg in album:
                                need_mesage = await create_or_ad_message(channel_id=channel_id, message_id=msg.id,
                                                                         grouped_id=grouped_id)
                        else:
                            need_mesage = await create_or_ad_message(channel_id=channel_id, message_id=message_id,
                                                                     grouped_id=grouped_id)
                        await sync_to_async(SendMessageTask.objects.create)(task=task, message=need_mesage, time=time)

                    else:
                        if album:
                            for msg in album:
                                need_mesage = await create_or_ad_message(channel_id=channel_id, message_id=msg.id,
                                                           grouped_id=grouped_id)
                        else:
                            need_mesage = await create_or_ad_message(channel_id=channel_id, message_id=message_id,
                                                       grouped_id=grouped_id)
                elif task.type == 'prrm':
                    if random.randint(1, 100) <= task.chance:
                        time = timezone.now() + datetime.timedelta(minutes=task.time)
                        if not grouped_id or not await sync_to_async(list)(
                                Messages.objects.filter(grouped_id=grouped_id)):
                            messages = await sync_to_async(list)(
                                Messages.objects.filter(channel_id=channel_id, is_send=False))
                            if messages:  # Проверяем, есть ли сообщения в списке
                                for message in messages[::-1]:
                                    if str(message_id) not in message.messages_id:
                                        await sync_to_async(SendMessageTask.objects.create)(task=task, message=message, time=time)
                                        break

                            else:
                                logging.warning(
                                    "Нет предыдущих сообщений для отправки (previousrepostrandomrepostminutes)")
                    if album:
                        for msg in album:
                            await create_or_ad_message(channel_id=channel_id, message_id=msg.id,
                                                       grouped_id=grouped_id)
                    else:
                        await create_or_ad_message(channel_id=channel_id, message_id=message_id,
                                                   grouped_id=grouped_id)
                elif task.type == 'pprrm':
                    if random.randint(1, 100) <= task.chance:
                        time = timezone.now() + datetime.timedelta(minutes=task.time)
                        if not grouped_id or not await sync_to_async(list)(
                                Messages.objects.filter(grouped_id=grouped_id)):
                            messages = await sync_to_async(list)(
                                Messages.objects.filter(channel_id=channel_id, is_send=False))
                            if messages:  # Проверяем, есть ли сообщения в списке
                                n = 1
                                for message in messages[::-1]:
                                    if str(message_id) not in message.messages_id:
                                        if n == 0:
                                            await sync_to_async(SendMessageTask.objects.create)(task=task, message=message, time=time)
                                            break
                                        n -= 1

                            else:
                                logging.warning(
                                    "Нет предыдущих сообщений для отправки (previousrepostrandomrepostminutes)")

                    if album:
                        for msg in album:
                            await create_or_ad_message(channel_id=channel_id, message_id=msg.id,
                                                       grouped_id=grouped_id)
                    else:
                        await create_or_ad_message(channel_id=channel_id, message_id=message_id,
                                                   grouped_id=grouped_id)
                elif task.type == 'ppprrm':
                    if random.randint(1, 100) <= task.chance:
                        time = timezone.now() + datetime.timedelta(minutes=task.time)
                        if not grouped_id or not await sync_to_async(list)(
                                Messages.objects.filter(grouped_id=grouped_id)):
                            messages = await sync_to_async(list)(
                                Messages.objects.filter(channel_id=channel_id, is_send=False))
                            if messages:  # Проверяем, есть ли сообщения в списке
                                for message in messages[::-1]:
                                    n = 2
                                    if str(message_id) not in message.messages_id:
                                        if n == 0:
                                            await sync_to_async(SendMessageTask.objects.create)(task=task, message=message, time=time)
                                            break
                                        n -= 1

                            else:
                                logging.warning(
                                    "Нет предыдущих сообщений для отправки (previousrepostrandomrepostminutes)")

                    if album:
                        for msg in album:
                            await create_or_ad_message(channel_id=channel_id, message_id=msg.id,
                                                       grouped_id=grouped_id)
                    else:
                        await create_or_ad_message(channel_id=channel_id, message_id=message_id,
                                                   grouped_id=grouped_id)
        channel.last_message_id = message_id
        await sync_to_async(channel.save)(update_fields=['last_message_id'])

    except Exception as e:
        logging.exception("Произошла ошибка в channel_check:")

@client.on(events.Album())
async def handler(event):
    message = event.message
    if message.is_channel and await sync_to_async(list)(
            Tasks.objects.filter(from_channel=message.message.peer_id.channel_id)):
        await channel_check(message, event.messages)

@client.on(events.NewMessage())
async def mk(message):
    """Обрабатывает новые сообщения.
    """
    try:
        if message.is_channel and await sync_to_async(list)(
                Tasks.objects.filter(from_channel=message.message.peer_id.channel_id)):
            await channel_check(message)
        elif message.is_private and message.sender_id in [595650100, 1288389919, 8175762996]:
            await create_task(message)
        else:
            logging.debug(f"Сообщение проигнорировано (не канал или не от доверенного пользователя)")
    except Exception as e:
        logging.exception("Произошла ошибка в mk:")


async def send_time_message():
    """Отправляет сообщения, запланированные по времени.
    """
    while True:
        try:
            for message in await sync_to_async(list)(SendMessageTask.objects.all()):
                if message.time <= timezone.now():
                    task = await sync_to_async(Tasks.objects.get)(send_messages_task=message)
                    messages = await sync_to_async(Messages.objects.get)(messages_task=message)
                    await send_message_group(messages, task)
                    await sync_to_async(message.delete)()
            # Заменено time.sleep на asyncio.sleep
        except Exception as e:
            logging.exception("Произошла ошибка в send_time_message:")
        await asyncio.sleep(1)


async def test():
    for task in await sync_to_async(list)(Tasks.objects.all()):
        await add_channel(task.from_channel)


async def main():
    """Главная функция для запуска клиента.
    """
    await client.start(phone='+79187564306', password='19097007')
    await test()
    task = asyncio.create_task(send_time_message())
    try:
        await client.send_message('skat100500', '12344')
        await client.run_until_disconnected()
    except Exception as e:
        logging.critical(f"Ошибка в main: {e}")
    finally:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass  # Игнорируем CancelledError, если задача была отменена


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
