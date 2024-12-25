from tortoise import Tortoise
from database.models.models import Admins
from config.config import POSTGRES_URL

async def main():
    await Tortoise.init(
        db_url=POSTGRES_URL,
        modules={'models': ["database.models.models"]},
    )

    await Tortoise.generate_schemas()
    await Admins.get_or_create(telegram_id=1190679768, defaults={"login": 'Lionsky77'})

