from django.core.management.base import BaseCommand
from bot.models import Profile, Message, Store
from telegram import Bot
from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import Filters
from telegram.ext import MessageHandler, CommandHandler
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram.utils.request import Request
from django.conf import settings
from functools import wraps
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


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


@log_errors
def button(update: Update, context: CallbackContext):
    query = update.callback_query
    chat_id = update.callback_query.message.chat_id
    name = update.callback_query.message.chat.username

    profile, _ = Profile.objects.get_or_create(
        telegram_id=chat_id,
        defaults={
            'name': name,
        }
    )

    store = Store.objects.get(
        id=int(query.data),
    )

    m = Message(
        profile=profile,
        text='Зарезервировано',
        store=store,
    )
    m.save()

    query.edit_message_text(text="Selected option: {}".format(query.data))


@prof_check
@log_errors
def chose_place(update: Update, context: CallbackContext):
    keyboard = []
    reply_markup = InlineKeyboardMarkup(keyboard)
    #chat_id = update.message.chat_id
    reply_text = ''
    count_var = 1
    for item in Store.objects.get_queryset():
        reply_text += f'{count_var}. {str(item)}\n\n'
        keyboard.append([InlineKeyboardButton(f"{count_var}", callback_data=item.id)])
        count_var = count_var + 1

    update.message.reply_text(reply_text, reply_markup=reply_markup)
    #update.message.reply_text(text=reply_text)


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
        # message_handler = MessageHandler(Filters.text, do_echo)
        # updater.dispatcher.add_handler(message_handler)

        updater.dispatcher.add_handler(CommandHandler('place', chose_place))
        updater.dispatcher.add_handler(CallbackQueryHandler(button))

        print(bot.get_me())

        # Continuous polling
        updater.start_polling()
        updater.idle()
