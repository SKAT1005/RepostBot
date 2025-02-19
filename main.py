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

from app.models import Tasks, Messages, SendMessageTask, GlobalNumber

client = telethon.TelegramClient('User', api_id=21546643, api_hash='54194901b3ff3a879cb371f6293a6422',
                                 system_version="4.16.30-vxCUSTOM")


async def create_task(message):
    """Создает задачу на основе сообщения.
    """
    try:
        tasks = message.text.split('\n')
        first = tasks[0].split()
        if first[0] == 'createtask':
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
            for task in tasks[1:]:
                task_list = task.split('"')[0].split()
                task_type = task_list[0]
                if task_type == 'repost':
                    try:
                        from_channel = task_list[1]
                        to_channel = ','.join(task_list[2:])
                        await sync_to_async(Tasks.objects.create)(
                            type=task_type,
                            global_task_id=global_task_id,
                            to_channel=to_channel,
                            from_channel=from_channel,
                        )

                        await message.reply('✅Задача успешно создана✅')
                    except Exception as e:
                        logging.error(f"Ошибка при создании задачи 'repost': {e}")
                        await message.reply(f'Не получилось создать задачу, неверный формат ввода:\n {task}')
                elif task_type == 'randomrepost':
                    try:
                        from_channel = task_list[1]
                        to_channel = ','.join(task_list[2:-1])
                        chance = task_list[-1]
                        await sync_to_async(Tasks.objects.create)(
                            type=task_type,
                            global_task_id=global_task_id,
                            to_channel=to_channel,
                            from_channel=from_channel,
                            chance=chance,
                        )
                        await message.reply('✅Задача успешно создана✅')

                    except Exception as e:
                        logging.error(f"Ошибка при создании задачи 'randomrepost': {e}")
                        await message.reply(f'Не получилось создать задачу, неверный формат ввода:\n {task}')
                elif task_type == 'previousrepost':
                    try:
                        from_channel = task_list[1]
                        to_channel = ','.join(task_list[2:])
                        await sync_to_async(Tasks.objects.create)(
                            type=task_type,
                            global_task_id=global_task_id,
                            to_channel=to_channel,
                            from_channel=from_channel,
                        )
                        await message.reply('✅Задача успешно создана✅')

                    except Exception as e:
                        logging.error(f"Ошибка при создании задачи 'previousrepost': {e}")
                        await message.reply(f'Не получилось создать задачу, неверный формат ввода:\n {task}')
                elif task_type == 'repostminutes':
                    try:
                        from_channel = task_list[1]
                        to_channel = ','.join(task_list[2:-1])
                        minutes = int(task_list[-1])
                        await sync_to_async(Tasks.objects.create)(
                            type=task_type,
                            global_task_id=global_task_id,
                            to_channel=to_channel,
                            from_channel=from_channel,
                            time=minutes,
                        )
                        await message.reply('✅Задача успешно создана✅')

                    except Exception as e:
                        logging.error(f"Ошибка при создании задачи 'repostminutes': {e}")
                        await message.reply(f'Не получилось создать задачу, неверный формат ввода:\n {task}')
                elif task_type == 'randomrepostminutes':
                    try:
                        from_channel = task_list[1]
                        to_channel = ','.join(task_list[2:-2])
                        chance = task_list[-2]
                        minutes = int(task_list[-1])
                        await sync_to_async(Tasks.objects.create)(
                            type=task_type,
                            chance=chance,
                            global_task_id=global_task_id,
                            to_channel=to_channel,
                            from_channel=from_channel,
                            time=minutes,
                        )
                        await message.reply('✅Задача успешно создана✅')

                    except Exception as e:
                        logging.error(f"Ошибка при создании задачи 'randomrepostminutes': {e}")
                        await message.reply(f'Не получилось создать задачу, неверный формат ввода:\n {task}')
                elif task_type == 'previousrepostrandomrepostminutes':
                    try:
                        from_channel = task_list[1]
                        to_channel = ','.join(task_list[2:-2])
                        chance = task_list[-2]
                        minutes = int(task_list[-1])
                        await sync_to_async(Tasks.objects.create)(
                            type=task_type,
                            chance=chance,
                            global_task_id=global_task_id,
                            to_channel=to_channel,
                            from_channel=from_channel,
                            time=minutes,
                        )
                        await message.reply('✅Задача успешно создана✅')
                    except Exception as e:
                        logging.error(f"Ошибка при создании задачи 'previousrepostrandomrepostminutes': {e}")
                        await message.reply(f'Не получилось создать задачу, неверный формат ввода:\n {task}')
                else:
                    logging.warning(f"Неизвестный тип задачи: {task_type}")
                    await message.reply(f'Не удалось создать {task} т.к неизвестный тип задачи')
        elif first[0] == 'list':
            global_task_ids = await sync_to_async(list)(GlobalNumber.objects.all())
            text = ''
            for n, task_id in enumerate(global_task_ids, start=1):
                text += f'{task_id.id}\n' \
                        f'{task_id.description}\n' \
                        f'{task_id.date()}\n'
                for task in await sync_to_async(list)(task_id.tasks.all()):
                    if task.is_active:
                        status = '✅'
                    else:
                        status = '❌'
                    text += f'{status} {task.id}) {task.type} {task.from_channel} {task.to_channel}\n'
                text += '\n=========================\n'
            try:
                await message.reply(text)
            except Exception as e:
                await message.reply('Задач пока нет')
        elif first[0] == 'stopall':
            try:
                id = first[1]
                global_task = await sync_to_async(GlobalNumber.objects.get)(id=id)
                await sync_to_async(global_task.delete)()
                await message.reply(f'Удалил все задачи с номером {first[1]}')
            except Exception as e:
                await message.reply('Неверный ID задачи')
        elif first[0] == 'stoptask':
            try:
                id = first[1]
                task = await sync_to_async(Tasks.objects.get)(id=id)
                await sync_to_async(task.delete)()
                await message.reply(f'Удалил все задачи с номером {first[1]}')
            except Exception as e:
                await message.reply('Неверный ID задачи')
        elif first[0].startswith('https'):
            try:
                if '/+' in first[0]:
                    link = first[0].split('/+')[1]
                    await client(ImportChatInviteRequest(link))
                else:
                    await client(JoinChannelRequest(first[0]))

            except Exception as e:
                logging.error(f"Не удалось подписаться на канал: {e}")
                await message.reply('Не удалось подписаться на канал')
        elif first[0] == 'help':
            text = 'Список задач - list\n\n' \
                   'Удалить задачу - stopall <id задачи>\n\n' \
                   'Создать задачу: createtask <DD.MM.YY HH:MM или 0>-<DD.MM.YY HH:MM или 0> <Описание задачи, оборачивать в "">\n\n' \
                   'Типы задач:\n\n' \
                   'Простой репост: repost <id канала, из которого репостим ><список каналов, в которые репостим через пробел>\n\n' \
                   'Рандомный репост: randomrepost <id канала, из которого репостим ><список каналов, в которые репостим через пробел> <Шанс репоста>\n\n' \
                   'Репост предыдущего поста: previousrepost <id канала, из которого репостим ><список каналов, в которые репостим через пробел>\n\n' \
                   'Репост с задержкой: repostminutes <id канала, из которого репостим ><список каналов, в которые репостим через пробел> <время задержки в минутах>\n\n' \
                   'Рандомный репост с задержкой: randomrepostminutes <id канала, из которого репостим ><список каналов, в которые репостим через пробел> <Шанс репоста> <время задержки в минутах>\n\n' \
                   'Рандомный репост предыдущего поста с задержкой: previousrepostrandomrepostminutes <id канала, из которого репостим ><список каналов, в которые репостим через пробел> <Шанс репоста> <время задержки в минутах>\n\n'
            await message.reply(text)
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
                    logging.error(f'Ошибка при пересылке сообщения: {e}')
    except Exception as e:
        logging.exception("Произошла ошибка в send_message_group:")


async def create_or_ad_message(channel_id, message_id, grouped_id):
    """Создает или добавляет ID сообщения в существующую запись.
    """
    try:
        msg = await sync_to_async(list)(Messages.objects.filter(channel_id=channel_id, grouped_id=grouped_id, messages_id__contains=message_id))
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


async def channel_check(message):
    """Проверяет сообщения в канале и выполняет задачи.
    """
    try:
        channel_id = message.message.peer_id.channel_id
        tasks = await sync_to_async(list)(Tasks.objects.filter(from_channel__icontains=channel_id))
        grouped_id = message.grouped_id
        message_id = message.id

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

            if task.is_active:
                if task.type == 'repost':
                    for to_channel_id in task.to_channel.split(','):
                        try:
                            while True:
                                try:
                                    await client.forward_messages(int(to_channel_id), message_id, channel_id)
                                    break
                                except telethon.errors.FloodWaitError:
                                    tm.sleep(3)
                            await create_or_ad_message(channel_id=channel_id, message_id=message_id,
                                                       grouped_id=grouped_id)
                        except Exception as e:
                            logging.error(f'Ошибка при пересылке сообщения: {e}')
                elif task.type == 'randomrepost':
                    if random.randint(1, 100) <= task.chance:
                        for to_channel_id in task.to_channel.split(','):
                            try:
                                await client.forward_messages(int(to_channel_id), message_id, channel_id)
                                break
                            except telethon.errors.FloodWaitError:
                                tm.sleep(3)
                    await create_or_ad_message(channel_id=channel_id, message_id=message_id, grouped_id=grouped_id)
                elif task.type == 'previousrepost':
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

                    await create_or_ad_message(channel_id=channel_id, message_id=message_id, grouped_id=grouped_id)

                elif task.type == 'repostminutes':
                    if not grouped_id or not await sync_to_async(list)(Messages.objects.filter(grouped_id=grouped_id)):
                        time = timezone.now() + datetime.timedelta(minutes=task.time)
                        need_mesage = await create_or_ad_message(channel_id=channel_id, message_id=message_id,
                                                                 grouped_id=grouped_id)
                        await sync_to_async(SendMessageTask.objects.create)(task=task, message=need_mesage, time=time)

                    await create_or_ad_message(channel_id=channel_id, message_id=message_id, grouped_id=grouped_id)
                elif task.type == 'randomrepostminutes':
                    if random.randint(1, 100) <= task.chance and (
                            not grouped_id or not await sync_to_async(list)(
                        Messages.objects.filter(grouped_id=grouped_id))):
                        time = timezone.now() + datetime.timedelta(minutes=task.time)
                        need_mesage = await create_or_ad_message(channel_id=channel_id, message_id=message_id,
                                                                 grouped_id=grouped_id)
                        await sync_to_async(SendMessageTask.objects.create)(task=task, message=need_mesage, time=time)

                    await create_or_ad_message(channel_id=channel_id, message_id=message_id, grouped_id=grouped_id)
                elif task.type == 'previousrepostrandomrepostminutes':
                    if random.randint(1, 100) <= task.chance:
                        if not grouped_id or not await sync_to_async(list)(
                                Messages.objects.filter(grouped_id=grouped_id)):
                            messages = await sync_to_async(list)(
                                Messages.objects.filter(channel_id=channel_id, is_send=False))
                            if messages:  # Проверяем, есть ли сообщения в списке
                                for message in messages[::-1]:
                                    if str(message_id) not in message.messages_id:
                                        await send_message_group(message, task)
                                        break

                            else:
                                logging.warning(
                                    "Нет предыдущих сообщений для отправки (previousrepostrandomrepostminutes)")

                    await create_or_ad_message(channel_id=channel_id, message_id=message_id, grouped_id=grouped_id)
    except Exception as e:
        logging.exception("Произошла ошибка в channel_check:")


@client.on(events.NewMessage())
async def mk(message):
    """Обрабатывает новые сообщения.
    """
    try:
        if message.is_channel and await sync_to_async(list)(
                Tasks.objects.filter(from_channel=message.message.peer_id.channel_id)):
            await asyncio.sleep(random.uniform(0.01, 5))
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


async def main():
    """Главная функция для запуска клиента.
    """
    await client.start(phone='+79187564306', password='19097007')
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
