import json


def import_data_from_file(file_name, phone_book_dict):
    if file_name.endswith(".csv"):
        with open(file_name, 'r') as f:
            lines = [line.strip() for line in f]
            for line in lines:
                k, v = line.split(",")
                phone_book_dict[k] = v
    elif file_name.endswith(".json"):
        with open(file_name, 'r') as f:
            pb = json.load(f)
            for k in pb:
                phone_book_dict[k] = pb[k]
    else:
        print("Формат файла не поддерживается!")

    return phone_book_dict


def export_data_to_file(file_name, phone_book_dict={}):
    if file_name.endswith(".csv"):
        with open(file_name, 'w') as f:
            for name in phone_book_dict:
                f.write(name + "," + phone_book_dict[name] + "\n")
    elif file_name.endswith(".json"):
        with open(file_name, 'w') as f:
            f.write(json.dumps(phone_book_dict))
    else:
        print("Формат файла не поддерживается!")


def view_phonebook(phonebook_dict):
    for k, v in phonebook_dict.items():
        print(k, '--->', v)


def add_contact(phonebook_dict, phone_number, contact_name):
    # Проверяем, если ли уже введенный пользователем номер в справочнике. Если такого номера нет, то добавляем его в книгу.
    if phone_number not in phonebook_dict.values():
        phonebook_dict[contact_name] = phone_number
        print("Контакт успешно сохранен.")
        print("Обновленная телефонная книга: ")
        view_phonebook(phonebook_dict)
    # В ином случае, информируем пользователя что контакт уже существует.
    else:
        print("Этот контакт уже существует в телефонной книге.")


def find_phone_number(name, phonebook_dict):
    found = False
    for k, v in phonebook_dict.items():
        if name.lower() == k.lower():
            print(k, '--->', phonebook_dict[k])
            found = True
            return phonebook_dict[k]
    if found == False:
        print("Этого контакта в книге нет. Вернитесь в меню, чтобы добавить контакт.")
        return ""


def delete_contact(confirm, phonebook_dict, name):
    if confirm.capitalize() == 'Да':
        phonebook_dict.pop(name, None)
        print("Можете видеть вашу обновленную книгу ниже: ")
        view_phonebook(phonebook_dict)
    else:
        print("Возвращаемся к главному меню.")
