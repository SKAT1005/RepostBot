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

client = telethon.TelegramClient('User', api_id=26204346, api_hash='7d5e7f858870d425aa1b708d68aba39e',
                                 system_version="4.16.30-vxCUSTOM")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RepostBot.settings')

django.setup()

from app.models import Tasks, Messages, SendMessageTask



async def create_task(message):
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
                # try:
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
                # except Exception as e:
                #     print(e)
                #     await client.send_message(message.sender_id,
                #                               f'Не получилось создать задачу, неверный формат ввода:\n {task}')
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
                except Exception:
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
                except Exception:
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
                except Exception:
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
                except Exception:
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
                except Exception:
                    await client.send_message(message.sender_id,
                                              f'Не получилось создать задачу, неверный формат ввода:\n {task}')
            else:
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
        except Exception:
            await message.reply('Задач пока нет')
    elif first[0] == 'stopall':
        try:
            id = first[1]
            for task in await sync_to_async(list)(Tasks.objects.filter(global_task_id=id)):
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
        except Exception:
            await client.send_message(message.sender_id, 'Не удалось подписаться на канал')

async def send_message_group(messages, task):
    channel_id = int(messages.channel_id)
    for message_id in messages.messages_id.split(','):
        try:
            to_channel = int(task.to_channel)
            await client.forward_messages(to_channel, int(message_id), channel_id, drop_author=True)
        except Exception as e:
            print(e)
            pass


async def create_or_ad_message(channel_id, message_id, grouped_id):
    messages = await sync_to_async(list)(Messages.objects.filter(channel_id=channel_id, grouped_id=grouped_id))
    message = messages[0]
    if message and grouped_id:
        message.messages_id += f',{message_id}'
        await sync_to_async(message.save)(update_fields=['messages_id'])
    else:
        message = await sync_to_async(Messages.objects.create)(channel_id=channel_id, grouped_id=grouped_id, messages_id=f'{message_id}')
    return message


async def channel_check(message):
    channel_id = message.message.peer_id.channel_id
    tasks = await sync_to_async(list)(Tasks.objects.filter(from_channel__icontains=channel_id))
    grouped_id = message.grouped_id
    message_id = message.id
    for task in tasks:

        if (task.start_date and timezone.now() < task.start_date) or (
                task.end_date and timezone.now() >= task.end_date):
            tasks.is_active = False
            await sync_to_async(task.save)(update_fields=['is_active'])
        elif (task.start_date and timezone.now() >= task.start_date) or (
                task.end_date and timezone.now() < task.end_date):
            tasks.is_active = True
            await sync_to_async(task.save)(update_fields=['is_active'])

        if task.is_active:
            if task.type == 'repost':
                await client.forward_messages(int(task.to_channel), message_id, channel_id, drop_author=True)
                await create_or_ad_message(channel_id=channel_id, message_id=message_id, grouped_id=grouped_id)
            elif task.type == 'randomrepost':
                if random.randint(1, 100) <= task.chance:
                    await client.forward_messages(int(task.to_channel), message_id, channel_id, drop_author=True)
                await create_or_ad_message(channel_id=channel_id, message_id=message_id, grouped_id=grouped_id)
            elif task.type == 'previousrepost':
                if not grouped_id or not await sync_to_async(list)(Messages.objects.filter(grouped_id=grouped_id)):
                    messages = await sync_to_async(list)(Messages.objects.filter(channel_id=channel_id, is_send=False))
                    message = messages[-1]
                    await send_message_group(message, task)
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
                        not grouped_id or not await sync_to_async(list)(Messages.objects.filter(grouped_id=grouped_id))):
                    time = timezone.now() + datetime.timedelta(minutes=task.time)
                    need_mesage = await create_or_ad_message(channel_id=channel_id, message_id=message_id,
                                                             grouped_id=grouped_id)
                    await sync_to_async(SendMessageTask.objects.create)(task=task, message=need_mesage, time=time)
                await create_or_ad_message(channel_id=channel_id, message_id=message_id, grouped_id=grouped_id)
            elif task.type == 'previousrepostrandomrepostminutes':
                if random.randint(1, 100) <= task.chance:
                    if not grouped_id or not await sync_to_async(list)(Messages.objects.filter(grouped_id=grouped_id)):
                        messages = await sync_to_async(list)(Messages.objects.filter(channel_id=channel_id, is_send=False))
                        message = messages[-1]
                        time = timezone.now() + datetime.timedelta(minutes=task.time)
                        await sync_to_async(SendMessageTask.objects.create)(task=task, message=message, time=time)
                await create_or_ad_message(channel_id=channel_id, message_id=message_id, grouped_id=grouped_id)


@client.on(events.NewMessage())
async def mk(message):
    if message.is_channel and await sync_to_async(list)(Tasks.objects.filter(from_channel__icontains=message.message.peer_id.channel_id)):
        await channel_check(message)
    elif message.is_private and message.sender_id in [595650100, 1288389919, 8175762996]:
        # try:
            await create_task(message)
        # except Exception:
        #     await client.send_message(1288389919, 'Неизвестная команда')


async def send_time_message():
    while True:
        for message in await sync_to_async(SendMessageTask.objects.all)():
            if message.time <= timezone.now():
                await send_message_group(message, message.task)
                message.delete()
        time.sleep(60)




async def main():
    task = asyncio.create_task(send_time_message())
    await client.start(phone='+79027573093', password='1005')
    try:
        await client.run_until_disconnected()
    finally:
        task.cancel() # Гарантируем остановку send_time_message при отключении
        await task

if __name__ == '__main__':
    asyncio.run(main())
