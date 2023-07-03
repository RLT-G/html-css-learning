import datetime
from flask import render_template, redirect, request, session
from deep_translator import GoogleTranslator
import requests
from .models import *
from .utils import *


@app.route("/")
def index():
    return render_template('index.html', session=session)


@app.route("/planets")
def planets():
    wiki_wiki = wikipediaapi.Wikipedia('ru')
    page_py = wiki_wiki.page('Солнечная_система')
    data = {
        "t1": page_py.summary.split('Четыре ближайшие к Солнцу планеты')[0],
        "t2": page_py.summary.split('Четыре более удалённые от Солнца')[0].split('на ~0,001 общей массы '
                                                                                 'Солнечной системы.')[1],
        "t3": page_py.summary.split('меньшие планеты-гиганты')[0].split('состоят в основном из силикатов '
                                                                        'и металлов.')[1],
        "t4": 'М' + page_py.summary.split('Шесть планет из восьми')[0].split('газовым гигантам;')[1][2::],
        "t5": page_py.summary.split('Крупнейшими объектами пояса')[0].split('«ледяных гигантов».')[1],
        "t6": page_py.summary.split('В Солнечной системе существуют и другие')[0].split(', поскольку состоит '
                                                                                        'из силикатов и металлов.')[1],
        "t7": page_py.summary.split('Орк и Эрида.')[1]
    }
    return render_template('planets.html', **data)


@app.route("/constellations")
def constellations():
    data = viki_data('Знаки_зодиака')
    data['t2'] = data['t2'][0:-2]
    return render_template('constellations.html', **data)


@app.route("/zodiac-signs")
def zodiac_signs():
    data = viki_data('Знаки_зодиака')
    data['t2'] = data['t2'][0:-1]
    return render_template('zodiac-signs.html', **data)


@app.route("/forum", methods=['POST', 'GET'])
def forum():
    if not session.get("name"):
        return redirect("/aut")
    if request.method == 'GET':
        forum_data = db.session.query(Forum).all()
        list_statey = []
        for i in forum_data:
            a = str(i)[1:-1].split('%, ')
            a[0] = a[0][a[0].index(',') + 1::]
            list_statey.append(a)
        return render_template('forum.html', array=list_statey[::-1])
    elif request.method == 'POST':
        title = request.form['title'] + '%'
        full_text = request.form['fulltext'] + '%'
        name = session.get('name') + '%'
        date = datetime.datetime.now().strftime('%d.%m.%Y %H:%M')
        new_post = Forum(title=title, full_text=full_text, name=name, date=date)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/forum')


@app.route("/feedback", methods=['POST', 'GET'])
def feedback():
    if not session.get("name"):
        return redirect("/aut")
    if request.method == 'GET':
        with open('rating.txt', 'r') as file:
            read_file = file.read()
            try:
                data = str(sum(list(map(int, read_file.split()))) / len(read_file.split()))[:4]
            except ZeroDivisionError:
                print("Rating is null")
                data = ''
        return render_template('feedback.html', data=data)
    elif request.method == 'POST':
        with open('rating.txt', 'r') as f:
            data = str(f.read())
        with open('rating.txt', 'w') as f:
            f.write(data + ' ' + request.form['star'])
        return redirect('/')


@app.route("/aut", methods=['POST', 'GET'])
def aut():
    if request.method == 'GET':
        if session.get('name'):
            return redirect('/')
        return render_template('aut.html')
    elif request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        availability_error = False
        password_error = False
        if not User.query.filter_by(name=name).first():
            availability_error = True
        if not User.query.filter_by(password=password).first():
            password_error = True
        if availability_error or password_error:
            data = {
                'name': name,
                'availability_error': availability_error,
                'password': password,
                'error_password': password_error,
            }
            return render_template('aut.html', **data)
        if User.query.filter_by(name=name).first() and User.query.filter_by(password=password).first():
            session["name"] = name
            db.session.commit()
            return redirect('/')


@app.route("/reg", methods=['POST', 'GET'])
def reg():
    if request.method == 'GET':
        if session.get('name'):
            return redirect('/')
        return render_template('reg.html')
    elif request.method == 'POST':
        name = request.form['name']
        gender = request.form['gender']
        dob = request.form['dob']
        password1 = request.form['password1']
        password2 = request.form['password2']
        about = request.form['about']
        country = request.form['country']
        number_phone = request.form['number_phone']
        password_error = False
        name_error = False
        availability_error = False
        for letter in name:
            if not (letter.isalnum() or letter == '_'):
                name_error = True
        if password1 != password2:
            password_error = True
        if User.query.filter_by(name=name).first():
            availability_error = True
        if password_error or name_error or availability_error:
            data = {
                'about': about,
                'country': country,
                'name': name,
                'number_phone': number_phone,
                'error_name': name_error,
                'gender': gender,
                'dob': dob,
                'password1': password1,
                'error_password': password_error,
                'availability_error': availability_error
            }
            return render_template('reg.html', **data)
        else:
            f = request.files['file']
            f.save(f'app/static/user_{name}.png')
            new_user = User(name=name, gender=gender, password=password1,
                            data=dob, number_phone=number_phone, about=about, country=country, image=None)
            db.session.add(new_user)
            session["name"] = name
            db.session.commit()
            return redirect("/")


@app.route("/out", methods=['POST', 'GET'])
def out():
    if not session.get("name"):
        return redirect('/aut')
    if request.method == 'GET':
        return render_template('out.html')
    elif request.method == 'POST':
        button_value = request.form['button']
        if button_value == '1':
            session["name"] = None
        return redirect('/')


@app.route("/account", methods=['GET'])
def account():
    if request.method == 'GET':
        if not session.get("name"):
            return redirect("/aut")
        else:
            inf_db = db.session.query(User).filter(User.name == session['name']).first()
            inf_db = str(inf_db)[1:-1].split(', ')
            user_profile = {
                'name': inf_db[1],
                'gender': inf_db[2],
                'date': inf_db[4],
                'number_phone': inf_db[5],
                'about': inf_db[6],
                'country': inf_db[7],
                'data': f'user_{inf_db[1]}.png'
            }
        return render_template('account.html', **user_profile)


@app.route("/zodiac-signs/horoscope", methods=['POST', 'GET'])
def horoscope():
    if request.method == 'GET':
        return render_template('zodiac-signs/horoscope.html')
    elif request.method == 'POST':
        signs = request.form['signs']
        try:
            response = requests.get(f'https://ohmanda.com/api/horoscope/{signs.lower()}').json()
            data = GoogleTranslator(source='auto', target='ru').translate(response['horoscope'])
            sign = GoogleTranslator(source='auto', target='ru').translate(response['sign'])
        except ValueError:
            data = ''
            sign = ''
        if sign == 'рак': sign = 'Рак'
        return render_template('zodiac-signs/horoscope.html', data=data, sign=sign)


@app.route('/planets/mercury')
def mercury():
    data = viki_data('Меркурий')
    data['t2'] = data['t2'][0:-5]
    return render_template('planets/mercury.html', **data)


@app.route('/planets/venera')
def venera():
    data = viki_data('Венера')
    data['t2'] = data['t2'][0:-6]
    return render_template('planets/venera.html', **data)


@app.route('/planets/earth')
def earth():
    data = viki_data('Земля')
    del data['t2'][-8]
    data['t2'] = data['t2'][0:-4]
    return render_template('planets/earth.html', **data)


@app.route('/planets/mars')
def mars():
    data = viki_data('Марс')
    data['t2'] = data['t2'][0:-2]
    return render_template('planets/mars.html', **data)


@app.route('/planets/jupiter')
def jupiter():
    data = viki_data('Юпитер')
    data['t2'] = data['t2'][0:-3]
    return render_template('planets/jupiter.html', **data)


@app.route('/planets/saturn')
def saturn():
    data = viki_data('Сатурн')
    data['t2'] = data['t2'][0:-3]
    return render_template('planets/saturn.html', **data)


@app.route('/planets/uran')
def uran():
    data = viki_data('Уран_(планета)')
    data['t2'] = data['t2'][0:-3]
    return render_template('planets/uran.html', **data)


@app.route('/planets/neptune')
def neptune():
    data = viki_data('Нептун')
    data['t2'] = data['t2'][0:-4]
    return render_template('planets/neptune.html', **data)


@app.route('/planets/pluto')
def pluto():
    data = viki_data('Плутон')
    data['t2'] = data['t2'][0:-4]
    return render_template('planets/pluto.html', **data)


@app.route('/zodiac-signs/aries')
def aries():
    data = viki_data('Овен_(знак_зодиака)')
    data['t2'] = data['t2'][0:-2]
    return render_template('zodiac-signs/aries.html', **data)


@app.route('/zodiac-signs/taurus')
def taurus():
    data = viki_data('Телец_(знак_зодиака)')
    data['t2'] = data['t2'][0:-1]
    return render_template('zodiac-signs/taurus.html', **data)


@app.route('/zodiac-signs/twins')
def twins():
    data = viki_data('Близнецы_(знак_зодиака)')
    data['t2'] = data['t2'][0:-2]
    return render_template('zodiac-signs/twins.html', **data)


@app.route('/zodiac-signs/cancer')
def cancer():
    data = viki_data('Рак_(знак_зодиака)')
    data['t2'] = data['t2'][0:-2]
    return render_template('zodiac-signs/cancer.html', **data)


@app.route('/zodiac-signs/lion')
def lion():
    data = viki_data('Лев_(знак_зодиака)')
    data['t2'] = data['t2'][0:-2]
    return render_template('zodiac-signs/lion.html', **data)


@app.route('/zodiac-signs/virgo')
def virgo():
    data = viki_data('Дева_(знак_зодиака)')
    data['t2'] = data['t2'][0:-2]
    return render_template('zodiac-signs/virgo.html', **data)


@app.route('/zodiac-signs/libra')
def libra():
    data = viki_data('Весы_(знак_зодиака)')
    data['t2'] = data['t2'][0:-2]
    return render_template('zodiac-signs/libra.html', **data)


@app.route('/zodiac-signs/scorpion')
def scorpion():
    data = viki_data('Скорпион_(знак_зодиака)')
    data['t2'] = data['t2'][0:-2]
    return render_template('zodiac-signs/scorpion.html', **data)


@app.route('/zodiac-signs/sagittarius')
def sagittarius():
    data = viki_data('Стрелец_(знак_зодиака)')
    data['t2'] = data['t2'][0:-2]
    return render_template('zodiac-signs/sagittarius.html', **data)


@app.route('/zodiac-signs/capricorn')
def capricorn():
    data = viki_data('Козерог_(знак_зодиака)')
    data['t2'] = data['t2'][0:-2]
    return render_template('zodiac-signs/capricorn.html', **data)


@app.route('/zodiac-signs/aquarius')
def aquarius():
    data = viki_data('Водолей_(знак_зодиака)')
    data['t2'] = data['t2'][0:-2]
    return render_template('zodiac-signs/aquarius.html', **data)


@app.route('/zodiac-signs/pisces')
def pisces():
    data = viki_data('Рыбы_(знак_зодиака)')
    data['t2'] = data['t2'][0:-2]
    return render_template('zodiac-signs/pisces.html', **data)


@app.route('/constellations/betelgeuse')
def betelgeuse():
    data = viki_data('Бетельгейзе')
    data['t2'] = data['t2'][0:-5]
    return render_template('constellations/betelgeuse.html', **data)


@app.route('/constellations/polar-star')
def polar_star():
    data = viki_data('Полярная_звезда')
    data['t2'] = data['t2'][0:-3]
    return render_template('constellations/polar-star.html', **data)


@app.route('/constellations/big-dipper')
def big_dipper():
    data = viki_data('Большая_Медведица')
    data['t2'] = data['t2'][0:-4]
    return render_template('constellations/big-dipper.html', **data)


@app.route('/constellations/orion')
def orion():
    data = viki_data('Орион_(созвездие)')
    data['t2'] = data['t2'][0:-3]
    return render_template('constellations/orion.html', **data)


@app.route('/constellations/cassiopeia')
def cassiopeia():
    data = viki_data('Кассиопея_(созвездие)')
    data['t2'] = data['t2'][0:-3]
    return render_template('constellations/cassiopeia.html', **data)


@app.route('/constellations/zodiac-constellations')
def zodiac_constellations():
    data = viki_data('Зодиакальные_созвездия')
    data['t2'] = data['t2'][0:-2]
    return render_template('constellations/zodiac-constellations.html', **data)


@app.route('/constellations/vega')
def vega():
    data = viki_data('Вега')
    data['t2'] = data['t2'][0:-3]
    return render_template('constellations/vega.html', **data)