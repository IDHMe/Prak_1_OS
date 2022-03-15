import xml.etree.ElementTree as ET
import win32api
import win32file
import json
import xml.etree.ElementTree
import zipfile
import os
import shutil
print('_____________________________________________')
print('Вывести информацию в консоль о логических дисках, именах, метке тома, размере и типе файловой системы')


drive_types = {0: 'Unknown', 1: 'No Root Directory', 2: 'Removable Disk', 3: 'Local Disk', 4: 'Network Drive', 5: 'Compact Disk', 6: 'RAM Disk'}

def get_drives_info():
    """Возвращает словарь с информацией по локальным дискам"""
    drive_list = win32api.GetLogicalDriveStrings()
    drive_list = drive_list.split("\x00")[0:-1]
    dict_drives = {}
    for drive in drive_list:
        try:
            drive_type = win32file.GetDriveType(drive)
            drive_size = win32file.GetDiskFreeSpace(drive)
            drive_volume = win32file.GetVolumePathName(drive)
            dict_drives[str(drive)] = {
                'type': drive_types[drive_type],
                'size': round((drive_size[0] * drive_size[1] * drive_size[3]) / (1024 * 1024 * 1024), 1),
                'free_size': round(drive_size[0] * drive_size[1] * drive_size[2] / (1024 * 1024 * 1024), 1),
                'volume_label': drive_volume if drive_volume != drive else "У диска нет метки"}
        except:
            pass

    return dict_drives

drives_data = get_drives_info()
for disk in drives_data.keys():
    s = f'''
    Название: {disk}
    Тип: {drives_data[disk]['type']}
    Пространство: {drives_data[disk]['size']} GB
    Свободное пространство: {drives_data[disk]['free_size']} GB
    Метка: {drives_data[disk]['volume_label']}
    '''
    print(s)

print('_____________________________________________')
print('Работа с файлами')



def delete(filename):
    try:
        os.remove(filename)
    except Exception as ex:
        print("[ОШИБКА ПРИ ПОПЫТКЕ УДАЛЕНИЯ ФАЙЛА]", ex)
    else:
        print("[УДАЛЕН ФАЙЛ] ", filename)


filename = 'text'
file = open(filename, 'w')
user_input = input(f'Введите данные, который попадут в файл {filename}:')
file.write(user_input)
file.close()
with open(filename, 'r') as file:
    print('Содержимое файла: ', file.read())
delete(filename)

print('_____________________________________________')
print('Работа с форматом JSON', '\n')

class VkProfile:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.first_name = kwargs.get('first_name')
        self.last_name = kwargs.get('last_name')
        self.can_access_closed = kwargs.get('can_access_closed')
        self.is_closed = kwargs.get('is_closed')


json_f = open('example/data.json', 'r')
json_data = json.load(json_f)
json_f.close()

profile = VkProfile(**json_data)
print("Объект инициализировался")
print(profile.id,
      profile.first_name,
      profile.last_name,
      profile.is_closed, sep='\n')

with open('profile.json', 'w') as file:
    json.dump(profile.__dict__, file, indent=5)

with open('profile.json', 'r') as json_f:
    json_data = json.load(json_f)

print(json_data)
delete('profile.json')


print('_____________________________________________')
print('Работа с форматом XML', '\n')

def user_xml_parse(root: xml.etree.ElementTree.Element) -> dict:
    user_data = {}
    for x in root.findall('user'):
        name = x.attrib.get('username')
        group = x.find('group').text
        age = x.find('age').text
        user_data[name] = {'group': group, 'age': age}
    return user_data


def print_user_data(user_data: dict):
    for user in user_data:
        print(f'\nUser: {user}\n\tAge: {user_data[user]["age"]}\n\tgroup: {user_data[user]["group"]}')


def append_user(root: xml.etree.ElementTree.Element, user_info: dict):
    user = ET.fromstring(f'''<user username="{user_info['username']}">
        <group>{user_info['group']}</group>
        <age>{user_info['age']}</age>
    </user>''')
    root.append(user)
    print("\n--------Информация о пользователе добавлена--------")


tree = ET.parse('example/data.xml')
root = tree.getroot()
data = user_xml_parse(root)
print_user_data(data)
info = {'username': input('Введите данные [Имя, Фамилия]: '), 'age': input('Введите возраст: '),
        'group': input('Введите группу: ')}
append_user(root, info)
tree.write('data.xml')
data = user_xml_parse(root)
print_user_data(data)
delete('data.xml')

print('_____________________________________________')
print('Создание zip архива, добавление туда файла, определение размера архива')





def check_path(path):
    if os.path.isfile(path):
        shutil.copy(src=path, dst=os.path.dirname(os.path.abspath(__file__)))
        return True
    else:
        print('[ОШИБКА] Файла не найден. Попробуйте еще')


check = False
path = ''
while not check:
    path = input('Введите путь файла который необходимо архивировать: ')
    check = check_path(path)

path = os.path.basename(path)
zip_path = f'{"".join(path.split(".")[:-1])}.zip'
with zipfile.ZipFile(zip_path, 'w') as zzip:
    try:
        zzip.write(path, compress_type=zipfile.ZIP_DEFLATED)
    except Exception as ex:
        print('[ОШИБКА]', ex)
    else:
        delete(path)
        print(f'[ZIP СОЗДАН]Данные архивированы {zzip.filename}')
input("Нажмите для продолжения...")
with zipfile.ZipFile(zip_path, 'r') as zzip:
    try:
        print(f'[ИНФОРМАЦИЯ ПО СЖАТИЮ]Архив: {zip_path}')
        for name in zzip.namelist():
            info = zzip.getinfo(name)
            print(f'\t+ Файл: {info.filename}[Исходный размер: {info.file_size}|'
                  f'Сжатый размер: {info.compress_size}|Тип сжатия: {info.compress_type}|'
                  f'Сжатие %: {100 - round(int(info.compress_size) * 100 / int(info.file_size), 1)}]')
        zzip.extract(member=path, path='')
    except Exception as ex:
        print('[ОШИБКА]', ex)
    else:
        print("[UN-ZIP]Данные разархивированы")
input("Нажмите для продолжения...")
delete(zip_path)
delete(path)
