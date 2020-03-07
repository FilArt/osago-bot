import logging

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
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # dp.add_handler(CommandHandler('info', info))
    # dp.add_handler(MessageHandler(Filters.regex('^Информация$'), info))
    # dp.add_handler(CommandHandler('cancel', cancel))
    # dp.add_handler(MessageHandler(Filters.regex('^Отмена$'), cancel))

    for handler in get_handlers() + get_user_handlers():
        dp.add_handler(handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
