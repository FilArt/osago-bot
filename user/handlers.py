from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ConversationHandler, CommandHandler, Filters, MessageHandler, CallbackQueryHandler

from conversation import Conversation, Information, Hello, Bye
from settings import ADMINS_IDS

INFO, PROCESS = list(map(str, range(200, 202)))
START_OVER = 'start_over'
END = ConversationHandler.END


def start(update, context):
    # logger.info('Пользователь %s начал диалог', update.effective_user['id'])
    buttons = [
        [InlineKeyboardButton(text='Заполнить заявку', callback_data=PROCESS)],
        [InlineKeyboardButton(text='Информация', callback_data=INFO)]
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    hello = Hello().read() or 'Привет!'

    if context.user_data.get(START_OVER) and update.callback_query:
        update.callback_query.edit_message_text(hello, reply_markup=keyboard)
    else:
        update.message.reply_text(hello, reply_markup=keyboard)
    context.user_data[START_OVER] = True
    return PROCESS


def info(update, context):
    buttons = [
        [InlineKeyboardButton(text='Заполнить заявку', callback_data=PROCESS)],
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    text = Information().read()
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)


def process(update: Update, context):
    if not context.user_data.get('processing') and update.callback_query and update.callback_query.data:
        context.user_data['processing'] = True

    if not context.user_data.get('processing'):
        return END
        # return start(update, context)

    conversation = Conversation()
    current_step = context.user_data.get('current_step', 0)
    context.user_data['current_step'] = current_step + 1
    current_question = conversation.get_question(current_step)

    if update.message:
        value = update.message.text
        previous_question = conversation.get_question(current_step - 1)
        if previous_question and value:
            context.user_data[previous_question] = value

    if current_step > 0:
        if current_step == len(conversation.questions):
            user = update.effective_user
            name = getattr(user, 'full_name', getattr(user, 'name')) or 'нет_имени'
            data = 'Поступила заявка от %s. (%s)\n' % (name, '@' + getattr(user, 'username'))
            for question in conversation.questions:
                question_text = question['text']
                data += '%s: %s\n' % (question_text, context.user_data[question_text])

            for admin_id in ADMINS_IDS:
                context.bot.send_message(admin_id, data)

            bye = Bye().read()
            update.message.reply_text(bye or 'С вами скоро свяжутся.')
            context.user_data.clear()
            return END

        update.message.reply_text(current_question)
        return PROCESS

    else:
        update.callback_query.edit_message_text(text=current_question)
        return PROCESS


def stop(update, context):
    update.message.reply_text('Пока.')
    return END


def get_handlers():
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            PROCESS: [
                MessageHandler(Filters.text, process),
                CallbackQueryHandler(process, pattern='^' + PROCESS + '$'),
            ],
        },
        fallbacks=[CommandHandler('stop', stop)],
    )
    info_handler = CallbackQueryHandler(info, pattern='^' + INFO + '$')

    return [conv_handler, info_handler]
