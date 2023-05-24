import requests
from os import system
# хоба!
try:
    import tkinter as tk
except:
    system('sudo apt install python3-tk-dbg')
    import tkinter as tk

import webbrowser
import json
import time


class Window:
    def __init__(self):
        self.window = tk.Tk()
        self.window.resizable(False, False)
        self.window["bg"] = "black"
        self.window.geometry('800x600')
        self.window.title("VKPhotoSaver")
        self.window.attributes('-fullscreen', False)

        self.height = 600
        self.width = 800

        self.VK_ID_Check = False
        self.VK_Token_Check = False
        self.Drive_Token_Check = False

        self.VK_ID = 'Input VK ID'
        self.VK_Token = 'Input VK Token'
        self.Drive_Token = 'Input Drive Token'
        self.Radiobutton = 1
        # Проверяем сохраненные поля, если нет, то создаем пустой шаблон. Если есть автозаполняем поля в приложении.
        try:
            with open('Inputs.json', 'r') as f:
                data = json.load(f)
        except:
            data = {}
            with open('Inputs.json', 'w') as f:
                data['VK_ID'] = 'None'
                data['VK_Token'] = 'None'
                data['Drive_Token'] = 'None'
                data['Drive'] = 1
                json.dump(data, f)
        else: 
            self.VK_ID = data['VK_ID']
            self.VK_Token = data['VK_Token']
            self.Drive_Token = data['Drive_Token']
            self.Radiobutton = data['Drive']
                 
        self.version = '5.131'
        self.client_id_VK = '51644780'

        self.InputAndHelpCanvas()
        
        self.window.mainloop()


    def InputAndHelpCanvas(self):
        def VK_ID_valid(*args):
            id = VK_ID_var.get()
            if id.isdigit():
                self.VK_ID_Check = True
                self.VK_ID = id
            else:
               self.VK_ID_Check = False

            self.UpdateHelpCanvas()


        def VK_TOKEN_valid(*args):
            url = 'https://api.vk.com/method/photos.get'
            id = str(VK_ID_var.get())
            token = VK_TOKEN_var.get()
            params = {'access_token': token, 'v': self.version, 'user_ids': id, 'album_id': 'wall', 'count': '1'}
           
            response = requests.get(url, params=params)
            data = response.json()
            if data.get('response'):
                self.VK_Token_Check = True
                self.VK_Token = token
            else:
                self.VK_Token_Check = False

            self.UpdateHelpCanvas()

        def Drive_TOKEN_valid(*args):
            token = Drive_TOKEN_var.get()
            headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': f'OAuth {token}'}
            response = requests.get('https://cloud-api.yandex.net/v1/disk', headers=headers).json()
            
            if response.get('user'):
                self.Drive_Token_Check = True
                self.Drive_Token = token
            else:
                self.Drive_Token_Check = False
            
            self.UpdateHelpCanvas()



        def click_Get_VK_ID():
            webbrowser.open('https://vk.com/faq18062?ysclid=lhq07j0q6960719923')


        def click_Get_VK_Token():
            webbrowser.open(f'https://oauth.vk.com/authorize?client_id={self.client_id_VK}&display=page&scope=photos&response_type=token&v=5.131')


        def click_Get_Drive_Token():
            if Radiobutton_var.get() == 1:
                webbrowser.open('https://oauth.yandex.ru/authorize?response_type=token&client_id=72ce1fb25c2d48789b4e0639ad0769ef')
            else:
                pass

        # Важное место
        def click_Connect():
            # формируем структуру со всеми необходимыми данными для дальнейшей передачи на диск
            def create_AllInfo():
                # ищет ссылку на фото с максимальным размером
                def maxSizePhoto(sizes): # photos -> list
                    max_size = max(sizes, key = lambda size: size['height']*size['width'])
                    return max_size['url'], max_size['type']
                #получаем информацию об альбомах
                album_ids = ','.join([str(i) for i in range(-40,40)])
                resp = requests.get('https://api.vk.com/method/photos.getAlbums', params={'access_token': self.VK_Token,
                                                                                          'v': self.version,
                                                                                          'owner_id': self.VK_ID,
                                                                                          'album_ids': album_ids})
                
                dataA = resp.json()
                self.allInfo = {}

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
                                                                                              'extended': '1',
                                                                                              'photo_sizes': '1'})
                        dataPh = resp.json()
                        self.allInfo[album['title']]['count'] = dataPh['response']['count']
                        for photo in dataPh['response']['items']:
                            url, size = maxSizePhoto(photo['sizes'])
                            self.allInfo[album['title']]['photos'][photo['id']] = {'status': False,
                                                                                   'likes': photo['likes']['count'],
                                                                                   'date': photo['date'],
                                                                                   'url': url,
                                                                                   'size': size}
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
                               

        bg = '#CCCCCC'

        self.inputCanvas = tk.Canvas(self.window, 
                                    bg=bg, 
                                    highlightthickness=7,  
                                    height=self.height * 0.65, 
                                    width=self.width,
                                    highlightbackground='black',
                                    highlightcolor='black')
        self.inputCanvas.pack()


        self.VK_ID_Text = tk.Label(self.inputCanvas,
                                   bg=bg,
                                   text='VK ID',
                                   font=('Comic Sans MS', 25))
        self.VK_ID_Text.place(x=10, y=10)

        VK_ID_var = tk.StringVar()
        VK_ID_var.set(self.VK_ID)
        self.VK_ID_Input = tk.Entry(self.inputCanvas,
                                    bg=bg,
                                    bd=5,
                                    font=('Comic Sans MS', 25),
                                    textvariable=VK_ID_var)
        self.VK_ID_Input.place(x=200, y=10)
        VK_ID_var.trace_add('write', VK_ID_valid)

        self.Button_Get_VKToken = tk.Button(self.inputCanvas,
                                        bg='white',
                                        width=12,
                                        text="Get VK ID",
                                        font=('Comic Sans MS', 15),
                                        command=click_Get_VK_ID)
        self.Button_Get_VKToken.place(x=620, y=15)


        self.VK_TOKEN_Text = tk.Label(self.inputCanvas,
                                   bg=bg,
                                   text='VK TOKEN',
                                   font=('Comic Sans MS', 25))
        self.VK_TOKEN_Text.place(x=10, y=80)
        
        VK_TOKEN_var = tk.StringVar()
        VK_TOKEN_var.set(self.VK_Token)
        self.VK_TOKEN_Input = tk.Entry(self.inputCanvas,
                                    bg=bg,
                                    bd=5,
                                    font=('Comic Sans MS', 25),
                                    textvariable=VK_TOKEN_var)
        self.VK_TOKEN_Input.place(x=200, y=80)
        VK_TOKEN_var.trace_add('write', VK_TOKEN_valid)

        self.Button_Get_VKToken = tk.Button(self.inputCanvas,
                                        bg='white',
                                        width=12,
                                        text="Get VK Token",
                                        font=('Comic Sans MS', 15),
                                        command=click_Get_VK_Token)
        self.Button_Get_VKToken.place(x=620, y=85)


        self.Drive_TOKEN_Text = tk.Label(self.inputCanvas,
                                   bg=bg,
                                   text='DRIVE TOKEN',
                                   font=('Comic Sans MS', 25))
        self.Drive_TOKEN_Text.place(x=10, y=155)

        Drive_TOKEN_var = tk.StringVar()
        Drive_TOKEN_var.set(self.Drive_Token)
        self.Drive_TOKEN_Input = tk.Entry(self.inputCanvas,
                                    bg=bg,
                                    bd=5,
                                    font=('Comic Sans MS', 25),
                                    textvariable=Drive_TOKEN_var)
        self.Drive_TOKEN_Input.place(x=10, y=210)
        Drive_TOKEN_var.trace_add('write', Drive_TOKEN_valid)

        self.Button_Get_DriveToken = tk.Button(self.inputCanvas,
                                        bg='white',
                                        width=13,
                                        text="Get Drive Token",
                                        font=('Comic Sans MS', 15),
                                        command=click_Get_Drive_Token)
        self.Button_Get_DriveToken.place(x=250, y=155)


        Radiobutton_var = tk.IntVar()
        Radiobutton_var.set(self.Radiobutton)
        self.Radiobutton_Yandex = tk.Radiobutton(self.inputCanvas,
                                                 bg=bg, 
                                                 text='YDrive',
                                                 font=('Comic Sans MS', 25), 
                                                 variable=Radiobutton_var, 
                                                 value=1)
        self.Radiobutton_Google = tk.Radiobutton(self.inputCanvas,
                                                 bg=bg,
                                                 text='GDrive',
                                                 font=('Comic Sans MS', 25),
                                                 variable=Radiobutton_var, 
                                                 value=2)
        self.Radiobutton_Yandex.place(x=430, y=145)
        self.Radiobutton_Google.place(x=430, y=200)

        self.Button_Connect = tk.Button(self.inputCanvas,
                                        bg='white',
                                        width=38,
                                        text="Connect",
                                        font=('Comic Sans MS', 25),
                                        command=click_Connect)
        self.Button_Connect.place(x=15, y=295)

        self.helpCanvas = tk.Canvas(self.window, 
                                   bg='black', 
                                   highlightthickness=7,  
                                   height=self.height * 0.35, 
                                   width=self.width,
                                   highlightbackground='black',
                                   highlightcolor='black')
        self.helpCanvas.pack()

        
        VK_ID_valid()
        VK_TOKEN_valid()
        Drive_TOKEN_valid()

        self.UpdateHelpCanvas()

    def UpdateHelpCanvas(self):
        self.helpCanvas.delete('text')
        if all([self.VK_ID_Check, self.VK_Token_Check, self.Drive_Token_Check]):
            self.helpCanvas.create_text(400, 100, 
                                        font=('Comic Sans MS', 25), 
                                        fill='green',
                                        text='Click the "Connect" button',
                                        tags='text')
        else:
            self.helpCanvas.create_text(150, 25, 
                                        font=('Comic Sans MS', 25), 
                                        fill='green' if self.VK_ID_Check else 'red',
                                        text='V - Enter VK ID' if self.VK_ID_Check else 'X - Enter VK ID',
                                        tags='text')
        
            self.helpCanvas.create_text(200, 75, 
                                        font=('Comic Sans MS', 25), 
                                        fill='green' if self.VK_Token_Check else 'red',
                                        text='V - Enter VK Token' if self.VK_Token_Check else 'X - Enter VK Token',
                                        tags='text')
        
            self.helpCanvas.create_text(250, 125, 
                                        font=('Comic Sans MS', 25), 
                                        fill='green' if self.Drive_Token_Check else 'red',
                                        text='V - Enter Drive Token' if self.Drive_Token_Check else 'X - Enter Drive Token',
                                        tags='text')
        
        


    def SetAlbomsCanvas(self):
        def displacement_changer(*args):
            self.UpdateAlbumsCanvas(self.album_displacement.get())

        bg = '#444444'
        albom_count = len(self.allInfo.keys())
        self.albomsCanvas = tk.Canvas(self.window, 
                                    bg=bg, 
                                    highlightthickness=7,  
                                    height=self.height * 0.3, 
                                    width=self.width,
                                    highlightbackground='black')
        self.albomsCanvas.pack(fill=tk.BOTH, expand=True)
        self.album_displacement = tk.IntVar()
        self.album_displacement.set(0)
        self.albomsScale = tk.Scale(self.albomsCanvas,
                                    bg='black',
                                    troughcolor=bg,
                                    highlightbackground=bg,
                                    bd=0,
                                    from_=0,
                                    to=100 * (albom_count * 1.9),
                                    sliderlength=45,
                                    length=750,
                                    showvalue=0,
                                    orient='horizontal',
                                    variable=self.album_displacement)
        self.albomsScale.pack(side=tk.BOTTOM, pady=7)
        self.album_displacement.trace_add('write', displacement_changer)

        self.UpdateAlbumsCanvas()
        
    def UpdateAlbumsCanvas(self, displacement=0):
        def flagChanger(title):
            self.allInfo[title]['status'] = not self.allInfo[title]['status']
            for photo_id in self.allInfo[title]['photos']:
                self.allInfo[title]['photos'][photo_id]['status'] = self.allInfo[title]['status']
            self.UpdateAlbumsCanvas(displacement)
            self.UpdatePhotosCanvas(self.photo_displacement.get())

        def MultiEvent(title):
            return lambda event: flagChanger(title)
        all_rect = []
        distance = 0
        self.albomsCanvas.delete('all')
        

        for albom in self.allInfo.keys():
            name = albom
            self.albomsCanvas.create_rectangle(10 - displacement + distance, 10,
                                               150 - displacement + distance, 200,
                                               fill="peru", 
                                               outline="black")

            self.albomsCanvas.create_text(80 - displacement + distance, 100, 
                                          font=('Comic Sans MS', 10), 
                                          text=name)
            
            if self.allInfo[name]['status']: fill = 'white'
            else: fill = 'black'
            rect = self.albomsCanvas.create_rectangle(10 - displacement + distance, 10,
                                               30 - displacement + distance, 30,
                                               fill=fill, 
                                               outline="black")
            all_rect.append([rect, name])

            distance += 200

        for rect in all_rect:
            self.albomsCanvas.tag_bind(rect[0], '<Button-1>', MultiEvent(rect[1]))
        

    def SetPhotosCanvas(self):
        def displacement_changer(*args):
            self.UpdatePhotosCanvas(self.photo_displacement.get())

        bg = '#444444'

        photo_count = 0
        for album in self.allInfo.keys():
            photo_count += self.allInfo[album]['count']
        self.photosCanvas = tk.Canvas(self.window, 
                                    bg=bg, 
                                    highlightthickness=7,  
                                    height=self.height * 0.4, 
                                    width=self.width,
                                    highlightbackground='black')
        self.photosCanvas.pack(fill=tk.BOTH, expand=True)
        self.photo_displacement = tk.IntVar()
        self.photo_displacement.set(0)
        self.photo_displacement
        self.photosScale = tk.Scale(self.photosCanvas,
                                    bg='black',
                                    troughcolor=bg,
                                    highlightbackground=bg,
                                    bd=0,
                                    from_=0,
                                    to=100 * (photo_count * 1.9),
                                    sliderlength=20,
                                    length=750,
                                    showvalue=0,
                                    orient='horizontal',
                                    variable=self.photo_displacement)
        self.photosScale.pack(side=tk.BOTTOM, pady=7)
        self.photo_displacement.trace_add('write', displacement_changer)

        self.UpdatePhotosCanvas()

    def UpdatePhotosCanvas(self, displacement=0):
        def flagChanger(album_id, photo_id):
            self.allInfo[album_id]['photos'][photo_id]['status'] = not self.allInfo[album_id]['photos'][photo_id]['status']
            
            # проверяет все ли фотографии в альбоме выбраны для передачи и меняет флажек над альбомом
            if all([self.allInfo[album_id]['photos'][photo_id]['status'] for photo_id in self.allInfo[album_id]['photos']]):
                self.allInfo[album_id]['status'] = True
            elif all([not self.allInfo[album_id]['photos'][photo_id]['status'] for photo_id in self.allInfo[album_id]['photos']]):
                self.allInfo[album_id]['status'] = False
            else: # оставлено на будущее
                self.allInfo[album_id]['status'] = False

            self.UpdateAlbumsCanvas(self.album_displacement.get())
            self.UpdatePhotosCanvas(displacement)

        def MultiEvent(album_id, photo_id):
            return lambda event: flagChanger(album_id, photo_id)
        
        self.photosCanvas.delete('all')
        distance = 0
        all_rect = []
        # содержимое поля с фотографиями
        for album in self.allInfo.keys():
            for photo_id in self.allInfo[album]['photos']:
                self.photosCanvas.create_rectangle(10 - displacement + distance, 10,
                                                   150 - displacement + distance, 200,
                                                   fill="peru", 
                                                   outline="black")

                self.photosCanvas.create_text(80 - displacement + distance, 100, 
                                              font=('Comic Sans MS', 10), 
                                              text=photo_id)
                self.photosCanvas.create_text(80 - displacement + distance, 120, 
                                              font=('Comic Sans MS', 10), 
                                              text=f"likes: {self.allInfo[album]['photos'][photo_id]['likes']}")
                self.photosCanvas.create_text(80 - displacement + distance, 140, 
                                              font=('Comic Sans MS', 10), 
                                              text=self.allInfo[album]['photos'][photo_id]['date'])
            
                if self.allInfo[album]['photos'][photo_id]['status']: fill = 'white'
                else: fill = 'black'
                rect = self.photosCanvas.create_rectangle(10 - displacement + distance, 10,
                                                          30 - displacement + distance, 30,
                                                          fill=fill, 
                                                          outline="black")
                all_rect.append([rect, album, photo_id])

                distance += 200
            # черная вертикальная полоска разделяет фотографии разных альбомов
            self.photosCanvas.create_rectangle(-30 - displacement + distance, 10,
                                               -20 - displacement + distance, 200,
                                               fill="black", 
                                               outline="black")

        for rect in all_rect:
            self.photosCanvas.tag_bind(rect[0], '<Button-1>', MultiEvent(rect[1], rect[2]))

    def SetFooterCanvas(self):
        # запускает прогрессбар
        def footerProgressBarStarter():
            self.footerCanvas.delete('ProgressBar','ProgressBarBlock')
            self.footerCanvas.create_rectangle(11, 10,
                                               640, 60,
                                               width=5,
                                               fill="black", 
                                               outline="white",
                                               tags='ProgressBar')
            self.footerCanvas.update()
        # Важное место
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
                        name = f"{self.allInfo[album]['photos'][photo_id]['likes']}_{self.allInfo[album]['photos'][photo_id]['date']}.jpg"
                        upload_list.append({'url': self.allInfo[album]['photos'][photo_id]['url'],
                                            'name': name,
                                            'size': self.allInfo[album]['photos'][photo_id]['size']})

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
            url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
            token = self.Drive_Token
            headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': f'OAuth {token}'}

            for i, photo in enumerate(upload_list):
                params = {'path': f'{folder_name}/{photo["name"]}', 'url': photo['url']}

                res1 = requests.post(url=url, params=params, headers=headers).json()
                time.sleep(0.3)

            # создаем json с информацией по последним фото
            with open('Info.json', 'w') as f:
                data = [{'file_name': photo['name'], 'size': photo['size']} for photo in upload_list]
                json.dump(data, f)
            footerProgressBarUpdater(21, True) 



        self.progress = 0
        self.footerCanvas = tk.Canvas(self.window, 
                                    bg='black', 
                                    highlightthickness=7,  
                                    height=self.height * 0.1, 
                                    width=self.width,
                                    highlightbackground='black')
        self.footerCanvas.pack()

        self.Upload_Button = tk.Button(self.footerCanvas,
                                        bg='white',
                                        width=10,
                                        text="Upload",
                                        font=('Comic Sans MS', 15),
                                        command=click_Upload)
        self.Upload_Button.place(x=650, y=10)

vkPhotoSaver = Window()
