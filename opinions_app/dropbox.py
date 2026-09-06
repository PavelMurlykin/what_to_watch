import json

import requests

from . import app

# Заголовок для авторизации. Так заголовок к API будет выполняться
# как от авторизованного пользователя. 
AUTH_HEADER = f'Bearer {app.config["DROPBOX_TOKEN"]}'
# Эндпоинт для загрузки изображений. Его можно найти в документации
# метода [upload()](https://www.dropbox.com/developers/documentation/http/documentation#files-upload).
UPLOAD_LINK = 'https://content.dropboxapi.com/2/files/upload'
# Эндпоинт для создания ссылки на изображение. Его можно найти 
# в документации метода [create_shared_link_with_settings()](https://www.dropbox.com/developers/documentation/http/documentation#sharing-create_shared_link_with_settings).
SHARING_LINK = ('https://api.dropboxapi.com/2/'
                'sharing/create_shared_link_with_settings')

def upload_files_to_dropbox(images):
    urls = []  # Список для сбора готовых ссылок.
    if images is not None:  # Если были переданы изображения...
        for image in images:  # ...для каждого изображения...
            # ...подготовить словарь и указать в нём, 
            # что надо загружать файлы по указанному пути path.
            # В случае если такой файл существует, переименовывать его.
            dropbox_args = json.dumps({
                'autorename': True,
                'path': f'/{image.filename}',
            })
            # Отправить post-запрос для загрузки файла.   
            response = requests.post(
                UPLOAD_LINK,
                headers={
                    # Передать токен.
                    'Authorization': AUTH_HEADER,
                    # Указать, что передача будет в формате бинарных данных.
                    'Content-Type': 'application/octet-stream',
                    # Передать подготовленные ранее аргументы.
                    'Dropbox-API-Arg': dropbox_args
                },
                # Передать файл в виде бинарных данных.
                data=image.read()
            )
            # Получить путь до файла из ответа от API.
            path = response.json()['path_lower']
            # Отправить второй запрос на формирование ссылки.
            response = requests.post(
                SHARING_LINK,
                headers={
                    'Authorization': AUTH_HEADER,
                    # Здесь данные уже в формате обычного json.
                    'Content-Type': 'application/json',
                },
                json={'path': path}
            )
            data = response.json()
            # Проверить, есть ли ключ url на верхнем уровне ответа.
            if 'url' not in data:
                # Обходной манёвр на случай, 
                # если пользователь попытается отправить
                # один и тот же файл дважды. Ему вернётся
                # ссылка на уже существующий файл.
                data = data['error']['shared_link_already_exists']['metadata']
            # Получить ссылку по ключу.
            url = data['url']
            # Заменить режим работы ссылки, 
            # чтобы получить ссылку на скачивание.
            url = url.replace('&dl=0', '&raw=1')
            # Добавить ссылку в общий список ссылок.
            urls.append(url)
    return urls