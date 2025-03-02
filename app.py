import math
import datetime # 파이썬에 기본적으로 내장되어있는 패키지
from flask_pymongo import PyMongo
from flask import Flask, render_template, request, redirect

app = Flask(__name__) # Flask 변수 app

# 몽고db랑 연결
# 변수 app에 config 안에 MONGI_URI라는 키에다가 값을 입력
# 몽고디비 접속 주소
app.config['MONGO_URI'] = 'mongodb://localhost:27017/local'

mongo = PyMongo(app)

@app.route('/write', methods=["POST"]) # 달라고만 할 수 있는 요청 주소 / methods 안에 POST 추가
def write(): # 함수 write
    # 주소로 방명록을 쓰는 거니까 이름, 내용을 써서 올린다.
    # 이름이랑 내용을 받아서 데이터베이스에다가 저장해준다.
    # 새로운 패키지 설정
        # 기존에 사용하던 mongodb 라이브러리 외에
        # flask에서 몽고db를 유용하게 사용할 수 있는 패키지 설치
        # 터미널에다가 입력 pip install flask-pymongo
        # 패키지를 설치했으나 VSCode에서 패키지를 못찾는 에러가 표시된다면
        # 우측 하단에 Python의 버전이 쓰여져있는 부분을 클릭하여
        # Select Interpreter라고 나와있는 부분에 Python을 선택하면 된다.
    # 입력 받기
        # request 요청. 웹사이트를 이용하는 사용자로부터 어떤 요청을 받을 때 요청에 대한 정보를 가지고 있는 변수
        # redirect. 요청 받은 값을 잘 처리한 다음에 이동시킨다.
            # 페이지를 보여주는 것이 아니라 글을 쓰고 나면 다시 페이지를 보여줘야되니 redirect 주소를 보여준다.
    # data 저장
        # POST 이용해서 data 전달받는다
    name = request.form.get('name') # request가 사용자로부터 전달된 data
    content = request.form.get('content')

    # 몽고db에 wedding이라는 collection 사용
    # name 과 content를 받아서 json이라는 딕셔너리 형태로 넣는다.
    # post로 전달된 요청 안에 name값과 content값을 변수로 받아서
        # 그 값을 mongo.db wedding collection 안에다가 추가한다.
    mongo.db['wedding'].insert_one( {
        "name" : name,
        "content" : content
    })
    # mongo db에 저장

    return redirect('/') # return 빈 문자열로 한다

# 모바일 청첩장을 만들기때문에 페이지는 하나밖에 없다.
@app.route('/')
# def : define 약자. 함수 만들 때 사용 / 함수 이름
def index(): # : 사용하는 건 조건문과 반복문
    # 오늘 날짜 / now 라는 변수에 현재 날짜와 시간 정보가 들어간다.
    now = datetime.datetime.now()

    # 결혼식 날짜 / 년도 / 월 / 날짜 / 시간 / 분 / 초
    wedding = datetime.datetime(2025, 9, 20, 0, 0, 0)

    # 며칠 차이가 나는지 알고 싶다.
    # 차이가 나는 값을 날짜로 표시한다.
    diff = (wedding - now).days

    #pagination 생성 (페이지 만들기)
        # 방명록을 보여줘야되니 몽고db에서 data를 가지고 온다.
        # find 함수. 모든 방명록을 가지고 온다.
        # 페이지네이션을 위해서는 limit과 skip을 활용해야 한다.
            # limit 함수. 가지고 오는 개수를 제한
            # 1페이지 3개, 2페이지 3개. 건너뛰는 것도 필요하다.
                # skip 함수 같이 사용함
                    # 한 페이지에 보여주고 싶은 data 갯수와 페이지 번호에 따라서 결정되는 값
        # request 사용자가 요청을 다뤄는 변수. 이 안에 args라는 값이 있다.
            # 페이지가 몇 페이지인지를 쓰면서 가지 않기 떄문에 값을 꺼내올 때 없을 수도 있다.
            # 없으면 1페이지를 보여준다.
            # 사용자가 요청한 주소에 페이지라는 data가 있으면 가지고 오고 없으면 1을 사용
        # 1, 2, 3 이렇게 입력을 했더라도 Query String 주소에서 넘어오는 data는 기본적으로 문자열이다.
            # 페이지네이션을 위해 쿼리로 페이지 번호를 받을 경우 전달 받은 해당 값은
                # 문자열이기때문에 숫자형으로 변환해야 한다.
    page = int(request.args.get('page', 1))

    limit = 5 # 고정으로 3개만 가지고 온다.

    # 페이지 값을 이용해서 만든다.
        # 1 페이지일 때는 skip(0)
        # 2 페이지일 때는 skip(3)
        # 3 페이지일 때는 skip(6)
        # 페이지 숫자보다 하나 작은 수만큼 skip을 해야 한다.
        # 그런데 3개씩 보여주니까 이 값을 곱해야 한다.
        # 3페이지 요청이 왔을 때 총 몇 개를 건너뛰고 들어갈 수 있다.
    skip = (page - 1) * limit

    # 전체 data 개수
    # count_documents
        # find는 어떤 애를 찾을 건지를 넣어도 되고 안 넣어도 된다
        # count_documents 는 안 넣어도 되는데 빈 값을 넣어줘야 된다
        # 모든 문서에 대해서 개수를 세려면 빈 딕셔너리 변수를 넣어줘야 한다
    count = mongo.db['wedding'].count_documents({})

    # 전체 페이지 번호
        # 한 페이지에 3개씩 나온다
        # count가 3이면 page는 1이 된다
        # count가 6이면 page는 2가 된다
        # count가 5이면 page는 2가 된다
            # 나눈 값은 1이 나온다. 버림이 된다.
            # 필요한 건 올림이다.
            # 나머지가 있다면 필요한건 page가 필요하다
    max_page = math.ceil(count / limit) # ceil을 이용하여 올림한다

    # page = range(1, 10) # 1부터 9까지
    pages = range(1, max_page + 1) # 1부터 내가 원하는 페이지까지

    guestbooks = mongo.db['wedding'].find().limit(limit).skip(skip)

    # 페이지값 입력
        # Query String 이용
            # 브라우저에서 주소에 ?와 어떤 값이 들어있는 주소를 본 적이 있을 것이다.
                # https://search.naver.com/search.naver?ie=UTF-8&sm=whl_hty&query=%ED%8C%A8%EC%8A%A4%ED%8A%B8%EC%BA%A0%ED%8D%BC%EC%8A%A4
                # 이 주소에 접속할 때 이런 data를 전달하고 싶다라는 뜻


    # 차이 나는 날짜를 전달해준다.
    # 왼쪽 diff : index.html에서 사용할 값
    # 오른쪽 diff : 실제로 사용된 파이썬 안에서 만들어진 값
    return render_template(
        '/index.html',
        diff=diff,
        guestbooks=guestbooks,
        pages=pages
    )

if __name__ == '__main__':
    app.run()
