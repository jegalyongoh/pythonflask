﻿from flask import Flask, render_template, request, json, redirect, url_for, session
import pymysql
import datetime

app = Flask(__name__)
conn = pymysql.connect(host='127.0.0.1', port=3307, user="root", passwd='a1234', db="bucketlist", charset='utf8')
cur = conn.cursor()
app.secret_key = 'any random string'

@app.route('/loaddate', methods=['GET', 'POST'])
def loaddate():
    i=0
    date = datetime.datetime.now()
    time = []
    while i <= 23:
        realtime = "%s-%s-%s %d:00:00" % (date.year, date.month, date.day, i)
        nexttime = "%s-%s-%s %d:59:59" % (date.year, date.month, date.day, i)
        datequery = "SELECT * FROM tbl_date where user_date >= '%s' and user_date <= '%s'" % (realtime, nexttime)
        alldate=cur.execute(datequery)
        time.append(alldate)
        i+=1
    return json.dumps(["User"] + time)


@app.route('/date', methods=['GET', 'POST'])
def date():
    i = 30
    date = datetime.datetime.now()
    month = []
    while i >= 0:
        startday = date - datetime.timedelta(days=i)
        start = "%s-%s-%s 00:00:00" % (startday.year, startday.month, startday.day)
        end = "%s-%s-%s 23:59:59" % (startday.year, startday.month, startday.day)
        datequery = "SELECT * FROM tbl_date where user_date >= '%s' and user_date <= '%s'"  % (start,end)
        monthdate = cur.execute(datequery)
        month.append(monthdate)
        i -= 1
    return json.dumps(["User"] + month)


@app.route('/admindata', methods=['GET', 'POST'])
def admindata():
    stu = "일반회원"
    adm = "관리자"
    cur.execute('SELECT * FROM user')
    userdata = cur.fetchall()
    userdatadict = []
    for a, b, c in userdata:
        if c == 0:
            c = stu
        else:
            c = adm
        wish_dict = [
            a,
            b,
            c
        ]
        userdatadict.append(wish_dict)
    return json.dumps({'data': userdatadict})


@app.route('/userlog', methods=['GET', 'POST'])
def userlog():
    _query = "SELECT id,DATE_FORMAT(user_date, '%Y년%m월%d일 %h:%i:%s') FROM tbl_date ORDER BY user_date desc;"
    cur.execute(_query)
    _data = cur.fetchall()
    logdata = []
    for a, b in _data:
        wish_dict = [
            a,
            b
        ]
        logdata.append(wish_dict)
    return json.dumps({'data': logdata}, sort_keys=False)


@app.route('/boarddata', methods=['GET', 'POST'])
def boarddata():
    cur.execute('SELECT * FROM board order by board_id DESC')
    boddata = cur.fetchall()
    boarddata = []
    for id_,a, b, c in boddata:
        wish_dict = [
            a,
            c,
            id_
        ]
        boarddata.append(wish_dict)
    return json.dumps({'data': boarddata})


@app.route('/adminboarddata', methods=['GET', 'POST'])
def adminboarddata():
    cur.execute('SELECT * FROM board')
    boddata = cur.fetchall()
    return json.dumps({'data': boddata})


@app.route('/',  methods=['GET', 'POST'])
def main():
    if 'username' in session:
        return redirect(url_for('mainpage'))
    else:
        return render_template('index.html')


@app.route('/joiner', methods=['GET', 'POST'])
def showtest():
    return render_template('join.html')


@app.route('/TEST', methods=['GET', 'POST'])
def helloworld():
    text = request.form['ir1']
    return text + '<br><button onclick="location.href=/student>이동</button>'


@app.route('/student')
def student():
    return render_template('sample.html')


@app.route('/del_user', methods=['POST'])
def deluser():
    _user = request.form['realusername']
    query = "delete from user where user_id='%s'" % _user
    cur.execute(query)
    conn.commit()
    return '<script>alert(\'성공\'); window.history.back();</script>'


@app.route('/updata_user', methods=['GET', 'POST'])
def updata_user():
    _realuser = request.form['realusername']
    _user = request.form['username']
    _pass = request.form['userpass']
    _grade = request.form['userad']
    query = "update user set user_id = '%s' , user_pass = '%s' , user_admin = %s where user_id='%s'" % (_user, _pass, _grade, _realuser)
    cur.execute(query)
    conn.commit()
    return '<script>alert(\'수정 완료\'); window.history.back();</script>'


@app.route('/del_board', methods=['POST'])
def delboard():
    _board = request.form['realboardname']
    query = "delete from board where board_id='%s'" % _board
    cur.execute(query)
    conn.commit()
    return '<script>alert(\'성공\'); window.history.back();</script>'


@app.route('/updata_board', methods=['GET', 'POST'])
def updata_board():
    _realbo = request.form['realboardname']
    _bona = request.form['boardname']
    _bova = request.form['boardvalue']
    _boid = request.form['boardid']
    query = "update board set board_title = '%s' , board_main = '%s' , board_user = '%s' where board_id='%s'" % (_bona, _bova, _boid, _realbo)
    cur.execute(query)
    conn.commit()
    return '<script>alert(\'성공\'); window.history.back();</script>'


@app.route('/crate_board', methods=['GET', 'POST'])
def createboard():
    cur.execute('SELECT board_id from board ORDER BY board_id DESC LIMIT 1')
    max_id = cur.fetchone()
    board_number = int(max_id[0])+1
    _board_title = request.form['boardtitle']
    _board_main = request.form['boardmain']
    _board_id = request.form['boardid']
    query = "insert into board values("+str(board_number)+",%s,%s,%s)"
    cur.execute(query, (_board_title, _board_main, _board_id))
    conn.commit()
    return '<script>alert(\'성공\'); window.history.back();</script>'


@app.route('/admin')
def adminpage():
    if 'username' in session and session['trade'] == 1:
        username = session['username']
        name=[]
        password=[]
        ad=[]
        cur.execute('SELECT * FROM user')
        userdata = cur.fetchall()
        for a, b, c in userdata:
            name.append(a)
            password.append(b)
            ad.append(c)
        return render_template('admin.html', adminname=username, username=name, userpass=password, userad=ad)
    else:
        return '<script>alert("관리자만 사용이 가능합니다."); history.back()</script>'

@app.route('/main')
def mainpage():
    if 'username' in session:
        user_name = session['username']
        user_trade = session['trade']
        return render_template('main.html', name = user_name, trade = user_trade)
    else:
        return '<script>alert("세션이 없습니다."); location.href=\'/\'</script>'


@app.route('/board/<board>')
def board(board):
    cur.execute('SELECT * FROM board where board_id="%s"' % board)
    boarddata = cur.fetchall()
    return render_template('board.html', boarddata=boarddata)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main'))


@app.route('/login', methods=['POST'])
def login():

    _name = request.form['inputid']             # ****
    _pass = request.form['inputpass']

    if _name and _pass:
        query = "SELECT * FROM user where user_id=\'%s\' and user_pass=\'%s\'" % (_name, _pass)
        value = cur.execute(query)
        teee = cur.fetchall()
        if value >= 1:
            print("유저 로그인  : %s" % _name)
            print('로그인 정보 로드완료')
            _trade = teee[0][2]             # ****
            date = datetime.datetime.now()
            nowDatetime = date.strftime('%Y-%m-%d %H:%M:%S')
            insquery="INSERT tbl_date values('%s','%s')" % (_name, nowDatetime)
            cur.execute(insquery)
            session['username'] = _name
            session['trade'] = _trade
            conn.commit()
            print(nowDatetime)
            return redirect(url_for('mainpage'))
        else:
            print('로그인 실패')
            return '<script>alert("로그인 실패"); location.href=\'/\'</script>'
    else:
        return '<script>alert("아이디와 비밀번호 둘다 입력해주세요"); location.href=\'/\'</script>'


@app.route('/join', methods=['POST'])
def join():
    _join_id = request.form['joinid']
    _join_pass = request.form['joinpass']
    _join_pass_2 = request.form['joinpass_2']
    joinckquery = "SELECT * FROM user where user_id=\'%s\'" % _join_id
    joinck = cur.execute(joinckquery)
    if _join_id and _join_pass:
        if _join_pass == _join_pass_2:
            if joinck:
                return '<script>alert("중복된 아이디입니다"); location.href="/joiner"</script>'
            else:
                i = 0
                boolean = True
                while i < len(_join_pass) - 2:
                    if _join_pass[i] == _join_pass[i + 1] == _join_pass[i + 2]:
                        boolean = False
                        break
                    else:
                        i += 1
                if boolean:
                    joinquery = "insert user values(%s,%s,'0')"
                    cur.execute(joinquery, (_join_id, _join_pass))
                    conn.commit()
                    return '<script>alert("성공"); location.href="/" </script>'
                else:
                    return '<script>alert("비밀번호는 연속으로 3자리이상 중복될수없습니다"); location.href="/joiner" </script>'
        else:
            return '<script>alert("비밀번호가 서로 맞지않습니다 다시입력해주세요"); location.href="/joiner" </script>'
    else:
        return '<script>alert("아이디와 비밀번호 둘다 입력해주세요"); location.href="/joiner" </script>'
@app.route('/angular')
def angular():
    return render_template('angular.html')

if __name__ == "__main__":
    app.run(debug=True)
    