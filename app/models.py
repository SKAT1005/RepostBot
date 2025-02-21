from django.db import models

class GlobalNumber(models.Model):
    description = models.TextField(blank=True, null=True, verbose_name='Описание задачи')
    start_date = models.DateTimeField(blank=True, null=True, verbose_name='Дата начала парсинга')
    end_date = models.DateTimeField(blank=True, null=True, verbose_name='Дата конца парсинга')

    def start_date_str(self):
        months = [
            "января", "февраля", "марта", "апреля", "мая", "июня",
            "июля", "августа", "сентября", "октября", "ноября", "декабря"
        ]
        dt = self.start_date
        if dt:
            day = dt.day
            month = months[dt.month - 1]  # Индексы в списке начинаются с 0
            hour = dt.hour
            minute = dt.minute
            return f"{day} {month} {hour:02}:{minute:02}"
        return ''
    def end_date_str(self):
        months = [
            "января", "февраля", "марта", "апреля", "мая", "июня",
            "июля", "августа", "сентября", "октября", "ноября", "декабря"
        ]
        dt = self.end_date
        if dt:
            day = dt.day
            month = months[dt.month - 1]  # Индексы в списке начинаются с 0
            hour = dt.hour
            minute = dt.minute
            return f"{day} {month} {hour:02}:{minute:02}"
        return ''


class Tasks(models.Model):
    global_task_id = models.ForeignKey('GlobalNumber', on_delete=models.CASCADE, related_name='tasks', verbose_name='Id блока задачи')
    type = models.CharField(max_length=128, verbose_name='Тип пересылки')
    to_channel = models.TextField(verbose_name='В какой канал пересылка')
    from_channel = models.CharField(max_length=128, verbose_name='Из каких каналов пересылаем')
    time = models.IntegerField(default=0, verbose_name='Количество минут перед отправкой')
    chance = models.IntegerField(default=100, verbose_name='Шанс отправки сообщения')
    is_active = models.BooleanField(default=True, verbose_name='Активен ли запрос')
    is_pause = models.BooleanField(default=False, verbose_name='Стоит ли задача на паузе?')


    def task_str(self):
        if not self.is_pause:
            status = '🟢'
        else:
            status = '🔴'
        return f'{status} {self.id}) {self.from_channel} → {self.to_channel}'


class Messages(models.Model):
    channel_id = models.CharField(max_length=128, verbose_name='Канал сообщения'
                                  )
    grouped_id = models.IntegerField(blank=True, null=True, verbose_name='Общий список')
    messages_id = models.TextField(verbose_name='ID сообщений')
    is_send = models.BooleanField(default=False, verbose_name='Отправлено ли сообщение?')

class SendMessageTask(models.Model):
    message = models.ForeignKey('Messages', on_delete=models.CASCADE, related_name='messages_task', verbose_name='Сообщение для отправк')
    task = models.ForeignKey('Tasks', on_delete=models.CASCADE, related_name='send_messages_task', verbose_name='Задача для отправки')
    time = models.DateTimeField(verbose_name='Дата отправки')
