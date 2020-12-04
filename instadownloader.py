from datetime import datetime
from itertools import dropwhile, takewhile
from time import sleep
import instaloader
import requests
from tqdm import tqdm
import re
import sys
import os

username = 'mentalidade_de_homem'
USERNAME = '****************'
PASSWORD = '****************'
SLEEPTIME = 1
SINCE = datetime(2020, 1, 1)
SINCE = datetime.strftime(SINCE, '%Y-%m-%d')
UNTIL = datetime(2020, 12, 4)
UNTIL = datetime.strftime(UNTIL, '%Y-%m-%d')

if os.path.isdir(os.path.join(os.getcwd(),'Posts')) == False:
    os.mkdir(os.path.join(os.getcwd(),'Posts'))

L = instaloader.Instaloader()
L.login(user=USERNAME, passwd=PASSWORD)

if not username:
    username = input('Type the username: ')

print('Looking for user posts...')
postagens = instaloader.Profile.from_username(L.context, username).get_posts()

posts = []
for post in postagens:
    posts.append(post)

matches = []
for post in posts:
    post_date = datetime.strftime(post.date, '%Y-%m-%d')
    if post_date < UNTIL and post_date > SINCE:
        matches.append(post)
print(f'{len(matches)} posts found that match these dates...')

n = 1
for post in posts:
    z = 1
    post_date = datetime.strftime(post.date, '%Y-%m-%d')

    if post_date < UNTIL and post_date > SINCE:
    	
        if post.is_video == True:
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
                            while os.path.isfile(os.path.join(os.getcwd(), f'Posts/{filename}')) == True:
                                filename = f'{post.owner_username}_{post_date}({str(z)}){ext}'
                                z += 1
                            t=tqdm(total=file_size, unit='B', unit_scale=True, desc=filename, ascii=True)
                            with open(f'{os.path.join(os.getcwd(),"Posts/")}{filename}', 'wb') as f:
                                for data in file_size_request.iter_content(block_size):
                                    t.update(len(data))
                                    f.write(data)
                            t.close()
                            print("Video downloaded successfully")
                            n += 1

            except Exception as e:
                print(e)

        else:
            ext = '.jpg'
            filename = f'{post.owner_username}_{post_date}{ext}'
            while os.path.isfile(os.path.join(os.getcwd(), f'Posts/{filename}')) == True:
                filename = f'{post.owner_username}_{post_date}({str(z)}){ext}'
                z += 1
            r = requests.get(post.url)
            print(f'Downloading post {n} www.instagram.com/p/{post.shortcode}')
            with open(f'{os.path.join(os.getcwd(),"Posts/")}{filename}', 'wb') as file:
                file.write(r.content)
                print('Download Done.')
                sleep(SLEEPTIME)
                n += 1