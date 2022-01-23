import logging
import telegram
import traceback
import sys

from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram.ext import Updater

logging.basicConfig()
logging.disable(30)  # disable warnings for beginners


class Bot():

    def __init__(self, api_key):
        if not api_key:
            raise(ValueError("Токен не указан"))
        self.api_key = api_key
        self.bot = telegram.Bot(token=api_key)
        self.logger = logging.getLogger('tbot')
        self.updater = Updater(self.api_key, use_context=True)
        self.job_queue = self.updater.job_queue
        self.dispatcher = self.updater.dispatcher
        self.logger.debug('Bot initialized')

    def send_message(self, chat_id, message):
        self.logger.debug(f'Message send: {message}')
        return self.bot.send_message(chat_id=chat_id, text=message).message_id

    def update_message(self, chat_id, message_id, new_message):
        self.logger.debug(f'Update message {message_id}: {new_message}')
        self.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=new_message)

    def create_timer(self, timeout_secs, callback, *args, **kwargs):
        if not callable(callback):
            raise TypeError('Ожидаем функцию на вход')
        if not timeout_secs:
            raise TypeError("Не могу запустить таймер на None секунд")
        if args:
            raise TypeError(f"create_timer() takes 2 positional arguments but {len(args) + 2} were given")

        def wrapper(context):
            callback(**kwargs)

        self.job_queue.run_once(wrapper, timeout_secs)

    def create_countdown(self, timeout_secs, callback, *args, **kwargs):
        if not callable(callback):
            raise TypeError('Ожидаем функцию на вход')
        if not timeout_secs:
            raise TypeError("Не могу запустить таймер на None секунд")
        if args:
            raise TypeError(f"create_countdown() takes 2 positional arguments but {len(args) + 2} were given")

        def wrapper(context):
            job = context.job
            job.context -= 1
            try:
                callback(job.context, **kwargs)
            except Exception as error:
                traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr, limit=-3)
                job.schedule_removal()
            if job.context <= 0:
                job.schedule_removal()

        first_callback = lambda context: callback(timeout_secs, **kwargs)
        self.job_queue.run_once(first_callback, 0)
        self.job_queue.run_repeating(wrapper, 1, context=timeout_secs)

    def reply_on_message(self, callback, *args, **kwargs):
        if not callable(callback):
            raise TypeError('Ожидаем функцию на вход')
        if args:
            raise TypeError(f"reply_on_message() takes 1 positional argument but {len(args) + 1} were given")

        def handle_text(update, context):
            users_reply = update.message.text
            chat_id = update.message.chat_id
            callback(chat_id, users_reply, **kwargs)

        self.dispatcher.add_handler(MessageHandler(Filters.text, handle_text))

    def run_bot(self):
        def error_handler(update, context):
            error = context.error
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr, limit=-3)

        self.dispatcher.add_error_handler(error_handler)
        self.updater.start_polling()
        self.updater.idle()