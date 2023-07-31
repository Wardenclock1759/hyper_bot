from telegram import Update, Bot, BotCommand, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, Filters, ConversationHandler, CallbackQueryHandler
from keras import models
from dotenv import load_dotenv
import os

AGE, GENDER, CHEST_PAIN, THRESTBPS, CHOL, FBS, THALACH, EXANG, OLDPEAK, SLOPE, THAL, PREDICT = range(12)

def handle_unknown(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Прогноз", callback_data='/predict')],
        [InlineKeyboardButton("Справка", callback_data='/about')],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        "К сожалению, мне не удалось найти информацию по вашему запросу"
    )

    update.message.reply_text(
        "Чем я могу Вам помочь?",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Прогноз", callback_data='/predict')],
        [InlineKeyboardButton("Справка", callback_data='/about')],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        "Вас приветствует *Health Check Bot!*\n\n"
        "С моей помощью Вы сможете получить прогноз риска возникновения сердечно-сосудистых заболеваний.\n\n"
        "Для дальнейшей работы с ботом воспользуйтесь одной из команд:\n\n"
        "*/predict* - Получить оценку риска возникновения сердечно-сосудистых заболеваний\n"
        "*/about* - Получить справочную информацию",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

def about(update: Update, context: CallbackContext) -> None:
    message = None
    if update.message is not None:
        message = update.message
    elif update.callback_query is not None:
        message = update.callback_query.message

    if message is not None:
        message.reply_text(
            "Вас приветствует *Health Check Bot!*\n\n"
            "С моей помощью Вы сможете получить прогноз риска возникновения "
            "сердечно-сосудистых заболеваний по введенным данным.\n\n"
            "*Справка по командам:*\n\n"
            "*/predict* - Получить оценку риска возникновения сердечно-сосудистых заболеваний\n"
            "*/about* - Получить справочную информацию",
            parse_mode='Markdown'
        )
        message.reply_text(
            "Я выдаю прогноз по шкале от 0 до 1.\n\n"
            "Интерпретация результатов риска:\n"
            "0.0-0.1 - очень низкий\n"
            "0.1-0.3 - низкий\n"
            "0.3-0.6 - средний\n"
            "0.6-1 - высокий\n\n"
            "При получении любого результата рекомендую не пренебрегать посещением врача. Не болейте!",
            parse_mode='Markdown'
        )

def get_age(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    if query is not None:
        query.answer()
        query.message.reply_text("Для прогнозирования риска возникновения сердечно-сосудистых заболеваний мне необходимо собрать данные о Вашем состоянии здоровья.")
        query.message.reply_text("Введите свой возраст цифрами:")
    else:
        update.message.reply_text("Для прогнозирования риска возникновения сердечно-сосудистых заболеваний мне необходимо собрать данные о Вашем состоянии здоровья.")
        update.message.reply_text("Введите свой возраст цифрами:")
    return AGE

def get_gender(update: Update, context: CallbackContext) -> int:
    keyboard = [
        [InlineKeyboardButton("Мужчина", callback_data=1)],
        [InlineKeyboardButton("Женщина", callback_data=0)],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Выберите пол:", reply_markup=reply_markup)
    return GENDER

def get_chest_pain(update: Update, context: CallbackContext) -> int:
    keyboard = [
        [InlineKeyboardButton("Асимптоматическая", callback_data=1)],
        [InlineKeyboardButton("Типичная стенокардия", callback_data=2)],
        [InlineKeyboardButton("Нестенокардическая боль", callback_data=3)],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Выберите тип боли в груди:", reply_markup=reply_markup)
    return CHEST_PAIN

def get_threstbps(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Введите артериальное давление в состояние покоя в мм рт. ст. Пример: 120")
    return THRESTBPS

def get_chol(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Введите уровень холестерина в сыворотке в мг/дл:")
    return CHOL

def get_fbs(update: Update, context: CallbackContext) -> int:
    keyboard = [
        [InlineKeyboardButton("Да", callback_data=1)],
        [InlineKeyboardButton("Нет", callback_data=0)],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Уровень сахара в крови натощак больше 120 мг/дл?", reply_markup=reply_markup)
    return FBS

def get_thalach(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Введите, какую максимальную достигнутую частоту сердечных сокращений Вы зафиксировали:")
    return THALACH

def get_exang(update: Update, context: CallbackContext) -> int:
    keyboard = [
        [InlineKeyboardButton("Да", callback_data=1)],
        [InlineKeyboardButton("Нет", callback_data=0)],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Зафиксирована ли при физической нагрузке стенокардия?", reply_markup=reply_markup)
    return EXANG

def get_oldpeak(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Введите значение депрессии сегмента ST, вызванной физической нагрузкой по сравнению с покоем:")
    return OLDPEAK

def get_slope(update: Update, context: CallbackContext) -> int:
    keyboard = [
        [InlineKeyboardButton("Восходящий", callback_data=0)],
        [InlineKeyboardButton("Плоский", callback_data=1)],
        [InlineKeyboardButton("Нисходящий", callback_data=2)],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Укажите наклон пика сегмента ST при пиковой физической нагрузке:", reply_markup=reply_markup)
    return SLOPE

def get_thal(update: Update, context: CallbackContext) -> int:
    keyboard = [
        [InlineKeyboardButton("Отклонений не выявлено", callback_data=0)],
        [InlineKeyboardButton("Нормальный", callback_data=1)],
        [InlineKeyboardButton("Фиксированный дефект", callback_data=2)],
        [InlineKeyboardButton("Обратимый дефект", callback_data=3)],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Укажите результат исследования таламической гиперактивности", reply_markup=reply_markup)
    return THAL

def predict(update: Update, context: CallbackContext) -> int:
    age = context.user_data.get('age')
    gender = context.user_data.get('gender')
    chest_pain = context.user_data.get('chest_pain')
    threstbps = context.user_data.get('threstbps')
    chol = context.user_data.get('chol')
    fbs = context.user_data.get('fbs')
    thalach = context.user_data.get('thalach')
    exang = context.user_data.get('exang')
    oldpeak = context.user_data.get('oldpeak')
    slope = context.user_data.get('slope')
    thal = context.user_data.get('thal')
    if age is None or gender is None or chest_pain is None or threstbps is None or chol is None or fbs is None or thalach is None or exang is None or oldpeak is None or slope is None or thal is None:
        return get_age(update, context)
    model = models.load_model('hypertension_classifier_neural_network.h5')
    data_pred = [[age, int(gender), int(chest_pain), threstbps, chol, int(fbs), thalach, int(exang), oldpeak, int(slope), int(thal)]]
    prediction = model.predict(data_pred)

    res = format_res(prediction)
    update.message.reply_text(
        "*Результаты готовы!*\n\n"
        f"Мой прогноз риска возникновения сердечно-сосудистых заболеваний по введенным данным - {float(prediction[0]).__round__(2)}.\n"
        f"Данный показатель относится к {res} степени риска\n"
        "За более подробным заключением рекомендую обратиться к врачу. Не болейте!\n",
        parse_mode='Markdown'
    )

    return ConversationHandler.END

def handle_age(update: Update, context: CallbackContext) -> int:
    user_input = update.message.text
    try:
        user_age = int(user_input)
        if 10 <= user_age <= 80:
            context.user_data['age'] = user_age
            return get_gender(update, context)
        raise ValueError
    except ValueError:
        update.message.reply_text("Неверный формат данных, введите число")
        return AGE
    
def handle_gender(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    user_input = query.data
    context.user_data['gender'] = user_input
    return get_chest_pain(query, context)

def handle_gender_incorrect_input(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Неверный формат данных, нажмите одну из кнопок выше")
    return GENDER

def handle_chest_pain(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    user_input = query.data
    context.user_data['chest_pain'] = user_input
    return get_threstbps(query, context)

def handle_threstbps(update: Update, context: CallbackContext) -> int:
    user_input = update.message.text
    try:
        user_threstbps = int(user_input)
        if 0 <= user_threstbps <= 300:
            context.user_data['threstbps'] = user_threstbps
            return get_chol(update, context)
        raise ValueError
    except ValueError:
        update.message.reply_text("Неверный формат данных, введите число")
        return THRESTBPS

def handle_chol(update: Update, context: CallbackContext) -> int:
    user_input = update.message.text
    try:
        user_chol = int(user_input)
        if 0 <= user_chol <= 300:
            context.user_data['chol'] = user_chol
            return get_fbs(update, context)
        raise ValueError
    except ValueError:
        update.message.reply_text("Неверный формат данных, введите число")
        return CHOL
    
def handle_fbs(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    user_input = query.data
    context.user_data['fbs'] = user_input
    return get_thalach(query, context)

def handle_fbs_incorrect_input(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Неверный формат данных, нажмите одну из кнопок выше")
    return FBS

def handle_pain_incorrect_input(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Неверный формат данных, нажмите одну из кнопок выше")
    return CHEST_PAIN

def handle_thalach(update: Update, context: CallbackContext) -> int:
    user_input = update.message.text
    try:
        user_thalach = int(user_input)
        if 50 <= user_thalach <= 250:
            context.user_data['thalach'] = user_thalach
            return get_exang(update, context)
        raise ValueError
    except ValueError:
        update.message.reply_text("Неверный формат данных, введите число от 50 до 250")
        return THALACH

def handle_exang(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    user_input = query.data
    context.user_data['exang'] = user_input
    return get_oldpeak(query, context)

def handle_exang_incorrect_input(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Неверный формат данных, нажмите одну из кнопок выше")
    return EXANG

def handle_oldpeak(update: Update, context: CallbackContext) -> int:
    user_input = update.message.text
    try:
        user_oldpeak = float(user_input)
        if 0 <= user_oldpeak <= 100:
            context.user_data['oldpeak'] = user_oldpeak
            return get_slope(update, context)
        raise ValueError
    except ValueError:
        update.message.reply_text("Неверный формат данных, введите число от 0 до 100")
        return OLDPEAK
    
def handle_slope(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    user_input = query.data
    context.user_data['slope'] = user_input
    return get_thal(query, context)

def handle_slope_incorrect_input(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Неверный формат данных, нажмите одну из кнопок выше")
    return SLOPE

def handle_thal(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    user_input = query.data
    context.user_data['thal'] = user_input
    return predict(query, context)

def handle_thal_incorrect_input(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Неверный формат данных, нажмите одну из кнопок выше")
    return THAL

def format_res(res):
    res = res[0]
    if 0 <= res < 0.1:
        return "очень низкий"
    elif 0.1 <= res < 0.3:
        return "низкий"
    elif 0.3 <= res < 0.6:
        return "средний"
    elif 0.6 <= res <= 1:
        return "высокий"
    else:
        return "неопределено"
    
def callback_query_handler(update, context):
    cqd = update.callback_query.data
    if cqd == '/about':
        about(update, context)
    if cqd == '/predict':
        return get_age(update, context)

def main() -> None:
    load_dotenv()
    chat_id = os.getenv('CHAT_ID')
    if chat_id is None:
        raise ValueError("CHAT_ID not found in .env file")

    bot = Bot(chat_id)
    updater = Updater(bot=bot, use_context=True)

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('predict', get_age),CallbackQueryHandler(callback_query_handler)],
        states={
            AGE: [MessageHandler(Filters.text & ~Filters.command, handle_age)],
            GENDER: [CallbackQueryHandler(handle_gender), MessageHandler(Filters.text & ~Filters.command, handle_gender_incorrect_input)],
            CHEST_PAIN: [CallbackQueryHandler(handle_chest_pain), MessageHandler(Filters.text & ~Filters.command, handle_pain_incorrect_input)],
            THRESTBPS: [MessageHandler(Filters.text & ~Filters.command, handle_threstbps)],
            CHOL: [MessageHandler(Filters.text & ~Filters.command, handle_chol)],
            FBS: [CallbackQueryHandler(handle_fbs), MessageHandler(Filters.text & ~Filters.command, handle_fbs_incorrect_input)],
            THALACH : [MessageHandler(Filters.text & ~Filters.command, handle_thalach)],
            EXANG: [CallbackQueryHandler(handle_exang), MessageHandler(Filters.text & ~Filters.command, handle_exang_incorrect_input)],
            OLDPEAK: [MessageHandler(Filters.text & ~Filters.command, handle_oldpeak)],
            SLOPE: [CallbackQueryHandler(handle_slope), MessageHandler(Filters.text & ~Filters.command, handle_slope_incorrect_input)],
            THAL: [CallbackQueryHandler(handle_thal), MessageHandler(Filters.text & ~Filters.command, handle_thal_incorrect_input)],
            PREDICT: [MessageHandler(Filters.text & ~Filters.command, predict)]
        },
        fallbacks=[],
    )

    updater.dispatcher.add_handler(conversation_handler)
    updater.dispatcher.add_handler(CommandHandler('about', about))
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CallbackQueryHandler(callback_query_handler))
    updater.dispatcher.add_handler(MessageHandler(Filters.all, handle_unknown))

    bot.set_my_commands([
        BotCommand("start", "Приветственное сообщение"),
        BotCommand("predict", "Получить прогноз"),
        BotCommand("about", "Получить справку по боту"),
    ])

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()