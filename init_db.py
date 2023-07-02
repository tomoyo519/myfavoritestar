import requests
from bs4 import BeautifulSoup

from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.dbjungle


# DB에 저장할 영화인들을 가져옵니다.
def get_all_stars():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get('https://movie.daum.net/ranking/reservation', headers=headers)

    soup = BeautifulSoup(data.text, 'html.parser')
    anchors = soup.select('ol.list_movieranking strong.tit_item > a')

    stars = []
    for a in anchors:
        if a is not None:
            base_url = 'https://movie.daum.net'
            link = a['href'].replace("/main?", "/crew?")
            url = base_url + link
            params = url.split("?")[1].split("&")
            for param in params:
                key, value = param.split("=")
                if key == "movieId":
                    stars.extend(get_stars(value))
                    break

    return stars


# 영화인 api를 통해 데이터를 가져옵니다
def get_stars(movie_id):
    url = f"https://movie.daum.net/api/movie/{movie_id}/crew"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
    }
    data = requests.get(url, headers=headers)
    movie_info = data.json()
    casts = movie_info.get("casts")
    주연 = 2
    조연 = 3
    return [get_star_info(cast) for cast in casts if cast.get("movieJob", {}).get("id") in [주연, 조연]]


# 영화인 api에서 가져온 데이터를 입맛에 맞게 바꿉니다.
def get_star_info(actor):
    return {
        'name': actor.get("nameKorean"),
        'img_url': actor.get("profileImage"),
        'recent': "",
        'url': f"https://movie.daum.net/person/main?personId={actor.get('personId')}",
        'like': 0
    }


# 출처 url로부터 영화인들의 사진, 이름, 최근작 정보를 가져오고 mystar 콜렉션에 저장합니다.
def insert_star(star):
    db.mystar.insert_one(star)
    print('완료!', star["name"])


# 기존 mystar 콜렉션을 삭제하고, 출처 url들을 가져온 후, 크롤링하여 DB에 저장합니다.
def insert_all():
    db.mystar.drop()  # mystar 콜렉션을 모두 지워줍니다.
    stars = get_all_stars()
    for star in stars:
        insert_star(star)


if __name__ == "__main__":
    ### 실행하기
    insert_all()