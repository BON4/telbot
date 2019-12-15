from django.db import models
#from django.contrib.gis.db import models as gis_models


class Profile(models.Model):
    telegram_id = models.PositiveIntegerField(unique=True, verbose_name="ID пользователя")

    name = models.CharField(verbose_name='Имя пользователя', max_length=200)

    def __str__(self):
        return f'#{self.telegram_id}_{self.name}'

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"


class Message(models.Model):
    profile = models.ForeignKey(to='bot.Profile', verbose_name='Профиль', on_delete=models.CASCADE)

    text = models.TextField(verbose_name='Текст', max_length=500)

    date_of_creation = models.DateTimeField(verbose_name='Время получения', auto_now_add=True)

    def __str__(self):
        return f'Сообщение {self.pk} от {self.profile.name}'

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = "Сообщения"
