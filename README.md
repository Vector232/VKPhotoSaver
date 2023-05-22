# Курсовая работа
## Задание
Нужно написать программу, которая будет:
- Получать фотографии с профиля. 
- Для этого нужно использовать метод photos.get.
- Сохранять фотографии максимального размера(ширина/высота в пикселях) на Я.Диске.
- Для имени фотографий использовать количество лайков.
- Сохранять информацию по фотографиям в json-файл с результатами.

### Обязательные требования к программе
- Использовать REST API Я.Диска и ключ, полученный с полигона.
- Для загруженных фотографий нужно создать свою папку.
- Сохранять указанное количество фотографий(по умолчанию 5) наибольшего размер(ширина/высота в пикселях) на Я.Диске
- Сделать прогресс-бар или логирование для отслеживания процесса программы.
- Код программы должен удовлетворять PEP8.
- У программы должен быть свой отдельный репозиторий.
- Все зависимости должны быть указаны в файле requiremеnts.txt.

### Необязательные требования к программе
- Сохранять фотографии и из других альбомов.
- Сохранять фотографии на Google.Drive.

## Текущая реализация

### Встречает фрейм с полями для дальнейшей работы
![Фрейм с полями](/screens/InputsFrame.PNG)
### Быстро проверяет верность введенных данных.
![Фрейм с полями](/screens/InputsFrame_check.PNG)
### Пропускает дальше, если все верно (но это не точно)
![Фрейм с полями](/screens/InputsFrame_success.PNG)
### Важная часть с кодом. Нажатие на кнопку Connect.
```Python
 def click_Connect():
            # формируем структуру со всеми необходимыми данными для дальнейшей передачи на диск
            def create_AllInfo():
                # ищет ссылку на фото с максимальным размером
                def maxSizePhoto(sizes): # photos -> list
                    url = max(sizes, key = lambda size: size['height']*size['width'])['url']
                    return url

                album_ids = ','.join([str(i) for i in range(-40,40)])
                resp = requests.get('https://api.vk.com/method/photos.getAlbums', params={'access_token': self.VK_Token,
                                                                                          'v': self.version,
                                                                                          'owner_id': self.VK_ID,
                                                                                          'album_ids': album_ids})
                
                dataA = resp.json()
                self.allInfo = {}
                # если все нормально
                if dataA.get('response'):
                    # на случай если нет доступных фото
                    if dataA['response']['count'] == 0:
                        self.helpCanvas.delete('all')
                        self.helpCanvas.create_text(350, 25, 
                                                    font=('Comic Sans MS', 25), 
                                                    fill='red',
                                                    text='No available albums.',
                                                    tags='text')
                        return False
                    # если есть из чего выбрать
                    for album in dataA['response']['items']:
                        time.sleep(0.34)
                        self.allInfo[album['title']] = {'status': False, 'id': album['id'], 'photos': {}}
                        resp = requests.get('https://api.vk.com/method/photos.get', params = {'access_token': self.VK_Token,
                                                                                              'v': self.version,
                                                                                              'owner_id': self.VK_ID,
                                                                                              'album_id': album['id'],
                                                                                              'extended': '1'})
                        dataPh = resp.json()
                        self.allInfo[album['title']]['count'] = dataPh['response']['count']
                        for photo in dataPh['response']['items']:
                            self.allInfo[album['title']]['photos'][photo['id']] = {'status': False,
                                                                                   'likes': photo['likes']['count'],
                                                                                   'date': photo['date'],
                                                                                   'url': maxSizePhoto(photo['sizes']),
                                                                                   'icon_url': photo['sizes'][0]['url']}
                    return True
                # если возникла ошибка
                elif dataA.get('error'):
                    print(dataA.get('error'))
                    self.helpCanvas.delete('all')
                    self.helpCanvas.create_text(350, 25, 
                                                font=('Comic Sans MS', 25), 
                                                fill='red',
                                                text=dataA['error']['error_msg'],
                                                tags='text')
                    return False
                # на всякий случай
                else:
                    self.helpCanvas.delete('all')
                    self.helpCanvas.create_text(250, 25, 
                                                font=('Comic Sans MS', 25), 
                                                fill='red',
                                                text='ERROR',
                                                tags='text')
                    return False
                    


            if all([self.VK_ID_Check, self.VK_Token_Check, self.Drive_Token_Check]):
                data = {}
                with open('Inputs.json', 'w') as f:
                    data['VK_ID'] = VK_ID_var.get()
                    data['VK_Token'] = VK_TOKEN_var.get()
                    data['Drive_Token'] = Drive_TOKEN_var.get()
                    data['Drive'] = Radiobutton_var.get()
                    json.dump(data, f)

                if create_AllInfo():
                    self.inputCanvas.pack_forget()
                    self.helpCanvas.pack_forget()
                    self.SetAlbomsCanvas()
                    self.SetPhotosCanvas()
                    self.SetFooterCanvas()
```
### Дальше фрейм с выбором перегружаемых фото
- Нажатие на черный\белый уголок на альбоме добавляет\убирает все фотографии этого альбома в\из списка на перегрузку.
- Нажатие на черный\белый уголок на фото добавляет\убирает фото в\из списка на перегрузку.
- Если все фото альбома помечены на перегрузку, альбом помечается белым уголком. Иначе - черным.

![Фрейм с выбором](/screens/Selection_check.PNG)
### Показывает прогресс, если он есть
![Фрейм с выбором](/screens/Selection_progress.PNG)
### Важная часть с кодом. Нажатие на кнопку Upload.
```Python
# загружает все из выбранных фото в одну папку
        def click_Upload():
            def footerProgressBarUpdater(value, finished=False):
                self.footerCanvas.delete('ProgressBarBlock')
                progress = 0
                while progress < value: # 21
                    self.footerCanvas.create_rectangle(20 + progress*30, 19,
                                                        35 + progress*30, 50,
                                                        fill="#005500" if finished else 'white', 
                                                        outline="#005500" if finished else 'white',
                                                        tags='ProgressBarBlock')
                    progress += 1
                self.footerCanvas.update()
            # запускаем прогрессбар
            footerProgressBarStarter()
            
            # создаем список только из выбранных фото
            upload_list = []
            for album in self.allInfo.keys():
                for photo_id in self.allInfo[album]['photos'].keys():
                    if self.allInfo[album]['photos'][photo_id]['status']:
                        name = f"{self.allInfo[album]['photos'][photo_id]['likes']}_{self.allInfo[album]['photos'][photo_id]['date']}"
                        upload_list.append({'url': self.allInfo[album]['photos'][photo_id]['url'], 'name': name})

            # создаем папку с уникальным именем
            folder_name = 'VKPhotoSaverFolder_1'
            url = 'https://cloud-api.yandex.net/v1/disk/resources?path=VKPhotoSaverFolder_1'
            headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': f'OAuth {self.Drive_Token}'}
            res = requests.put(url=url, headers=headers).json()
            if res.get('error'):
                i = 2
                while res.get('error') == 'DiskPathPointsToExistentDirectoryError':
                    res = requests.put(f'https://cloud-api.yandex.net/v1/disk/resources?path=VKPhotoSaverFolder_{i}', headers=headers).json()
                    i += 1
                folder_name = f'VKPhotoSaverFolder_{i-1}'
            
            '''for i, photo in enumerate(upload_list):  #ЭТА ЧАСТЬ СКАЧИВАЛА ФОТО И ПОТОМ ПЕРЕГРУЖАЛА НА ДИСК С ЛОКАЛЬНОГО ХРАНИЛИЩА
                # скачиваем полноразмерное фото
                h = httplib2.Http('.cache')
                response, content = h.request(photo['url'])
                out = open(f'temp/{photo["name"]}.jpg', 'wb')
                out.write(content)
                out.close()
                # кусок из дз, загружает фото на диск
                res = requests.get(f'{url}/upload?path={folder_name}/{photo["name"]}&overwrite={True}', headers=headers).json() 
                try:
                    with open(f'temp/{photo["name"]}.jpg', 'rb') as f:
                        # если по какой-то причине мы не можем закинуть файл в нужное место, то и ссылки не будет(соответственно и ключа в json файле)
                        if res.get('href'): 
                            response = requests.put(res['href'], files={'file':f})
                        else:
                            print(res)
                except:
                    print(f'No such file or directory: temp/{photo["name"]}.jpg')
                footerProgressBarUpdater(int((i+1)*19/len(upload_list))) # пополняем шкалу
                time.sleep(0.3)
                '''
            # загружаем фото на диск по полученному из ВК URL   
            url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
            token = self.Drive_Token
            headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': f'OAuth {token}'}

            for i, photo in enumerate(upload_list):
                params = {'path': f'{folder_name}/{photo["name"]}', 'url': photo['url']}

                res1 = requests.post(url=url, params=params, headers=headers).json()
                time.sleep(0.3)

            # создаем json с информацией по последним фото
            with open('Info.json', 'w') as f:
                data = upload_list
                json.dump(data, f)
            footerProgressBarUpdater(21, True) 
```
### Меняет цвет на зелененький, когда закончит
![Фрейм с выбором](/screens/Selection_success.PNG)
### Каждая  перегрузка(даже пустая(даже неудачная)) создает папку с уникальным именем
![Фрейм с выбором](/screens/Drive_folders.PNG)
### В папке перегруженные фото с именем по правилу - лайки_датазагрузки
![Фрейм с выбором](/screens/Drive_images.PNG)
### Оставляет файлик Info.json с информацией по сохраненным фото.
Оставил только url и конечное имя.

# Работа по замечаниям.
Все замечания и действия по их отработке.
## Первая проверка.
### requirements.
- Поблема: В requirements вписаны библиотеки, которые уже есть в стандартном пакете. Вызывает ошибки при установке пакетов.
- Решение: Удалил лишние библиотеки из requirements.
### tkinter.
- Проблема: Пришлось устанавливать в виртуальное окружение дополнительно python3-tk-dbg, чтобы запустить программу.
- Решение: Полагаю, проблема связана с различиями в ОС. Сделал отдельный requirements для Ubuntu.
### Проблемы с проверкой ID.
- Проблема: Не предусмотрена длина ID отличная от 8. В случае удаленных или заблокированных профилей, возникает ошибка при проверке полученного ответа.
- Решение: Длина ID больше не ограничена. Изменил проверки полученных данных. Теперь в случае возникновения ошибки, формулировка ошибки будет отображена в нижней области начального фрейма.
### Проблема с папкой temp.
- Проблема: Для скачивания фото преред перегрузкой на диск, необходимо наличие папки temp, которая не создается автоматически.
- Решение: Папка temp больше не нужна, так как фото не скачиваются в локальное хранилище.
### Получение максимальных размеров загружаемых фото.
- Проблема: Ошибочно, полагал, что варианты фото с разными размерами уже отсортированны, а самое большое находится в конце списка.
- Решение: Перед закреплением URL в allInfo, находим большую по размеру фотографию из данных.
```Python
def maxSizePhoto(sizes): # photos -> list
                    url = max(sizes, key = lambda size: size['height']*size['width'])['url']
                    return url
```

## Послесловие
- Так как я крымчанин и доступ к гуглу ограничен (без VPN), решил не запариваться с этой частью задания. Пусть гугл страдает от того, что Я его игнорирую! :)
- 1001 раз пожалел, что решился делать оконное приложение, а не простую консольную программку с логированием через print-ы. 
