#%% [markdown]
# ## 넷플릭스 인스타 🤖
#
# 넷플릭스 인스타그램을 모아주는 봇입니다.
# 
# - 개발자: skettee
#
# - 깃허브 주소: [netflixkr_on_instagram](https://github.com/skettee/netflixkr_on_instagram)
# 
#
# ### 개발 환경 만들기
# 
# 봇을 개발하기 위해서는 몇가지 소프트웨어를 설치하고 환경을 설정해야 합니다. 
# [개발 환경 만들기](https://github.com/moabogey/docs/wiki/개발환경만들기)를 참조 하세요.
# 
# ### 코드 실행
# 
# - 터미널 실행
#
#   - 🖼  Windows PowerShell을 실행한다.
#
#   - 🍎 Terminal을 실행한다.
# 
# - 작업할 폴더를 생성한다.
# 
# ```
# mkdir MyWork
# ```
# 
# - 작업할 폴더로 이동한다.
#  
# ```
# cd MyWork
# ```
# 
# - 깃 클론 (Git Clone)을 수행한다.
# 
# ```
# git clone https://github.com/skettee/netflixkr_on_instagram.git
# ```
# 
# - 복사한 코드의 폴더로 이동한다.
# 
# ```
# cd netflixkr_on_instagram
# ```
# 
# - VSCode를 실행한다.
# 
# ```
# code .
# ```
# 
# - 왼쪽 EXPLORE에서 `netflixkr_on_instagram.py`를 선택한다.
# 
# - 하단 바에 `Python3.7.3 64-bit('base':conda)`를 누른다.
# 
# - `Python 3.6.8 64-bit ('moabogey':conda)`를 선택한다.
# 
# - 소스 코드에 RunCell | Run Below에서 `Run Below`를 누른다.
# 
# - 데이터가 정상적으로 수집이 되는지 오른쪽 Python Interactive에서 확인한다. 
#    
#
# ### 코드 분석
# 
# netflixkr_on_instagram.py를 분석합니다.  
# 봇의 소스 코드는 크게 세단계로 나눌 수 있습니다.  
# 
# 1. 사이트의 HTML에서 JSON 데이터를 수집
# 
# 2. JSON 데이터에서 포스트 데이터를 수집
# 
# 3. 데이터 저장
#  
#
# **사이트의 HTML에서 JSON 데이터를 수집**
#  
# - 데이터를 수집할 사이트의 정보와 주소를 설정합니다. 여기에서는 https://www.instagram.com/netflixkr/?hl=ko 에서 데이터를 수집합니다.
# 
# - requests와 beautifulsoup4를 이용해서 사이트의 HTML을 가져오고 파일로 저장합니다.
# 
# - 저장된 HTML파일 (instagram_source.html)을 열어 봅니다. 여기서 우리가 원하는 정보를 가지고 있는 JSON 데이터를 찾습니다.
#
# - JSON을 분석하기 위해 JSON DUMP를 파일로 저장합니다.
#  
#
# **JSON 데이터에서 포스트 데이터를 수집**
#  
# - 저장된 JSON파일 (json_dump.json)을 열어 봅니다. 여기서 우리는 "포스트의 리스트"를 표현하는 구간을 찾을 것입니다. **포스트**는 제목, 내용, 이미지, 작성자, 작성 날짜 및 페이지 위치(URL)를 가지고 있는 하나의 문서를 나타내는 용어로 사용합니다.
# 
# ```
# entry_data.ProfilePage[0].graphql.user.edge_owner_to_timeline_media.edges[ (Post1), (Post2), ...]
# ```
# 
# - 발견한 포스트에서 아래와 같이 제목, 포스트 위치(URL), 포스트 시간, 이미지 및 작성자를 찾습니다.
# 
# ```
# title: node.edge_media_to_caption.edges[0].node.text
# url: node.shortcode
# createdAt: node.taken_at_timestamp
# image: node.display_url
# createdBy: node.owner.username
# ```
#  
#
# **데이터 저장**
# 
# - 수집한 데이터를 선별해서 중복되는 것을 제외하고 데이터베이스에 저장합니다. 모아보기 봇은 하루에 24번 이상 동작 하도록 되어 있기 때문에 한번에 모든 데이터를 수집하지 않고 가장 최근의 데이터 1~2개를 수집하는 것이 원칙입니다. 여기서는 현재 날짜에 포스팅된 것만 수집합니다.
#  
#
# ### 참고 사이트
#  
# - [개발 환경 만들기](https://github.com/moabogey/docs/wiki/개발환경만들기)
#
# - [예제 코드 실행](https://github.com/moabogey/docs/wiki/예제코드실행)
#
# - [코딩을 하기 전에](https://github.com/moabogey/docs/wiki/코딩하기전에)
#
# - [예제 코드 분석](https://github.com/moabogey/docs/wiki/예제코드분석)
#
# - [봇 개발 하기](https://github.com/moabogey/docs/wiki/봇개발하기)
# 
#
# ### ⬇️소스코드

#%%
import requests
from requests.exceptions import HTTPError
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime
from datetime import timedelta

if __debug__:
    import os.path

# 모아보기 컴포넌트를 가져온다.
import moabogey_database as moabogey
from moabogey_id import *

# 사이트 이름
site_name = 'instagram'
# 사이트에서 가져올 주제
subject_name = 'netflixkr'
# 사이트 주소
site_url = 'https://www.instagram.com/netflixkr/?hl=ko'
if __debug__:
    print('{} 데이터 수집 중... ⚙️'.format(site_url))

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
    
    # HTML을 분석하기 위해서 페이지의 소스를 파일로 저장한다.
    if __debug__:
        file_name = site_name + '_source.html'
        if not os.path.isfile(file_name):
            print('file save: ', file_name)
            with open(file_name, 'w', encoding='utf-8') as f:
                f.write(soup.prettify())
       
    # 데이터를 저장할 데이터베이스를 생성한다. 
    # bot_id는 moabogey_id에서 가져온 값이다.
    db_name = subject_name + '_on_' + site_name 
    my_db = moabogey.Dbase(db_name, bot_id)
            
    post_json = ''
    # 정보가 저장되어 있는 json파일을 수집한다.
    for post in soup.find_all('script', {'type': 'text/javascript'}):
        if post.text.find('window._sharedData = {') != -1:
            post_json = post.text.replace('window._sharedData = ', '').replace(';', '')      
    #print(post_json[:100])
    #print(post_json[len(post_json) -100 :])
    
    json_data = json.loads(post_json)

    # JSON을 분석하기 위해서 JSON DUMP를 파일로 저장한다.
    if __debug__:
        json_dump = json.dumps(json_data, indent=4)
        file_name = site_name + '_json_source.json'
        if not os.path.isfile(file_name):
            print('file save: ', file_name)
            with open('json_dump.json', 'w') as f:
                f.write(json_dump)

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

                if __debug__:
                    # 디버그를 위해서 수집한 데이터를 출력한다.
                    temp_data = db_data.copy()
                    temp_data['desc'] = temp_data['desc'][:20] + '...'
                    print('📀 수집한 json data: ')
                    print(json.dumps(temp_data, indent=4, ensure_ascii=False, default=str))

                # 수집한 데이터를 데이터베이스에 전송한다.
                my_db.insertTable(db_data)

    # 데이터 베이스에 저장된 데이터를 디스플레이 한다.
    if __debug__:
        my_db.displayHTML()

    # 데이터 베이스를 닫는다.
    my_db.close()

