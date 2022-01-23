import ptbot, os
from pytimeparse import parse

TG_TOKEN = os.getenv('TELEGRAM_TOKEN')

def render_progressbar(total, iteration, prefix='', suffix='', length=20, fill='█', zfill='░'):
    iteration = min(total, iteration)
    percent = "{0:.1f}"
    percent = percent.format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    pbar = fill * filled_length + zfill * (length - filled_length)
    return '{0} |{1}| {2}% {3}'.format(prefix, pbar, percent, suffix)

def countdown(time_to, chat_id, message_id, total_time):
    bot.update_message(chat_id, message_id, f'Осталось {time_to} секунд\n' + render_progressbar(total_time, total_time - time_to))

def finish(chat_id):
    bot.send_message(chat_id, 'Время вышло!')

def wait(chat_id, text):
    total_time = time_to = parse(text)
    message_id = bot.send_message(chat_id, 'Запускаю таймер...')
    bot.create_countdown(time_to, countdown, chat_id = chat_id, message_id = message_id,total_time = total_time)
    bot.create_timer(time_to, finish, chat_id = chat_id)


bot = ptbot.Bot(TG_TOKEN)
bot.reply_on_message(wait)
bot.run_bot()
