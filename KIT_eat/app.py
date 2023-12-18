from flask import Flask, request, render_template, redirect, session, jsonify, Response
from dotenv import load_dotenv
import os
import sqlite3
import json

load_dotenv(verbose=True)
API_KEY = os.getenv('API_KEY')

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.secret_key = os.getenv('LOGIN_SECRET_KEY')

# 메인 서비스 페이지
@app.route('/')
def hello():
    API_KEY = os.getenv('API_KEY')
    return render_template('food.html', API_KEY = API_KEY)


# 관리자 로그인 페이지

@app.route('/admin', methods=['GET'])
def admin():
    if 'admin_id' in session:
        return render_template('admin.html', username=session['admin_id'])
    else : 
        return render_template('admin_login.html')

# @app.route('/admin_login', methods=['GET', 'POST'])
# def admin_login():
#     if request.method == 'GET':
#         return render_template('login.html')
#     else:

@app.route('/admin_login', methods=['GET'])
def login():
    return render_template('admin_login.html')

@app.route('/admin_login', methods=['POST'])
def process_login():
    admin_id = request.form['admin_id']
    admin_pw = request.form['admin_pw']

    conn = sqlite3.connect('admin.db')
    c = conn.cursor()
    c.execute('SELECT * FROM member WHERE admin_id=? AND admin_pw=?', (admin_id, admin_pw))
    user = c.fetchone()
    conn.close()

    if user:
        session['admin_id'] = user[0]  # 세션에 사용자 정보 저장
        return redirect('/admin')
    else:
        return render_template('admin_login.html', error='Invalid credentials')
    
@app.route('/logout', methods=['GET'])
def logout():
    session.pop('admin_id', None)
    return redirect('/admin_login')


# 회원가입 DB 함수
def sign_up_to_db(admin_id, admin_pw, nickname):
    conn = sqlite3.connect("admin.db")
    c = conn.cursor()

    # 테이블이 없으면 생성
    c.execute('CREATE TABLE IF NOT EXISTS member (admin_id TEXT, admin_pw TEXT, nickname TEXT)')
    
    # 데이터 삽입
    c.execute('INSERT INTO member VALUES(?, ?, ?)',(admin_id, admin_pw, nickname) )

    conn.commit()
    conn.close()


# 회원가입 및 완료 페이지

@app.route('/sign_up')
def sign_up():
    return render_template('sign_up.html')

@app.route('/signup_complete', methods=['POST'])
def signup_complete():
    admin_id = request.form['admin_id']
    admin_pw = request.form['admin_pw']
    nickname = request.form['nickname']
    sign_up_to_db(admin_id, admin_pw, nickname)  # 저장 함수
    return '관리자 정보가 저장 되었습니다. <br><a href="/admin_login">로그인<a>'

def store_to_db(name, address, category):
    conn = sqlite3.connect("address.db")
    c = conn.cursor()

    # 테이블이 없으면 생성
    c.execute('CREATE TABLE IF NOT EXISTS table_name (name TEXT, address TEXT, category TEXT)')
    
    # 데이터 삽입
    c.execute('INSERT INTO table_name VALUES (?, ?, ?)', (name, address, category))

    conn.commit()
    conn.close()

@app.route('/store', methods=['POST'])
def store():
    name = request.form['name']
    address = request.form['address']
    category = request.form['category']
    store_to_db(name, address, category)  # 저장 함수
    return '식당 정보가 저장 되었습니다. <br><a href="/admin">뒤로가기<a>'

def get_data_from_db():
    conn = sqlite3.connect('address.db')  # DB에 연결
    c = conn.cursor()

    # 모든 데이터 가져오기
    c.execute('SELECT * FROM table_name')
    data = c.fetchall()

    conn.close()

    return data


# 식당 정보 JSON 출력

def get_data_from_db_dict():
    conn = sqlite3.connect('address.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES, isolation_level=None) # DB에 연결
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute('SELECT name, address, category FROM table_name')
    data = c.fetchall()
    
    data_list = [{'name': row[0], 'address': row[1], 'category': row[2]} for row in data]

    conn.close()
    
    json_data = json.dumps({'data': data_list}, ensure_ascii=False).encode('utf-8')
    response = Response(response=json_data, status=200, mimetype="application/json; charset=utf-8")

    return response

# 아래 코드는 식당 정보를 일괄로 갱신 할 때 사용하는 코드입니다.
# def edit_db(name, new_name, new_address):
#     conn = sqlite3.connect('address.db')  # DB에 연결
#     c = conn.cursor()

#     # 데이터 수정
#     c.execute('UPDATE table_name SET name = ?, address = ? WHERE name = ?', (new_name, new_address, name))

#     conn.commit()  # 변경사항 저장
#     conn.close()


# 식당 정보 수정

def edit_name_in_db(old_name, new_name):
    conn = sqlite3.connect('address.db')  # DB에 연결
    c = conn.cursor()

    # 상호명 수정
    c.execute('UPDATE table_name SET name = ? WHERE name = ?', (new_name, old_name))

    conn.commit()  # 변경사항 저장
    conn.close()

def edit_address_in_db(name, new_address):
    conn = sqlite3.connect('address.db')  # DB에 연결
    c = conn.cursor()

    # 주소 수정
    c.execute('UPDATE table_name SET address = ? WHERE name = ?', (new_address, name))

    conn.commit()  # 변경사항 저장
    conn.close()

def edit_category_in_db(name, new_category):
    conn = sqlite3.connect('address.db')  # DB에 연결
    c = conn.cursor()

    # 카테고리 수정
    c.execute('UPDATE table_name SET category = ? WHERE name = ?', (new_category, name))

    conn.commit()  # 변경사항 저장
    conn.close()

def delete_from_db(name):
    conn = sqlite3.connect('address.db')  # DB에 연결
    c = conn.cursor()

    # 데이터 삭제
    c.execute('DELETE FROM table_name WHERE name = ?', (name,))

    conn.commit()  # 변경사항 저장
    conn.close()

# 식당 정보 수정 및 삭제 페이지

@app.route('/data')
def data_page():
    if 'admin_id' in session:
        data = get_data_from_db()
        return render_template('address.html', data=data, username=session['admin_id'])
    else : 
        return render_template('admin_login.html')

# 아래 코드는 식당 정보를 일괄 수정할 수 있는 폼입니다.
# @app.route('/edit', methods=['POST'])
# def edit():
#     name = request.form['name']
#     new_name = request.form['new_name']
#     new_address = request.form['new_address']
#     edit_db(name, new_name ,new_address)  # 수정 함수
#     return 'Data updated.'

@app.route('/edit_name', methods=['POST'])
def edit_name():
    old_name = request.form['old_name']
    new_name = request.form['new_name']
    edit_name_in_db(old_name, new_name)  # 상호명 수정 함수
    return '상호명이 업데이트 되었습니다. <br><a href="/data">뒤로가기<a>'

@app.route('/edit_address', methods=['POST'])
def edit_address():
    name = request.form['name']
    new_address = request.form['new_address']
    edit_address_in_db(name, new_address)  # 주소 수정 함수
    return '주소가 업데이트 되었습니다.<br><a href="/data">뒤로가기<a>'

@app.route('/edit_category', methods=['POST'])
def edit_category():
    name = request.form['name']
    new_category = request.form['new_category']
    edit_category_in_db(name, new_category)  # 카테고리 수정 함수
    return '카테고리가 업데이트 되었습니다.<br><a href="/data">뒤로가기<a>'

@app.route('/delete', methods=['POST'])
def delete():
    name = request.form['name']
    delete_from_db(name)  # 삭제 함수
    return '식당 정보가 삭제되었습니다.<br><a href="/data">뒤로가기<a>'

@app.route('/data_test')
def dt():
    data = get_data_from_db_dict()
    # print(type(data))
    return data

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5100, debug=True)