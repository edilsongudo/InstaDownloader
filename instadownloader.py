from datetime import datetime
from itertools import dropwhile, takewhile
from time import sleep
import instaloader
import requests
from tqdm import tqdm
import re
import sys
import os
import PySimpleGUI as sg
import queue
import threading

def long_operation_thread():

    HOME = 'C:/Program Files/InstagramDownloader'

    if os.path.isfile(os.path.join(HOME, f'Config/HOME_FOLDER.txt')) == False:
        with open(os.path.join(HOME, f'Config/HOME_FOLDER.txt'), 'w') as f:
            f.write('C:/Program Files/InstagramDownloader')

    with open(os.path.join(HOME, f'Config/HOME_FOLDER.txt'), 'r') as f:
        HOME = f.read().strip()

    print(f'Home folder root is set to {HOME}. You can always change your settings here.')

    L = instaloader.Instaloader()

    if os.path.isdir(HOME) == False:
        os.mkdir(HOME)

    if os.path.isdir(os.path.join(HOME,'Posts')) == False:
        os.mkdir(os.path.join(HOME,'Posts'))

    if os.path.isdir(os.path.join(HOME,'Config')) == False:
        os.mkdir(os.path.join(HOME,'Config'))

    if os.path.isdir(os.path.join(HOME,'Login')) == False:
        os.mkdir(os.path.join(HOME,'Login'))

    if os.path.isfile(os.path.join(HOME, f'Config/usernames.txt')) == False:
        with open(os.path.join(HOME, f'Config/usernames.txt'), 'w') as f:
            f.write('mentalidade_de_homem\ncristiano')

    if os.path.isfile(os.path.join(HOME, f'Login/account_username.txt')) == False:
        with open(os.path.join(HOME, f'Login/account_username.txt'), 'w') as f:
            f.write('your_account_username_create_a_alternative_one_to_this')

    if os.path.isfile(os.path.join(HOME, f'Login/account_password.txt')) == False:
        with open(os.path.join(HOME, f'Login/account_password.txt'), 'w') as f:
            f.write('your_account_password_create_a_new_one_to_this_job')

    if os.path.isfile(os.path.join(HOME, f'Login/LOGIN.txt')) == False:
        with open(os.path.join(HOME, f'Login/LOGIN.txt'), 'w') as f:
            f.write('false')

    if os.path.isfile(os.path.join(HOME, f'Config/ALLOW_VIDEO.txt')) == False:
        with open(os.path.join(HOME, f'Config/ALLOW_VIDEO.txt'), 'w') as f:
            f.write('true')

    if os.path.isfile(os.path.join(HOME, f'Config/SINCE.txt')) == False:
        with open(os.path.join(HOME, f'Config/SINCE.txt'), 'w') as f:
            f.write('2020-11-04')

    if os.path.isfile(os.path.join(HOME, f'Config/UNTIL.txt')) == False:
        with open(os.path.join(HOME, f'Config/UNTIL.txt'), 'w') as f:
            f.write('2020-12-04')

    if os.path.isfile(os.path.join(HOME, f'Config/SLEEP_SECONDS_PER_DOWNLOAD.txt')) == False:
        with open(os.path.join(HOME, f'Config/SLEEP_SECONDS_PER_DOWNLOAD.txt'), 'w') as f:
            f.write('5')

    with open(os.path.join(HOME, f'Config/usernames.txt'), 'r') as f:
        usernames = f.readlines()

    with open(os.path.join(HOME, f'Config/SINCE.txt'), 'r') as f:
        SINCE = f.read().strip()

    print(f'Since date is {SINCE}.')

    with open(os.path.join(HOME, f'Config/UNTIL.txt'), 'r') as f:
        UNTIL = f.read().strip()

    print(f'Until date is {UNTIL}.')

    with open(os.path.join(HOME, f'Config/SLEEP_SECONDS_PER_DOWNLOAD.txt'), 'r') as f:
        SLEEPTIME = int(f.read().strip())

    print(f'Sleep time betwwen downloads is set to {SLEEPTIME}.')

    with open(os.path.join(HOME, f'Config/ALLOW_VIDEO.txt'), 'r') as f:
        ALLOW_VIDEO = f.read().lower().strip()

    print(f'Allow video is set to {ALLOW_VIDEO}. You can set only "true" or "false".')

    with open(os.path.join(HOME, f'Login/account_username.txt'), 'r') as f:
        USERNAME = f.read().lower().strip()

    with open(os.path.join(HOME, f'Login/account_password.txt'), 'r') as f:
        PASSWORD = f.read().lower().strip()

    with open(os.path.join(HOME, f'Login/LOGIN.txt'), 'r') as f:
        LOGIN = f.read().lower()
        if 'true' in LOGIN:
            L.login(user=USERNAME, passwd=PASSWORD)
            print(f'Loggin in with {USERNAME}')
        else:
            print(f'Your are not logged in. Login allows more downloads in less time.\nTo log in, is recommended to create a new profile and go to home folder/Login')

    for username in usernames:
        try:
            username = username.strip()
            print(f"Looking for {username}'s posts... Please wait")
            postagens = instaloader.Profile.from_username(L.context, username).get_posts()

            posts = []
            for post in postagens:
                posts.append(post)

            matches = []
            for post in posts:
                post_date = datetime.strftime(post.date, '%Y-%m-%d %H %M %S')
                if post_date < UNTIL and post_date > SINCE:
                    matches.append(post)
            print(f"{len(matches)} {username}' posts found between {SINCE} and {UNTIL}")

            n = 1
            for post in posts:
                z = 1
                post_date = datetime.strftime(post.date, '%Y-%m-%d %H %M %S')

                if post_date < UNTIL and post_date > SINCE:
                    
                    if post.is_video == True:
                        if ALLOW_VIDEO != 'false':
                            ext = '.mp4'
                            filename = f'{post.owner_username}_{post_date}{ext}'
                            if os.path.isfile(os.path.join(HOME, f'Posts/{filename}')) == False:    
                                url = f'https://www.instagram.com/p/{post.shortcode}'
                                x = re.match(r'^(https:)[/][/]www.([^/]+[.])*instagram.com', url)

                                try:
                                    if x:
                                        request_image = requests.get(url)
                                        src = request_image.content.decode('utf-8')
                                        check_type = re.search(r'<meta name="medium" content=[\'"]?([^\'" >]+)', src)
                                        check_type_f = check_type.group()
                                        final = re.sub('<meta name="medium" content="', '', check_type_f)

                                        if final == "video": 
                                            msg = 'yes'

                                            if msg == "yes":
                                                print("Downloading the video...")
                                                extract_video_link = re.search(r'meta property="og:video" content=[\'"]?([^\'" >]+)', src)
                                                video_link = extract_video_link.group()
                                                final = re.sub('meta property="og:video" content="', '', video_link)
                                                _response = requests.get(final).content
                                                file_size_request = requests.get(final, stream=True)
                                                file_size = int(file_size_request.headers['Content-Length'])
                                                block_size = 1024 
                                                # filename = f'{post.owner_username}_{post_date}{ext}'
                                                # while os.path.isfile(os.path.join(HOME, f'Posts/{filename}')) == True:
                                                #     filename = f'{post.owner_username}_{post_date}({str(z)}){ext}'
                                                #     z += 1
                                                t=tqdm(total=file_size, unit='B', unit_scale=True, desc=filename, ascii=True)
                                                with open(f'{os.path.join(HOME,"Posts/")}{filename}', 'wb') as f:
                                                    for data in file_size_request.iter_content(block_size):
                                                        t.update(len(data))
                                                        f.write(data)
                                                t.close()
                                                print("Video downloaded successfully")
                                                n += 1
                                                sleep(SLEEPTIME)
                                except Exception as e:
                                    print(e)
                            else:
                                print(f'{filename} already downloaded')
                        else:
                            print('ALLOW_VIDEO.txt is set to "false". Set it to "true" to enable it')

                    else:
                        ext = '.jpg'
                        filename = f'{post.owner_username}_{post_date}{ext}'
                        if os.path.isfile(os.path.join(HOME, f'Posts/{filename}')) == False:
                            # while os.path.isfile(os.path.join(HOME, f'Posts/{filename}')) == True:
                            #     filename = f'{post.owner_username}_{post_date}({str(z)}){ext}'
                            #     z += 1
                            r = requests.get(post.url)
                            print(f'Downloading post {n} www.instagram.com/p/{post.shortcode}')
                            with open(f'{os.path.join(HOME,"Posts/")}{filename}', 'wb') as file:
                                file.write(r.content)
                                print('Download Done.')
                                n += 1
                                sleep(SLEEPTIME)
                        else:
                            print(f'{filename} already downloaded.')                    
                else:
                    pass

        except Exception as e:
            print(e)
          
    print('Finished')

                    
def the_gui():

    gui_queue = queue.Queue() #ESTA LINHA E IMPORTANTE
    
    sg.ChangeLookAndFeel('LightGrey1')      
    sg.SetOptions(element_padding=(0, 0))      

    menu_def = [['Bot', ['Login Settings']],    
            ['Help', ['About...']]]

    interruptor_roxo = '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'
    interruptor_cinza = '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'
    
    image = interruptor_cinza

    layout = [      
    [sg.Menu(menu_def, )],
    [sg.Button(image_data=image, button_color=(sg.theme_background_color(), sg.theme_background_color()), border_width=0, key='botao')],
    [sg.Output(size=(160,30))]
         ]      

    janela = sg.Window("InstagramBot", layout, default_element_size=(12, 1), auto_size_text=False, auto_size_buttons=False,      
                   default_button_element_size=(12, 1)).Finalize()
    janela.Maximize()

    while True:
        button, values = janela.read()

        if button == 'botao':
            if image == interruptor_cinza:
                image = interruptor_roxo
                janela['botao'].update(image_data=image)
            elif image == interruptor_roxo:
                image = interruptor_cinza
                janela['botao'].update(image_data=image)


        if button == sg.WIN_CLOSED:
            break

        if button == 'botao':
            if image == interruptor_roxo:
                try:
                    threading.Thread(target=long_operation_thread, daemon=True).start()
                except Exception as e:
                    print('Error starting work thread.')
        
        try:
            message = gui_queue.get_nowait()
        except queue.Empty:
            message = None 
        if message:
            print('Got a message back from the thread: ', message)
            
    janela.close()


if __name__ == '__main__':
    the_gui()
    print('Exiting Program')
