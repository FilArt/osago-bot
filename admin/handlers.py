from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CommandHandler, ConversationHandler, CallbackQueryHandler, MessageHandler, Filters

from conversation import Conversation, Information, Bye, Hello
from settings import ADMINS_IDS

SELECTING_ACTION, ADDING_QUESTION, CHANGING_QUESTION, DETAIL_QUESTION, CH_INFO = map(chr, range(5))
CH_HELLO, CH_BYE = 'ch_hello', 'ch_bye'
FINISH_CH_HELLO, FINISH_CH_BYE = 'f_ch_hello', 'f_cj_bye'
FINISH_ADD, FINISH_CHANGE, FINISH_REMOVE, FINISH_CH_INFO = map(chr, range(90, 94))
RESOLVE = 2000

REMOVING_QUESTION = 5000
NO_REMOVING_QUESTION = 2001
SHOWING = 'showing'
END = ConversationHandler.END
START_OVER = 'start_over'
CURRENT_ACTION = 'current_action'
TRUNCATE_CHARS = 25


def _truncate(some: str) -> str:
    if len(some) > TRUNCATE_CHARS:
        some = some[:TRUNCATE_CHARS - 3] + '...'
    return some


def _return(update, text='Сохранено.'):
    button = InlineKeyboardButton(text='Вернуться', callback_data=SHOWING)
    keyboard = InlineKeyboardMarkup.from_button(button)
    if update.message:
        update.message.reply_text(text=text, reply_markup=keyboard)
    else:
        update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    return SHOWING


def start(update, context):
    if update.effective_user.id not in ADMINS_IDS:
        return

    text = 'Админка. Для отмены, нажмите "готово".'
    buttons = []
    for i, question in enumerate(Conversation().questions):
        q_text = _truncate(question['text'])
        buttons.append([
            InlineKeyboardButton(text=q_text, callback_data=f'{DETAIL_QUESTION}_{i}'),
            InlineKeyboardButton(text='📝', callback_data=f'{CHANGING_QUESTION}_{i}'),
            InlineKeyboardButton(text='🗑️', callback_data=f'{REMOVING_QUESTION}_{i}'),
        ])
    buttons.extend([
        [InlineKeyboardButton(text='Добавить вопрос', callback_data=str(ADDING_QUESTION))],
        [InlineKeyboardButton(text='Изменить информацию', callback_data=str(CH_INFO))],
        [InlineKeyboardButton(text='Изменить приветствие', callback_data=str(CH_HELLO))],
        [InlineKeyboardButton(text='Изменить прощание', callback_data=str(CH_BYE))],
        [InlineKeyboardButton(text='Готово', callback_data=str(END))]
    ])
    keyboard = InlineKeyboardMarkup(buttons)

    if update.callback_query:
        update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    else:
        update.message.reply_text(text=text, reply_markup=keyboard)

    context.user_data[START_OVER] = True
    return SELECTING_ACTION


def change_information(update, context):
    context.user_data[CURRENT_ACTION] = CH_INFO
    text = 'Старая информация: \n%s\nВведите новую информацию:' % Information().read()
    buttons = [[
        InlineKeyboardButton(text='Вернуться', callback_data=SHOWING),
    ]]
    keyboard = InlineKeyboardMarkup(buttons)
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    return RESOLVE


def finish_change_information(update, context):
    new_text = update.message.text
    try:
        Information().write(new_text)
    except ValueError as e:
        update.message.reply_text(text="Произошла ошибка: %s" % str(e))

    return _return(update)


def change_bye(update, context):
    context.user_data[CURRENT_ACTION] = CH_BYE
    text = 'Старое прощание: \n%s\nВведите новое:' % Bye().read()
    buttons = [[
        InlineKeyboardButton(text='Вернуться', callback_data=SHOWING),
    ]]
    keyboard = InlineKeyboardMarkup(buttons)
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    return RESOLVE


def finish_change_bye(update, context):
    new_text = update.message.text
    try:
        Bye().write(new_text)
    except ValueError as e:
        update.message.reply_text(text="Произошла ошибка: %s" % str(e))

    return _return(update)


def change_hello(update, context):
    context.user_data[CURRENT_ACTION] = CH_HELLO
    text = 'Старое приветствие: \n%s\nВведите новое:' % Hello().read()
    buttons = [[
        InlineKeyboardButton(text='Вернуться', callback_data=SHOWING),
    ]]
    keyboard = InlineKeyboardMarkup(buttons)
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    return RESOLVE


def finish_change_hello(update, context):
    new_text = update.message.text
    try:
        Hello().write(new_text)
    except ValueError as e:
        update.message.reply_text(text="Произошла ошибка: %s" % str(e))

    return _return(update)


def add_question(update, context):
    context.user_data[CURRENT_ACTION] = ADDING_QUESTION
    text = 'Введите текст нового вопроса:'
    buttons = [[
        InlineKeyboardButton(text='Вернуться', callback_data=SHOWING),
    ]]
    keyboard = InlineKeyboardMarkup(buttons)
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    return RESOLVE


def finish_add_question(update, context):
    text = update.message.text
    try:
        Conversation().add_question(text)
    except ValueError as e:
        update.message.reply_text(str(text))

    return _return(update)


def remove_question(update, context):
    context.user_data[CURRENT_ACTION] = REMOVING_QUESTION
    data = update.callback_query.data
    question_id = int(data.split('_')[1])
    text = 'Удалить вопрос "%s"?' % Conversation().get_question(question_id)
    context.user_data[REMOVING_QUESTION] = question_id
    buttons = [[
        InlineKeyboardButton(text='Подтвердить', callback_data='remove0'),
        InlineKeyboardButton(text='Вернуться', callback_data='remove1'),
    ]]
    keyboard = InlineKeyboardMarkup(buttons)
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    return REMOVING_QUESTION


def finish_remove_question(update, context):
    if update.callback_query.data.endswith('1'):
        return start(update, context)

    question_id = context.user_data.pop(REMOVING_QUESTION)
    try:
        Conversation().remove_question(question_id)
    except ValueError as e:
        update.message.reply_text(text="Произошла ошибка: %s" % str(e))

    return _return(update)


def change_question(update, context):
    context.user_data[CURRENT_ACTION] = CHANGING_QUESTION

    old_question_id = update.callback_query.data.split('_')[1]
    context.user_data[CHANGING_QUESTION] = old_question_id

    text = 'Введите текст вопроса:'
    buttons = [[
        InlineKeyboardButton(text='Вернуться', callback_data=SHOWING),
    ]]
    keyboard = InlineKeyboardMarkup(buttons)
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    return RESOLVE


def finish_change_question(update, context):
    old_text_id = context.user_data.pop(CHANGING_QUESTION)
    new_text = update.message.text
    try:
        Conversation().change_question(int(old_text_id), new_text)
    except ValueError as e:
        update.message.reply_text(text="Произошла ошибка: %s" % str(e))

    return _return(update)


def resolve(update, context):
    if update.callback_query and update.callback_query.data == SHOWING:
        return start(update, context)

    current_action = context.user_data[CURRENT_ACTION]
    if current_action == ADDING_QUESTION:
        f = finish_add_question
    elif current_action == CH_INFO:
        f = finish_change_information
    elif current_action == CH_HELLO:
        f = finish_change_hello
    elif current_action == CH_BYE:
        f = finish_change_bye
    elif current_action == CHANGING_QUESTION:
        f = finish_change_question
    elif current_action == REMOVING_QUESTION:
        f = remove_question

    else:
        raise Exception("INTERNAL")
    return f(update, context)


def detail_question(update, context):
    q_id = int(update.callback_query.data.split('_')[1])
    full_question = Conversation().get_question(q_id)
    return _return(update, text=full_question)


def stop(update, context):
    update.message.reply_text('Пока.')
    return END


def end(update, context):
    text = 'Пока.'
    update.callback_query.edit_message_text(text=text)
    return END


def _get_pattern(some, some2=''):
    return f'^{some}{some2}$'


def get_handlers():
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('admin', start)],

        states={
            SHOWING: [CallbackQueryHandler(start, pattern=_get_pattern(SHOWING))],
            RESOLVE: [CallbackQueryHandler(resolve, pattern=_get_pattern(SHOWING)),
                      MessageHandler(Filters.text, resolve)],
            SELECTING_ACTION: [
                CallbackQueryHandler(start, pattern=_get_pattern(SHOWING)),
                CallbackQueryHandler(change_information, pattern=_get_pattern(CH_INFO)),
                CallbackQueryHandler(change_bye, pattern=_get_pattern(CH_BYE)),
                CallbackQueryHandler(change_hello, pattern=_get_pattern(CH_HELLO)),
                CallbackQueryHandler(add_question, pattern=_get_pattern(ADDING_QUESTION)),
                CallbackQueryHandler(remove_question, pattern=_get_pattern(REMOVING_QUESTION, '.+')),
                CallbackQueryHandler(change_question, pattern=_get_pattern(CHANGING_QUESTION, '.+')),
                CallbackQueryHandler(end, pattern=_get_pattern(END)),
                CallbackQueryHandler(detail_question, pattern=_get_pattern(DETAIL_QUESTION, '.+')),
            ],
            REMOVING_QUESTION: [
                CallbackQueryHandler(finish_remove_question, pattern='^remove.$'),
            ],
            FINISH_CH_INFO: [MessageHandler(Filters.text, finish_change_information)],
            FINISH_CH_HELLO: [MessageHandler(Filters.text, finish_change_hello)],
            FINISH_CH_BYE: [MessageHandler(Filters.text, finish_change_bye)],
            FINISH_CHANGE: [MessageHandler(Filters.text, finish_change_question)],
            FINISH_ADD: [MessageHandler(Filters.text, finish_add_question)],
        },
        fallbacks=[CommandHandler('stop', stop)],
    )
    return [conv_handler]
