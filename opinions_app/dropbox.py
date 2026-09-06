import aiohttp
import asyncio
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


# Асинхронная функция, которая создаёт задачи и запускает их.
async def async_upload_files_to_dropbox(images):
    if images is not None:
        # Создать пустой список для асинхронных задач.
        tasks = []
        # Инициализировать единую сессию для работы с aiohttp.
        async with aiohttp.ClientSession() as session:
            for image in images:
                # Для каждого изображения создать асинхронную задачу.
                tasks.append(
                    asyncio.ensure_future(
                        # Передать в асинхронную функцию сессию и изображение.
                        upload_file_and_get_url(session, image)
                    )
                )
            # После того, как все задачи созданы, запустить их на выполнение.
            urls = await asyncio.gather(*tasks)
        return urls

 
 # Асинхронная функция загрузки изображений и получения на них ссылок.
async def upload_file_and_get_url(session, image):
    dropbox_args = json.dumps({
        'autorename': True,
        'mode': 'add',
        'path': f'/{image.filename}',
    })   
    # Асинхронная загрузка в aiohttp выполняется 
    # с помощью асинхронного контекстного менеджера.
    async with session.post(
        UPLOAD_LINK,
        headers={
            'Authorization': AUTH_HEADER,
            'Content-Type': 'application/octet-stream',
            'Dropbox-API-Arg': dropbox_args
        },
        data=image.read()
    ) as response:
        # Асинхронное получение ответа должно сопровождаться 
        # ключевым словом await.
        data = await response.json()
        path = data['path_lower']
    async with session.post(
        SHARING_LINK,
        headers={
            'Authorization': AUTH_HEADER,
            'Content-Type': 'application/json',
        },
        json={'path': path}
    ) as response:
        data = await response.json()
        if 'url' not in data:
            data = data['error']['shared_link_already_exists']['metadata']
        url = data['url']
        url = url.replace('&dl=0', '&raw=1')
    return url 