
import asyncio
import datetime
import os
import threading
import time
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

from app.models import Tasks, Messages, SendMessageTask
client = telethon.TelegramClient('User', api_id=21546643, api_hash='54194901b3ff3a879cb371f6293a6422',
                                     system_version="4.16.30-vxCUSTOM")


async def create_task(message):
    """Создает задачу на основе сообщения.
    """
    try:
        tasks = message.text.split('\n')
        first = tasks[0].split()
        global_task_id = int(time.time())
        if first[0] == 'createtask':
            start_date, end_date = ' '.join(first[1:]).split('-')
            if start_date == '0':
                start_date = None
            else:
                start_date = datetime.datetime.strptime(start_date, "%d.%m.%Y %H:%M")
            if end_date == '0':
                end_date = None
            else:
                end_date = datetime.datetime.strptime(end_date, "%d.%m.%Y %H:%M")
            for task in tasks[1:]:
                if len(task.split('"')) == 3:
                    description = task.split('"')[1]
                else:
                    description = None
                task_list = task.split('"')[0].split()
                task_type = task_list[0]
                if task_type == 'repost':
                    try:
                        to_channel = task_list[1]
                        from_channel = ','.join(task_list[2:])
                        await sync_to_async(Tasks.objects.create)(
                            type=task_type,
                            global_task_id=global_task_id,
                            to_channel=to_channel,
                            from_channel=from_channel,
                            start_date=start_date,
                            end_date=end_date,
                            description=description
                        )
                        logging.info(f"Создана задача типа 'repost' для канала {to_channel} из {from_channel}")

                    except Exception as e:
                        logging.error(f"Ошибка при создании задачи 'repost': {e}")
                        await client.send_message(message.sender_id,
                                                  f'Не получилось создать задачу, неверный формат ввода:\n {task}')
                elif task_type == 'randomrepost':
                    try:
                        to_channel = task_list[1]
                        from_channel = ','.join(task_list[2:-1])
                        chance = task_list[-1]
                        await sync_to_async(Tasks.objects.create)(
                            type=task_type,
                            global_task_id=global_task_id,
                            to_channel=to_channel,
                            from_channel=from_channel,
                            start_date=start_date,
                            end_date=end_date,
                            description=description,
                            chance=chance
                        )
                        logging.info(f"Создана задача типа 'randomrepost' для канала {to_channel} из {from_channel} с шансом {chance}")

                    except Exception as e:
                        logging.error(f"Ошибка при создании задачи 'randomrepost': {e}")
                        await client.send_message(message.sender_id,
                                                  f'Не получилось создать задачу, неверный формат ввода:\n {task}')
                elif task_type == 'previousrepost':
                    try:
                        to_channel = task_list[1]
                        from_channel = ','.join(task_list[2:])
                        await sync_to_async(Tasks.objects.create)(
                            type=task_type,
                            global_task_id=global_task_id,
                            to_channel=to_channel,
                            from_channel=from_channel,
                            start_date=start_date,
                            end_date=end_date,
                            description=description
                        )
                        logging.info(f"Создана задача типа 'previousrepost' для канала {to_channel} из {from_channel}")

                    except Exception as e:
                        logging.error(f"Ошибка при создании задачи 'previousrepost': {e}")
                        await client.send_message(message.sender_id,
                                                  f'Не получилось создать задачу, неверный формат ввода:\n {task}')
                elif task_type == 'repostminutes':
                    try:
                        to_channel = task_list[1]
                        from_channel = ','.join(task_list[2:-1])
                        minutes = int(task_list[-1])
                        await sync_to_async(Tasks.objects.create)(
                            type=task_type,
                            global_task_id=global_task_id,
                            to_channel=to_channel,
                            from_channel=from_channel,
                            start_date=start_date,
                            time=minutes,
                            end_date=end_date,
                            description=description
                        )
                        logging.info(f"Создана задача типа 'repostminutes' для канала {to_channel} из {from_channel} с интервалом {minutes} минут")

                    except Exception as e:
                        logging.error(f"Ошибка при создании задачи 'repostminutes': {e}")
                        await client.send_message(message.sender_id,
                                                  f'Не получилось создать задачу, неверный формат ввода:\n {task}')
                elif task_type == 'randomrepostminutes':
                    try:
                        to_channel = task_list[1]
                        from_channel = ','.join(task_list[2:-2])
                        chance = task_list[-2]
                        minutes = int(task_list[-1])
                        await sync_to_async(Tasks.objects.create)(
                            type=task_type,
                            chance=chance,
                            global_task_id=global_task_id,
                            to_channel=to_channel,
                            from_channel=from_channel,
                            start_date=start_date,
                            time=minutes,
                            end_date=end_date,
                            description=description
                        )
                        logging.info(f"Создана задача типа 'randomrepostminutes' для канала {to_channel} из {from_channel} с шансом {chance} и интервалом {minutes} минут")

                    except Exception as e:
                        logging.error(f"Ошибка при создании задачи 'randomrepostminutes': {e}")
                        await client.send_message(message.sender_id,
                                                  f'Не получилось создать задачу, неверный формат ввода:\n {task}')
                elif task_type == 'previousrepostrandomrepostminutes':
                    try:
                        to_channel = task_list[1]
                        from_channel = ','.join(task_list[2:-2])
                        chance = task_list[-2]
                        minutes = int(task_list[-1])
                        await sync_to_async(Tasks.objects.create)(
                            type=task_type,
                            chance=chance,
                            global_task_id=global_task_id,
                            to_channel=to_channel,
                            from_channel=from_channel,
                            start_date=start_date,
                            time=minutes,
                            end_date=end_date,
                            description=description
                        )
                        logging.info(f"Создана задача типа 'previousrepostrandomrepostminutes' для канала {to_channel} из {from_channel} с шансом {chance} и интервалом {minutes} минут")
                    except Exception as e:
                        logging.error(f"Ошибка при создании задачи 'previousrepostrandomrepostminutes': {e}")
                        await client.send_message(message.sender_id,
                                                  f'Не получилось создать задачу, неверный формат ввода:\n {task}')
                else:
                    logging.warning(f"Неизвестный тип задачи: {task_type}")
                    await client.send_message(message.sender_id, f'Не удалось создать {task} т.к неизвестный тип задачи')
        elif first[0] == 'list':
            global_task_ids = await sync_to_async(list)(Tasks.objects.values_list('global_task_id', flat=True))
            text = ''
            for task_id in global_task_ids:
                text += f'{task_id}\n'
                for task in await sync_to_async(list)(Tasks.objects.filter(global_task_id=task_id)):
                    if task.is_active:
                        status = '✅'
                    else:
                        status = '❌'
                    text += f'{task.id} {status}, {task.type}, {task.to_channel}, {task.description}\n'
                text += '\n=========================\n'
            try:
                await message.reply(text)
                logging.info(f"Отправлен список задач")
            except Exception as e:
                logging.error(f"Ошибка при отправке списка задач: {e}")
                await message.reply('Задач пока нет')
        elif first[0] == 'stopall':
            try:
                id = first[1]
                for task in await sync_to_async(list)(Tasks.objects.filter(global_task_id=id)):
                    await sync_to_async(task.delete)()
                await message.reply(f'Удалил все задачи с номером {first[1]}')
                logging.info(f"Удалены все задачи с global_task_id={id}")

            except Exception as e:
                logging.error(f"Ошибка при удалении задач: {e}")
                await message.reply('Неверный ID задачи')
        elif first[0].startswith('https'):
            try:
                if '/+' in first[0]:
                    link = first[0].split('/+')[1]
                    await client(ImportChatInviteRequest(link))
                    logging.info(f"Подписались на канал (invite link): {first[0]}")
                else:
                    await client(JoinChannelRequest(first[0]))
                    logging.info(f"Подписались на канал: {first[0]}")

            except Exception as e:
                logging.error(f"Не удалось подписаться на канал: {e}")
                await client.send_message(message.sender_id, 'Не удалось подписаться на канал')
    except Exception as e:
        logging.exception("Произошла ошибка в create_task:")


async def send_message_group(messages, task):
    """Отправляет группу сообщений в канал.
    """
    try:
        channel_id = int(messages.channel_id)
        for message_id in messages.messages_id.split(','):
            try:
                to_channel = int(task.to_channel)
                await client.forward_messages(to_channel, int(message_id), channel_id, drop_author=True)
                logging.info(f"Переслано сообщение {message_id} из канала {channel_id} в канал {to_channel}")

            except Exception as e:
                logging.error(f"Ошибка при пересылке сообщения {message_id} из канала {channel_id} в канал {task.to_channel}: {e}")
                pass
    except Exception as e:
        logging.exception("Произошла ошибка в send_message_group:")


async def create_or_ad_message(channel_id, message_id, grouped_id):
    """Создает или добавляет ID сообщения в существующую запись.
    """
    try:
        messages = await sync_to_async(list)(Messages.objects.filter(channel_id=channel_id, grouped_id=grouped_id))
        message = messages[0] if messages else None  # Исправлено для обработки пустого списка
        if message and grouped_id:
            message.messages_id += f',{message_id}'
            await sync_to_async(message.save)(update_fields=['messages_id'])
            logging.info(f"Добавлено сообщение {message_id} к существующей группе сообщений {grouped_id} в канале {channel_id}")
        else:
            message = await sync_to_async(Messages.objects.create)(channel_id=channel_id, grouped_id=grouped_id, messages_id=f'{message_id}')
            logging.info(f"Создана новая группа сообщений {grouped_id} с сообщением {message_id} в канале {channel_id}")
        return message
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
            if (task.start_date and timezone.now() < task.start_date) or (
                    task.end_date and timezone.now() >= task.end_date):
                task.is_active = False
                await sync_to_async(task.save)(update_fields=['is_active'])
                logging.info(f"Задача {task.id} деактивирована (start_date/end_date)")
            elif (task.start_date and timezone.now() >= task.start_date) or (
                    task.end_date and timezone.now() < task.end_date):
                task.is_active = True
                await sync_to_async(task.save)(update_fields=['is_active'])
                logging.info(f"Задача {task.id} активирована (start_date/end_date)")

            if task.is_active:
                if task.type == 'repost':
                    await client.forward_messages(int(task.to_channel), message_id, channel_id, drop_author=True)
                    logging.info(f"Переслано сообщение {message_id} из канала {channel_id} в канал {task.to_channel} (repost)")

                    await create_or_ad_message(channel_id=channel_id, message_id=message_id, grouped_id=grouped_id)
                elif task.type == 'randomrepost':
                    if random.randint(1, 100) <= task.chance:
                        await client.forward_messages(int(task.to_channel), message_id, channel_id, drop_author=True)
                        logging.info(
                            f"Переслано сообщение {message_id} из канала {channel_id} в канал {task.to_channel} (randomrepost, шанс {task.chance})")

                    await create_or_ad_message(channel_id=channel_id, message_id=message_id, grouped_id=grouped_id)
                elif task.type == 'previousrepost':
                    if not grouped_id or not await sync_to_async(list)(Messages.objects.filter(grouped_id=grouped_id)):
                        messages = await sync_to_async(list)(Messages.objects.filter(channel_id=channel_id, is_send=False))
                        if messages:  # Проверяем, есть ли сообщения в списке
                            message = messages[-1]
                            await send_message_group(message, task)
                            logging.info(f"Отправлена группа предыдущих сообщений в канал {task.to_channel} (previousrepost)")

                        else:
                            logging.warning("Нет предыдущих сообщений для отправки (previousrepost)")

                    await create_or_ad_message(channel_id=channel_id, message_id=message_id, grouped_id=grouped_id)

                elif task.type == 'repostminutes':
                    if not grouped_id or not await sync_to_async(list)(Messages.objects.filter(grouped_id=grouped_id)):
                        time = timezone.now() + datetime.timedelta(minutes=task.time)
                        need_mesage = await create_or_ad_message(channel_id=channel_id, message_id=message_id,
                                                                 grouped_id=grouped_id)
                        await sync_to_async(SendMessageTask.objects.create)(task=task, message=need_mesage, time=time)
                        logging.info(
                            f"Создана задача на отправку сообщения {message_id} через {task.time} минут в канал {task.to_channel} (repostminutes)")

                    await create_or_ad_message(channel_id=channel_id, message_id=message_id, grouped_id=grouped_id)
                elif task.type == 'randomrepostminutes':
                    if random.randint(1, 100) <= task.chance and (
                            not grouped_id or not await sync_to_async(list)(Messages.objects.filter(grouped_id=grouped_id))):
                        time = timezone.now() + datetime.timedelta(minutes=task.time)
                        need_mesage = await create_or_ad_message(channel_id=channel_id, message_id=message_id,
                                                                 grouped_id=grouped_id)
                        await sync_to_async(SendMessageTask.objects.create)(task=task, message=need_mesage, time=time)
                        logging.info(
                            f"Создана задача на отправку сообщения {message_id} через {task.time} минут с шансом {task.chance} в канал {task.to_channel} (randomrepostminutes)")

                    await create_or_ad_message(channel_id=channel_id, message_id=message_id, grouped_id=grouped_id)
                elif task.type == 'previousrepostrandomrepostminutes':
                    if random.randint(1, 100) <= task.chance:
                        if not grouped_id or not await sync_to_async(list)(Messages.objects.filter(grouped_id=grouped_id)):
                            messages = await sync_to_async(list)(Messages.objects.filter(channel_id=channel_id, is_send=False))
                            if messages:  # Проверяем, есть ли сообщения в списке
                                message = messages[-1]
                                time = timezone.now() + datetime.timedelta(minutes=task.time)
                                await sync_to_async(SendMessageTask.objects.create)(task=task, message=message, time=time)
                                logging.info(
                                    f"Создана задача на отправку предыдущего сообщения через {task.time} минут с шансом {task.chance} в канал {task.to_channel} (previousrepostrandomrepostminutes)")
                            else:
                                logging.warning("Нет предыдущих сообщений для отправки (previousrepostrandomrepostminutes)")

                    await create_or_ad_message(channel_id=channel_id, message_id=message_id, grouped_id=grouped_id)
    except Exception as e:
        logging.exception("Произошла ошибка в channel_check:")


@client.on(events.NewMessage())
async def mk(message):
    """Обрабатывает новые сообщения.
    """
    try:
        if message.is_channel and await sync_to_async(list)(Tasks.objects.filter(from_channel__icontains=message.message.peer_id.channel_id)):
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
                    await send_message_group(message.message, message.task)
                    logging.info(f"Отправлено сообщение {message.message.id} по расписанию в канал {message.task.to_channel}")
                    message.delete()
                    logging.info(f"Удалена задача SendMessageTask {message.id} после выполнения")

            await asyncio.sleep(60)  # Заменено time.sleep на asyncio.sleep
        except Exception as e:
            logging.exception("Произошла ошибка в send_time_message:")
        await asyncio.sleep(60)



async def main():
    """Главная функция для запуска клиента.
    """
    task = asyncio.create_task(send_time_message())
    try:
        await client.start(phone='+79187564306', password='19097007')
        await client.send_message('skat100500', '12344')
        logging.info("Клиент успешно запущен и подключен")
        await client.run_until_disconnected()
    except Exception as e:
        logging.critical(f"Ошибка в main: {e}")
    finally:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            logging.info("Задача send_time_message отменена")
            pass  # Игнорируем CancelledError, если задача была отменена


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
