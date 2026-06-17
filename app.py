import sys
import os

# Добавляем текущую папку в путь поиска модулей
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate

from config import Config
from models import db

# Импортируем blueprints — пробуем оба варианта (с папкой routes и без)
try:
    from routes.auth import auth_bp
    from routes.anime import anime_bp
    from routes.collections import collections_bp
    from routes.ratings import ratings_bp
except ModuleNotFoundError:
    from auth import auth_bp
    from anime import anime_bp
    from collections_routes import collections_bp
    from ratings import ratings_bp


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    Migrate(app, db)
    JWTManager(app)
    CORS(app, origins=app.config['CORS_ORIGINS'])

    app.register_blueprint(auth_bp)
    app.register_blueprint(anime_bp)
    app.register_blueprint(collections_bp)
    app.register_blueprint(ratings_bp)

    @app.route('/api')
    def index():
        return jsonify({'name': 'KitsunePlay API', 'version': '1.0.0', 'status': 'ok'})

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Не найдено'}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({'error': 'Ошибка сервера'}), 500

    with app.app_context():
        db.create_all()
        _seed_if_empty()

    return app


def _seed_if_empty():
    from models import User, Anime, Genre

    if User.query.count() > 0:
        return

    print('🌱 Первый запуск — заполняем базу данных...')

    admin = User(username='admin', email='admin@kitsune.ru', role='admin')
    admin.set_password('admin123')
    db.session.add(admin)

    ANIME_DATA = [
        {'mal_id':11061,'title':'Атака Титанов','title_orig':'進撃の巨人','status':'finished','year':2013,'episodes':25,'studio':'Wit Studio','rating':9.0,'members':3500000,'description':'Столетиями человечество живёт за гигантскими стенами. Когда стена рушится, Эрен Йегер клянётся уничтожить всех титанов.','image_url':'https://cdn.myanimelist.net/images/anime/10/47347l.jpg','genres':['Action','Drama','Fantasy']},
        {'mal_id':16498,'title':'Клинок, рассекающий демонов','title_orig':'鬼滅の刃','status':'ongoing','year':2019,'episodes':26,'studio':'Ufotable','rating':8.7,'members':2900000,'description':'Тандзиро Камадо становится истребителем демонов, чтобы спасти сестру.','image_url':'https://cdn.myanimelist.net/images/anime/1286/99889l.jpg','genres':['Action','Fantasy','Historical']},
        {'mal_id':31964,'title':'Моя геройская академия','title_orig':'僕のヒーローアカデミア','status':'ongoing','year':2016,'episodes':113,'studio':'BONES','rating':8.2,'members':2100000,'description':'В мире сверхспособностей Изуку Мидория — единственный без силы.','image_url':'https://cdn.myanimelist.net/images/anime/10/78745l.jpg','genres':['Action','Comedy','School']},
        {'mal_id':1535,'title':'Тетрадь смерти','title_orig':'デスノート','status':'finished','year':2006,'episodes':37,'studio':'Madhouse','rating':9.0,'members':3800000,'description':'Лайт Ягами находит тетрадь убивающую любого чьё имя написано в ней.','image_url':'https://cdn.myanimelist.net/images/anime/9/9453l.jpg','genres':['Mystery','Psychological','Thriller']},
        {'mal_id':5114,'title':'Стальной алхимик: Братство','title_orig':'鋼の錬金術師','status':'finished','year':2009,'episodes':64,'studio':'BONES','rating':9.1,'members':3300000,'description':'Братья Элрик ищут Философский камень чтобы вернуть потерянные тела.','image_url':'https://cdn.myanimelist.net/images/anime/1223/96541l.jpg','genres':['Action','Adventure','Drama','Fantasy']},
        {'mal_id':136430,'title':'Магическая битва','title_orig':'呪術廻戦','status':'ongoing','year':2020,'episodes':24,'studio':'MAPPA','rating':8.6,'members':2200000,'description':'Юдзи Итадори поглощает палец проклятого духа и вступает в мир экзорцистов.','image_url':'https://cdn.myanimelist.net/images/anime/1171/109222l.jpg','genres':['Action','Fantasy','School']},
        {'mal_id':9253,'title':'Врата Штейна','title_orig':'Steins;Gate','status':'finished','year':2011,'episodes':24,'studio':'White Fox','rating':9.1,'members':2400000,'description':'Хакер-учёный случайно изобретает машину времени.','image_url':'https://cdn.myanimelist.net/images/anime/5/73199l.jpg','genres':['Drama','Sci-Fi','Thriller']},
        {'mal_id':22319,'title':'Токийский гуль','title_orig':'東京喰種','status':'finished','year':2014,'episodes':12,'studio':'Pierrot','rating':7.9,'members':1900000,'description':'Кэн Канэки становится полугулем и живёт между двумя мирами.','image_url':'https://cdn.myanimelist.net/images/anime/5/64449l.jpg','genres':['Action','Horror','Mystery']},
        {'mal_id':38000,'title':'Сага о Винланде','title_orig':'Vinland Saga','status':'finished','year':2019,'episodes':24,'studio':'Wit Studio','rating':8.7,'members':1200000,'description':'Молодой викинг Торфинн жаждет мести за убийство отца.','image_url':'https://cdn.myanimelist.net/images/anime/1500/103005l.jpg','genres':['Action','Adventure','Drama','Historical']},
        {'mal_id':40748,'title':'Доктор Стоун','title_orig':'Dr. STONE','status':'finished','year':2019,'episodes':24,'studio':'TMS Entertainment','rating':8.2,'members':1100000,'description':'Гений-учёный возрождает цивилизацию с нуля.','image_url':'https://cdn.myanimelist.net/images/anime/1613/102576l.jpg','genres':['Adventure','Comedy','Sci-Fi']},
        {'mal_id':21,'title':'Ван-Пис','title_orig':'One Piece','status':'ongoing','year':1999,'episodes':1000,'studio':'Toei Animation','rating':8.7,'members':2800000,'description':'Монки Д. Луффи мечтает стать Королём пиратов.','image_url':'https://cdn.myanimelist.net/images/anime/6/73245l.jpg','genres':['Action','Adventure','Comedy','Fantasy']},
        {'mal_id':4181,'title':'Охотник × Охотник','title_orig':'Hunter x Hunter','status':'finished','year':2011,'episodes':148,'studio':'Madhouse','rating':9.0,'members':2600000,'description':'Гон Фрикс мечтает найти своего отца — легендарного Охотника.','image_url':'https://cdn.myanimelist.net/images/anime/1337/99013l.jpg','genres':['Action','Adventure','Fantasy']},
    ]

    for item in ANIME_DATA:
        anime = Anime(
            mal_id=item['mal_id'], title=item['title'],
            title_orig=item['title_orig'], description=item['description'],
            image_url=item['image_url'], status=item['status'],
            year=item['year'], episodes=item['episodes'],
            studio=item['studio'], rating=item['rating'],
            members=item['members'],
        )
        for g_name in item['genres']:
            genre = Genre.query.filter_by(name=g_name).first()
            if not genre:
                genre = Genre(name=g_name)
                db.session.add(genre)
                db.session.flush()
            anime.genres.append(genre)
        db.session.add(anime)

    db.session.commit()
    print('✅ База данных заполнена!')


app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
