from django.core.management.base import BaseCommand
from bot.models import Profile, Message
from telegram import Bot
from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import Filters
from telegram.ext import MessageHandler, CommandHandler
from telegram.ext import Updater
from telegram.utils.request import Request
from django.conf import settings
from functools import wraps


# Decorator for error loggs
def log_errors(f):
    @wraps(f)
    def inner(*args, **kwargs):
        print("Error_check")
        try:
            return f(*args, **kwargs)
        except Exception as e:

            error_mesage = f'Error: {e}'
            print(error_mesage)
            raise e
    return inner


# Decorator that`s create profile if person isn`t logged
def prof_check(f):
    @wraps(f)
    def inner(*args, **kwargs):
        print("Prof_check")
        my_index = 0
        for item in args:
            if type(item) == Update:
                my_index = args.index(item)
        print(f"Stage_1 {my_index}")
        chat_id = args[my_index].message.chat_id
        if not args[my_index].message.from_user.username:
            chat_name = 'None'
        else:
            chat_name = args[my_index].message.from_user.username
        print(f"Stage_2 {chat_id}")
        Profile.objects.get_or_create(
            telegram_id=chat_id,
            defaults={
                'name': chat_name,
            }
        )
        print(f"Stage_3 {Profile.objects.last()}")
        return f(*args, **kwargs)
    return inner


@prof_check
@log_errors
def chose_place(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    reply_text = ''
    for item in Profile.objects.get_queryset():
        if item.telegram_id == chat_id:
            reply_text += f'{str(item)} - it is you\n'
        else:
            reply_text += f'{str(item)}'
    update.message.reply_text(text=reply_text)


@prof_check
@log_errors
def do_echo(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    text = update.message.text

    print("Echo")

    profile, _ = Profile.objects.get_or_create(
        telegram_id=chat_id,
        defaults={
            'name': update.message.from_user.username,
        }
    )

    m = Message(
        profile=profile,
        text=text,
    )
    m.save()

    reply_text = f'Profile ID: {chat_id}\nText: {text}\nMessage ID: {m.pk}'
    update.message.reply_text(text=reply_text)


class Command(BaseCommand):
    help = 'Telegram_Bot'

    def handle(self, *args, **options):
        request = Request(
            connect_timeout=0.5,
            read_timeout=1.0,
        )
        bot = Bot(
            request=request,
            token=settings.TOKEN,
            base_url=settings.PROXY_URL,
        )
        updater = Updater(
            bot=bot,
            use_context=True,
        )
        message_handler = MessageHandler(Filters.text, do_echo)
        updater.dispatcher.add_handler(message_handler)

        order_handler = CommandHandler('places', chose_place)
        updater.dispatcher.add_handler(order_handler)
        print(bot.get_me())

        # Continuous polling
        updater.start_polling()
        updater.idle()
