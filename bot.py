import logging
import os

from telegram.ext import Updater, ConversationHandler

from admin.handlers import get_handlers
from settings import TOKEN
from user.handlers import get_handlers as get_user_handlers

logging.basicConfig(format='%(message)s', level=logging.DEBUG)

logger = logging.getLogger(__name__)

INFO = 100


def info(update, context):
    msg = 'информация'
    update.message.reply_text(msg)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def cancel(update, context):
    update.message.reply_text('Заполнение заявки отменено.')
    return ConversationHandler.END


def main():
    updater = Updater(TOKEN, use_context=True)
    updater.start_webhook(listen="0.0.0.0", port=int(os.environ.get('PORT', '8443')), url_path=TOKEN)
    updater.bot.set_webhook("https://anketa-bot.herokuapp.com/" + TOKEN)

    dp = updater.dispatcher
    for handler in get_handlers() + get_user_handlers():
        dp.add_handler(handler)
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
