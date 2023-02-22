import io
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaDocument
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)
from model import add_contact, find_phone_number, delete_contact


menu_items = ["Показать все контакты",
              "Создать новый контакт",
              "Найти телефон по имени",
              "Удалить контакт",
              "Импорт из файла JSON или CSV",
              "Экспорт в файл JSON или CSV",
              "Выйти"]

export_menu_items = ["JSON", "CSV"]

(MENU, VIEW,
 ADD_PARSE_PHONE, ADD_PARSE_NAME,
 SEARCH_PARSE_NAME,
 DELETE_PARSE_NAME, DELETE_PARSE_CONFIRMATION,
 IMPORT_READ_FILE, EXPORT_SELECT_FORMAT, CLOSE) = range(10)

phonebook_dict = {}


async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [[InlineKeyboardButton(item, callback_data=item)]
                for item in menu_items]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Вас приветствует телефонная книга.\n"
                                    "Пожалуйста, выберете одну из следующих опций:",
                                    reply_markup=reply_markup)
    return MENU


async def view(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    contact_list = ""
    for k, v in phonebook_dict.items():
        contact_list += (k + " ----> " + v + "\n")
    if contact_list != "":
        await update.callback_query.edit_message_text(contact_list)
    else:
        await update.callback_query.edit_message_text("Телефонная книга пуста!")
    return MENU


async def add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()  # Ожидаем пока текст с кнопки обработается
    await update.callback_query.edit_message_text("Введите имя контакта:")
    return ADD_PARSE_NAME


async def parse_contact_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    contact_name = update.message.text
    context.user_data['contact_name'] = contact_name
    await update.message.reply_text("Введите номер контакта:")
    return ADD_PARSE_PHONE


async def parse_contact_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    phone_number = update.message.text
    if context.user_data.get('contact_name'):
        contact_name = context.user_data['contact_name']
        add_contact(phonebook_dict, phone_number, contact_name)
        await update.message.reply_text("Контакт успешно сохранен.")
    else:
        await update.message.reply_text("Ошибка при создании контакта!")
    del context.user_data['contact_name']
    return MENU


async def search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("Введите имя контакта для поиска:")
    return SEARCH_PARSE_NAME


async def parse_name_as_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    contact_name = update.message.text
    phone_number = find_phone_number(contact_name, phonebook_dict)
    if phone_number != "":
        await update.message.reply_text("Найден номер: " + phone_number)
    else:
        await update.message.reply_text("""Этого контакта в книге нет.
                                           Вернитесь в меню, чтобы добавить контакт.""")
    return MENU


# обработчик нажатия на кнопку "Удалить контакт"
async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("Введите имя контакта для удаления:")
    return DELETE_PARSE_NAME


# обработчик введенного текста на запрос "Введите имя контакта для удаления:"
async def parse_name_to_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    contact_name = update.message.text  # парсим присланный пользователем текст
    phone_number = find_phone_number(contact_name, phonebook_dict)
    if phone_number != "":
        context.user_data['contact_name_to_delete'] = contact_name
        await update.message.reply_text("Введите 'да', чтобы удалить контакт [" + contact_name + "]:")
        return DELETE_PARSE_CONFIRMATION
    else:
        await update.message.reply_text("""Этого контакта в книге нет!""")
        return MENU


async def parse_delete_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    confirmation = update.message.text  # парсим присланный пользователем текст
    if confirmation.lower() == "да":
        if context.user_data.get('contact_name_to_delete'):
            contact_name = context.user_data['contact_name_to_delete']
            delete_contact(confirmation, phonebook_dict, contact_name)
            await update.message.reply_text("Контакт " + "[" + contact_name + "] успешно удален!")
            del context.user_data['contact_name_to_delete']
    else:
        await update.message.reply_text("Контакт " + "[" + contact_name + "] не удален!")
    return MENU


async def close(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("До свидания!")
    return MENU


async def import_pb(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("Загрузите файл в формате JSON или CSV:")
    # await update.callback_query.edit_message_text("Импорт контактов успешно!")
    return IMPORT_READ_FILE


async def import_from_csv_or_json(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # создаем объект в памяти, куда запишем содержимое загруженного файла в байтах
    csv = io.BytesIO()
    # дожидаемся загрузки файла
    csv_file = await update.message.document.get_file()
    # записываем содержимое файла в объект в памяти
    await csv_file.download_to_memory(csv)
    # устанавливам начальный байт для чтения созданного объекта в памяти
    csv.seek(0)
    # декодируем байты в UTF-8
    csv_str = csv.read().decode('utf-8')

    try:
        # json.loads() method can be used to parse a valid JSON string and convert it into a Python Dictionary
        pb = json.loads(csv_str)
        for k in pb:
            phonebook_dict[k] = pb[k]
    except:
        try:
            lines = csv_str.strip().split('\n')
            for line in lines:
                k, v = line.split(",")
                phonebook_dict[k] = v
        except Exception as e:
            await update.message.reply_text("Ошибка импорта! Проверьте содержимое файла.")
            return MENU

    await update.message.reply_text("Импорт контактов успешно завершен!")
    return MENU


async def export_pb(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    keyboard = [[InlineKeyboardButton(item, callback_data=item)]
                for item in export_menu_items]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text("Выберите формат файла для экспорта контактов:",
                                                  reply_markup=reply_markup)
    return EXPORT_SELECT_FORMAT


async def export_json(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # json.dumps() function will convert a subset of Python objects into a json string.
    bytes_str = json.dumps(phonebook_dict).encode("utf-16")
    await context.bot.send_document(chat_id=context._chat_id,
                                    document=bytes_str,
                                    filename='pb_export.json')
    await update.callback_query.edit_message_text("Экспорт контактов в JSON произведен успешно!")
    return MENU


async def export_csv(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    csv_str = ""
    for k, v in phonebook_dict.items():
        csv_str += (k + ',' + v + '\n')
    bytes_str = csv_str.encode("utf-16")
    await context.bot.send_document(chat_id=context._chat_id,
                                    document=bytes_str,
                                    filename='pb_export.csv')
    await update.callback_query.edit_message_text("Экспорт контактов в CSV произведен успешно!")
    return MENU


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    app = ApplicationBuilder().token(
        "5791071729:AAEiavttEiJezSYE6RtE6H5MuCp4IZ65XBo").build()

    # Add conversation handler with the states
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", show_menu)],
        allow_reentry=True,
        states={  # список возможных состояний диалога с ботом
            MENU: [  # обработчики события нажатия пользователем на кнопки меню
                CallbackQueryHandler(view, pattern="^" + menu_items[0] + "$"),
                CallbackQueryHandler(add, pattern="^" + menu_items[1] + "$"),
                CallbackQueryHandler(
                    search, pattern="^" + menu_items[2] + "$"),
                CallbackQueryHandler(
                    delete, pattern="^" + menu_items[3] + "$"),
                CallbackQueryHandler(import_pb, pattern="^" +
                                     menu_items[4] + "$"),
                CallbackQueryHandler(export_pb, pattern="^" +
                                     menu_items[5] + "$"),
                CallbackQueryHandler(close, pattern="^" + menu_items[6] + "$")
            ],

            # обработчики события получения сообщения от пользователя
            ADD_PARSE_NAME: [MessageHandler(filters.ALL, parse_contact_name)],
            ADD_PARSE_PHONE: [MessageHandler(filters.ALL, parse_contact_phone)],
            SEARCH_PARSE_NAME: [MessageHandler(filters.ALL, parse_name_as_query)],
            DELETE_PARSE_NAME: [MessageHandler(filters.ALL, parse_name_to_delete)],
            DELETE_PARSE_CONFIRMATION: [MessageHandler(filters.ALL, parse_delete_confirm)],
            IMPORT_READ_FILE: [MessageHandler(filters.ALL, import_from_csv_or_json)],
            EXPORT_SELECT_FORMAT: [CallbackQueryHandler(export_json, pattern="^" + export_menu_items[0] + "$"),
                                   CallbackQueryHandler(export_csv, pattern="^" + export_menu_items[1] + "$")]
        },
        fallbacks=[show_menu]
    )

    app.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    app.run_polling()


if __name__ == "__main__":
    main()
