from tortoise import models, fields

class User(models.Model):
    id = fields.IntField(pk=True)
    balance = fields.FloatField(default=0.0)
    telegram_id = fields.BigIntField(unique=True)

    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = 'users'

class LogFilms(models.Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=64)
    file_ids = fields.CharField(max_length=512)
    quality = fields.CharField(max_length=32)
    downloaded_by = fields.BigIntField()
    downloaded_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = 'films_logs'

class Admins(models.Model):
    id = fields.IntField(pk=True)
    telegram_id = fields.BigIntField(unique=True)
    login = fields.CharField(max_length=32, default='')
    hash_password = fields.CharField(max_length=1024, default='')

    class Meta:
        table = 'admins'


