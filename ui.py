import model


def welcome():
    entry = int(input("""Вас приветствует телефонная книга.
                >> > Пожалуйста, выберете одну из следующих опций: << <
                1. Показать все контакты
                2. Создать новый контакт
                3. Найти телефон по имени
                4. Удалить контакт
                5. Импорт из файла (поддерживаемые форматы: JSON, CSV)
                6. Экспорт в файл (поддерживаемые форматы: JSON, CSV)
                7. Выйти \n"""))
    return entry


def choose_file_name():
    file_name = input("Введите имя файла с расширением (.csv или .json)")
    return file_name


def phonebook():
    # Создаем пустой словарь для хранения контактов (Имя Фамилия + Телефон)
    contact_dict = {}

    while True:
        entry = welcome()

        if entry == 1:
            # Проверяем, является ли словарь контактов пустым.
            # Если он не пуст, то выводим список контактов в консоль
            if len(contact_dict) != 0:
                model.view_phonebook(contact_dict)
            else:
                print(
                    "Телефонная книга пуста! Вернитесь к меню, чтобы добавить новый контакт.")

        elif entry == 2:
            contact_name = input(
                "Введите контакт в формате 'Имя Фамилия': ")
            phone_number = input("Введите телефон.")

            model.add_contact(contact_dict, phone_number, contact_name)

        elif entry == 3:
            name = input(
                "Введите имя и фамилию человека, телефон которого хотели бы найти: ")
            model.find_phone_number(name, contact_dict)

        elif entry == 4:
            name = input(
                "Введите имя и фамилию контакта, который хотите удалить.")
            model.find_phone_number(name, contact_dict)
            confirm = input("Вы уверены, что хотите удалить контакт? Да/Нет ")
            model.delete_contact(confirm, contact_dict, name)

        elif entry == 5:
            file_name = choose_file_name()
            phonebook_dict_imported = model.import_data_from_file(
                file_name, contact_dict)
            model.view_phonebook(phonebook_dict_imported)

        elif entry == 6:
            file_name = choose_file_name()
            model.export_data_to_file(file_name, contact_dict)

        elif entry == 7:
            print("Закрываем книгу.")
            break

        else:
            print("Неверный ввод!")
