from datetime import datetime
from itertools import dropwhile, takewhile
from time import sleep
import instaloader
import requests
from tqdm import tqdm
import re
import sys
import os
import json

HOME = 'C:/ProgramData/InstagramDownloader'

while True:
    LOGIN = input('Do you want to Login with an account? Login is not necessary but may be recommended if needed to download hundreads of posts. The non login executions has limited ammount of api calls to Instagram servers. [y/n]').lower()
    if LOGIN == 'y':
        USERNAME = input('Type your username: ')
        PASSWORD = input('Type your password: ')
        break
    elif LOGIN == 'n':
        break

L = instaloader.Instaloader()
if LOGIN == 'y':
    L.login(user=USERNAME, passwd=PASSWORD)

if os.path.isdir(HOME) == False:
    os.mkdir(HOME)

if os.path.isdir(os.path.join(HOME,'Posts')) == False:
    os.mkdir(os.path.join(HOME,'Posts'))

if os.path.isdir(os.path.join(HOME,'Config')) == False:
    os.mkdir(os.path.join(HOME,'Config'))

if os.path.isfile(os.path.join(HOME, f'Config/usernames.txt')) == False:
    with open(os.path.join(HOME, f'Config/usernames.txt'), 'w') as f:
        f.write('mentalidade_de_homem\ncristiano')

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
    SINCE = f.read()

with open(os.path.join(HOME, f'Config/UNTIL.txt'), 'r') as f:
    UNTIL = f.read()

with open(os.path.join(HOME, f'Config/SLEEP_SECONDS_PER_DOWNLOAD.txt'), 'r') as f:
    SLEEPTIME = int(f.read())

with open(os.path.join(HOME, f'Config/ALLOW_VIDEO.txt'), 'r') as f:
    ALLOW_VIDEO = f.read().lower()

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
            post_date = datetime.strftime(post.date, '%Y-%m-%d')
            if post_date < UNTIL and post_date > SINCE:
                matches.append(post)
        print(f"{len(matches)} {username}' posts found between {SINCE} and {UNTIL}")

        n = 1
        for post in posts:
            z = 1
            post_date = datetime.strftime(post.date, '%Y-%m-%d')

            if post_date < UNTIL and post_date > SINCE:
            	
                if post.is_video == True:
                    if ALLOW_VIDEO != 'false':
                        ext = '.mp4'
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
                                        filename = f'{post.owner_username}_{post_date}{ext}'
                                        while os.path.isfile(os.path.join(HOME, f'Posts/{filename}')) == True:
                                            filename = f'{post.owner_username}_{post_date}({str(z)}){ext}'
                                            z += 1
                                        t=tqdm(total=file_size, unit='B', unit_scale=True, desc=filename, ascii=True)
                                        with open(f'{os.path.join(HOME,"Posts/")}{filename}', 'wb') as f:
                                            for data in file_size_request.iter_content(block_size):
                                                t.update(len(data))
                                                f.write(data)
                                        t.close()
                                        print("Video downloaded successfully")
                                        n += 1
                        except Exception as e:
                            print(e)
                    else:
                        print('ALLOW_VIDEO.txt is set to "false". Set it to "true" to enable it')

                else:
                    ext = '.jpg'
                    filename = f'{post.owner_username}_{post_date}{ext}'
                    while os.path.isfile(os.path.join(HOME, f'Posts/{filename}')) == True:
                        filename = f'{post.owner_username}_{post_date}({str(z)}){ext}'
                        z += 1
                    r = requests.get(post.url)
                    print(f'Downloading post {n} www.instagram.com/p/{post.shortcode}')
                    with open(f'{os.path.join(HOME,"Posts/")}{filename}', 'wb') as file:
                        file.write(r.content)
                        print('Download Done.')
                        n += 1
                sleep(SLEEPTIME)
            else:
                print('post doesnt match date')

    except Exception as e:
        print(e)
      
print('Finished')
