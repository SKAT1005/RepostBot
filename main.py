import telethon
from telethon import events
from telethon.tl.types import UpdateShortMessage

client = telethon.TelegramClient('User', api_id=26204346, api_hash='7d5e7f858870d425aa1b708d68aba39e', system_version="4.16.30-vxCUSTOM")



client.start(phone='+79027573093', password='1005')

async def create_task(message):
    command = message.text.split('"')
    main = command[0].split()
    type = main[0]
    if type == 'repost':
        pass
    elif type == 'randomrepost':
        channels = ','.join(main[1:])

    elif type == 'previousrepost':
        pass
    elif type == 'repostminutes':
        pass
    elif type == 'randomrepostminutes':
        pass
    elif type == 'previousrepostrandomrepostminutes':
        pass
    elif type == 'stopall':
        try:
            time = int(main[1])
        except Exception:
            await client.send_message(message.sender_id, 'Введите верный формат: stopall <Время в минутах числом>')



@client.on(events.NewMessage())
async def mk(message):
    if message.is_channel:
        print(message.id)
        print(type(message.grouped_id))
    elif message.is_private and message.sender_id in [595650100, 1288389919]:
        create_task(message)


client.run_until_disconnected()