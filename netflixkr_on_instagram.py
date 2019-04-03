import requests
from requests.exceptions import HTTPError
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime
from datetime import timedelta

# moabot 컴포넌트를 가져온다.
import moabot_database as moabot
from moabot_id import *

# 사이트 이름
site_name = 'instagram'
# 사이트에서 가져올 주제
section_name = 'netflixkr'
# 사이트 주소
site_url = 'https://www.instagram.com/netflixkr/?hl=ko'
print('site url is: ', site_url)

# 사이트의 HTML을 가져온다.
try:
    response = requests.get(site_url)
    # 에러가 발생 했을 경우 에러 내용을 출력하고 종료한다.
    response.raise_for_status()
except HTTPError as http_err:
    print(f'HTTP error occurred: {http_err}')
except Exception as err:
        print(f'Other error occurred: {err}')
else:
    html_source = response.text
    #print(response.status_code)
    #print(html_source)
    
    # BeautifulSoup 오브젝트를 생성한다.
    soup = BeautifulSoup(html_source, 'html.parser')
    
    # 디버그를 위해서 page의 소스를 파일로 저장한다.
    # 봇으로 등록하기 위해서는 주석처리를 해야한다.
    #import os.path
    #file_name = site_name + '_requests.html'
    #if not os.path.isfile(file_name):
    #    print('file save: ', file_name)
    #    with open(file_name, 'w') as f:
    #        f.write(soup.prettify())
    
    # 데이터를 저장할 데이터베이스를 연다. 
    # bot_id는 moabot_id에서 가져오는 변수값이다.
    # 프로그램을 종료하기 전에 데이터 베이스를 닫아야 한다.
    db_name = section_name + '_on_' + site_name 
    my_db = moabot.Dbase(db_name, bot_id)
    
    post_json = ''
    # 정보가 저장되어 있는 json파일을 수집한다.
    for post in soup.find_all('script', {'type': 'text/javascript'}):
        if post.text.find('window._sharedData = {') != -1:
            post_json = post.text.replace('window._sharedData = ', '').replace(';', '')      
    #print(post_json[:100])
    #print(post_json[len(post_json) -100 :])
    
    json_data = json.loads(post_json)
    
    # dump data for debug
    #post_dump = json.dumps(json_data, indent=4)
    #print(post_dump[:100])
    #with open('json_dump.json', 'w') as f:
    #     f.write(post_dump)
    
    # entry_data.ProfilePage[0].graphql.user.edge_owner_to_timeline_media.edges[]
    # title: node.edge_media_to_caption.edges[0].node.text
    # url: node.shortcode
    # createdAt: node.taken_at_timestamp
    # image: node.display_url
    # createdBy: node.owner.username
    edges = json_data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['edges']
    
    for edge in edges:
        timestamp = int(edge['node']['taken_at_timestamp'])
        delta = datetime.now() - datetime.fromtimestamp(timestamp)
        if  delta.days <= 0:
        
            title = edge['node']['edge_media_to_caption']['edges'][0]['node']['text']
            # Title
            moa_title = title.splitlines()[0]
            #print('title: ', moa_title)
            # Description
            moa_desc = ''.join(title.splitlines()[1:])
            #print(moa_desc)
            # URL
            href = edge['node']['shortcode']
            moa_url = 'https://www.instagram.com/p/' + href
            #print('url: ', moa_url)
            # Image
            moa_image = edge['node']['display_url']
            #print('image: ', moa_image)
            # CreatedAt
            moa_createdAt = datetime.fromtimestamp(timestamp)
            #print('createdAt: ', moa_createdAt)
            # CreatedBy
            moa_createdBy = edge['node']['owner']['username']
            #print('createdBt: ', moa_createdBy)
            # timeStamp
            moa_timeStamp = datetime.now()
            #print('timeStamp: ', moa_timeStamp)
            
            # siteName
            moa_site_name = 'Instagram'
            
            # 데이터베이스에 있는 포스트와 중복되는지를 확인한다.
            if my_db.isNewItem('title', moa_title):
                # 데이터 타입을 확인한다.
                assert type(moa_title) == str, 'title: type error'
                assert type(moa_desc) == str, 'desc: type error'
                assert type(moa_url) == str, 'url: type error'
                assert type(moa_image) == str, 'image: type error'
                assert type(moa_site_name) == str, 'siteName: type error'
                assert type(moa_createdBy) == str, 'createdBy: type error'
                assert type(moa_createdAt) == datetime, 'createdAt: type error'
                assert type(moa_timeStamp) == datetime, 'timeStamp: type error'

                # JSON형식으로 수집한 데이터를 변환한다.
                db_data = { 'title': moa_title, 
                    'desc': moa_desc,
                    'url': moa_url,
                    'image': moa_image,
                    'siteName': moa_site_name,
                    'createdBy': moa_createdBy,
                    'createdAt': moa_createdAt,
                    'timeStamp': moa_timeStamp
                }

                # 디버그를 위해서 수집한 데이터를 출력한다.
                temp_data = db_data.copy()
                temp_data['desc'] = temp_data['desc'][:20] + '...'
                print(json.dumps(temp_data, indent=4, ensure_ascii=False, default=str))

                # 수집한 데이터를 데이터베이스에 전송한다.
                my_db.insertTable(db_data)

    # 데이터 베이스를 닫는다.
    my_db.close()

