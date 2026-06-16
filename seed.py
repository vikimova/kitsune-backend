"""
seed.py — заполнение базы данных без интернета.
Запуск: py seed.py
"""
from app import app
from models import db, User, Anime, Genre, StreamLink, ScheduleEntry

ANIME_DATA = [
    {
        'mal_id': 11061, 'title': 'Атака Титанов', 'title_orig': '進撃の巨人',
        'status': 'finished', 'year': 2013, 'episodes': 25, 'studio': 'Wit Studio',
        'rating': 9.0, 'members': 3500000, 'duration': 24,
        'image_url': 'https://cdn.myanimelist.net/images/anime/10/47347l.jpg',
        'description': 'Человечество живёт за огромными стенами, защищающими от титанов. Когда стена рушится, молодой Эрен Йегер клянётся уничтожить всех титанов.',
        'genres': ['Action', 'Drama', 'Fantasy'],
        'streams': [('AniLibria', 'https://anilibria.tv', 'Рус. озвучка'), ('Netflix', 'https://netflix.com', 'Рус. субтитры')],
        'schedule': ('Пн', '18:00', 'Сер. 5'),
    },
    {
        'mal_id': 16498, 'title': 'Клинок, рассекающий демонов', 'title_orig': '鬼滅の刃',
        'status': 'ongoing', 'year': 2019, 'episodes': 26, 'studio': 'Ufotable',
        'rating': 8.7, 'members': 2900000, 'duration': 24,
        'image_url': 'https://cdn.myanimelist.net/images/anime/1286/99889l.jpg',
        'description': 'Тандзиро Камадо становится истребителем демонов, чтобы спасти сестру и отомстить за семью.',
        'genres': ['Action', 'Fantasy', 'Historical'],
        'streams': [('AniLibria', 'https://anilibria.tv', 'Рус. озвучка')],
        'schedule': ('Чт', '17:30', 'Сер. 8'),
    },
    {
        'mal_id': 31964, 'title': 'Моя геройская академия', 'title_orig': '僕のヒーローアカデミア',
        'status': 'ongoing', 'year': 2016, 'episodes': 113, 'studio': 'BONES',
        'rating': 8.2, 'members': 2100000, 'duration': 23,
        'image_url': 'https://cdn.myanimelist.net/images/anime/10/78745l.jpg',
        'description': 'В мире сверхспособностей Изуку Мидория — единственный без силы. Встреча с величайшим героем меняет всё.',
        'genres': ['Action', 'Comedy', 'School'],
        'streams': [('AniLibria', 'https://anilibria.tv', 'Рус. озвучка'), ('Crunchyroll', 'https://crunchyroll.com', 'Субтитры')],
        'schedule': ('Чт', '23:00', 'Сер. 5'),
    },
    {
        'mal_id': 1535, 'title': 'Тетрадь смерти', 'title_orig': 'デスノート',
        'status': 'finished', 'year': 2006, 'episodes': 37, 'studio': 'Madhouse',
        'rating': 9.0, 'members': 3800000, 'duration': 23,
        'image_url': 'https://cdn.myanimelist.net/images/anime/9/9453l.jpg',
        'description': 'Лайт Ягами находит тетрадь, убивающую любого чьё имя написано в ней, и решает создать идеальный мир без преступников.',
        'genres': ['Mystery', 'Psychological', 'Thriller'],
        'streams': [('Netflix', 'https://netflix.com', 'Рус. озвучка')],
        'schedule': None,
    },
    {
        'mal_id': 5114, 'title': 'Стальной алхимик: Братство', 'title_orig': '鋼の錬金術師',
        'status': 'finished', 'year': 2009, 'episodes': 64, 'studio': 'BONES',
        'rating': 9.1, 'members': 3300000, 'duration': 24,
        'image_url': 'https://cdn.myanimelist.net/images/anime/1223/96541l.jpg',
        'description': 'Братья Элрик ищут Философский камень, чтобы вернуть тела, потерянные при запретном ритуале.',
        'genres': ['Action', 'Adventure', 'Drama', 'Fantasy'],
        'streams': [('AniLibria', 'https://anilibria.tv', 'Рус. озвучка')],
        'schedule': ('Пт', '19:00', 'Спецвыпуск'),
    },
    {
        'mal_id': 136430, 'title': 'Магическая битва', 'title_orig': '呪術廻戦',
        'status': 'ongoing', 'year': 2020, 'episodes': 24, 'studio': 'MAPPA',
        'rating': 8.6, 'members': 2200000, 'duration': 24,
        'image_url': 'https://cdn.myanimelist.net/images/anime/1171/109222l.jpg',
        'description': 'Юдзи Итадори поглощает палец проклятого духа и вступает в мир экзорцистов.',
        'genres': ['Action', 'Fantasy', 'School'],
        'streams': [('Crunchyroll', 'https://crunchyroll.com', 'Субтитры'), ('AniLibria', 'https://anilibria.tv', 'Рус. озвучка')],
        'schedule': ('Ср', '20:00', 'Сер. 12'),
    },
    {
        'mal_id': 9253, 'title': 'Врата Штейна', 'title_orig': 'Steins;Gate',
        'status': 'finished', 'year': 2011, 'episodes': 24, 'studio': 'White Fox',
        'rating': 9.1, 'members': 2400000, 'duration': 24,
        'image_url': 'https://cdn.myanimelist.net/images/anime/5/73199l.jpg',
        'description': 'Хакер-учёный случайно изобретает машину времени и начинает менять прошлое, не подозревая о последствиях.',
        'genres': ['Drama', 'Sci-Fi', 'Thriller'],
        'streams': [('AniLibria', 'https://anilibria.tv', 'Рус. озвучка')],
        'schedule': ('Сб', '22:00', 'Сер. 10'),
    },
    {
        'mal_id': 22319, 'title': 'Токийский гуль', 'title_orig': '東京喰種',
        'status': 'finished', 'year': 2014, 'episodes': 12, 'studio': 'Pierrot',
        'rating': 7.9, 'members': 1900000, 'duration': 24,
        'image_url': 'https://cdn.myanimelist.net/images/anime/5/64449l.jpg',
        'description': 'Кэн Канэки становится полугулем и вынужден жить между двумя мирами — людей и монстров.',
        'genres': ['Action', 'Horror', 'Mystery'],
        'streams': [('Netflix', 'https://netflix.com', 'Рус. субтитры')],
        'schedule': ('Вс', '16:00', 'Сер. 13'),
    },
    {
        'mal_id': 38000, 'title': 'Сага о Винланде', 'title_orig': 'Vinland Saga',
        'status': 'finished', 'year': 2019, 'episodes': 24, 'studio': 'Wit Studio',
        'rating': 8.7, 'members': 1200000, 'duration': 24,
        'image_url': 'https://cdn.myanimelist.net/images/anime/1500/103005l.jpg',
        'description': 'Молодой викинг Торфинн жаждет мести за убийство отца в эпоху великих завоеваний.',
        'genres': ['Action', 'Adventure', 'Drama', 'Historical'],
        'streams': [('AniLibria', 'https://anilibria.tv', 'Рус. озвучка')],
        'schedule': ('Сб', '19:00', 'Сер. 24'),
    },
    {
        'mal_id': 40748, 'title': 'Доктор Стоун', 'title_orig': 'Dr. STONE',
        'status': 'finished', 'year': 2019, 'episodes': 24, 'studio': 'TMS Entertainment',
        'rating': 8.2, 'members': 1100000, 'duration': 24,
        'image_url': 'https://cdn.myanimelist.net/images/anime/1613/102576l.jpg',
        'description': 'Гений-учёный возрождает цивилизацию с нуля после того как всё человечество превратилось в камень.',
        'genres': ['Adventure', 'Comedy', 'Sci-Fi'],
        'streams': [('Crunchyroll', 'https://crunchyroll.com', 'Субтитры')],
        'schedule': ('Пн', '21:00', 'Сер. 9'),
    },
    {
        'mal_id': 21, 'title': 'Ван-Пис', 'title_orig': 'One Piece',
        'status': 'ongoing', 'year': 1999, 'episodes': 1000, 'studio': 'Toei Animation',
        'rating': 8.7, 'members': 2800000, 'duration': 23,
        'image_url': 'https://cdn.myanimelist.net/images/anime/6/73245l.jpg',
        'description': 'Монки Д. Луффи мечтает стать Королём пиратов и найти легендарное сокровище Ван-Пис.',
        'genres': ['Action', 'Adventure', 'Comedy', 'Fantasy'],
        'streams': [('Crunchyroll', 'https://crunchyroll.com', 'Субтитры')],
        'schedule': ('Вт', '17:30', 'Сер. 1104'),
    },
    {
        'mal_id': 4181, 'title': 'Охотник × Охотник', 'title_orig': 'Hunter x Hunter',
        'status': 'finished', 'year': 2011, 'episodes': 148, 'studio': 'Madhouse',
        'rating': 9.0, 'members': 2600000, 'duration': 23,
        'image_url': 'https://cdn.myanimelist.net/images/anime/1337/99013l.jpg',
        'description': 'Гон Фрикс мечтает найти своего отца — легендарного Охотника. Чтобы найти его, мальчик решает сам стать Охотником.',
        'genres': ['Action', 'Adventure', 'Fantasy'],
        'streams': [('Netflix', 'https://netflix.com', 'Рус. субтитры')],
        'schedule': None,
    },
]

def seed():
    with app.app_context():
        print('🗄️  Создаём таблицы...')
        db.create_all()

        # Администратор
        if not User.query.filter_by(username='admin').first():
            print('👤  Создаём администратора...')
            admin = User(username='admin', email='admin@kitsune.ru', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print('   admin / admin123')
        else:
            print('👤  Администратор уже существует.')

        # Аниме
        added = 0
        for item in ANIME_DATA:
            if Anime.query.filter_by(mal_id=item['mal_id']).first():
                continue

            anime = Anime(
                mal_id      = item['mal_id'],
                title       = item['title'],
                title_orig  = item['title_orig'],
                description = item['description'],
                image_url   = item['image_url'],
                status      = item['status'],
                year        = item['year'],
                episodes    = item['episodes'],
                duration    = item['duration'],
                studio      = item['studio'],
                rating      = item['rating'],
                members     = item['members'],
            )

            # Жанры
            for g_name in item['genres']:
                genre = Genre.query.filter_by(name=g_name).first()
                if not genre:
                    genre = Genre(name=g_name)
                    db.session.add(genre)
                    db.session.flush()
                anime.genres.append(genre)

            # Стриминги
            for platform, url, lang in item['streams']:
                anime.streams.append(StreamLink(platform=platform, url=url, lang=lang))

            # Расписание
            if item['schedule']:
                day, time, ep = item['schedule']
                anime.schedule.append(ScheduleEntry(day_of_week=day, air_time=time, episode=ep))

            db.session.add(anime)
            added += 1

        db.session.commit()
        print(f'🎌  Добавлено аниме: {added}')
        print()
        print('✅  Готово:')
        print(f'   👤 Пользователей: {User.query.count()}')
        print(f'   🎌 Аниме:         {Anime.query.count()}')
        print(f'   🏷️  Жанров:        {Genre.query.count()}')
        print()
        print('🚀  Запуск: py app.py')
        print('🔑  Логин:  admin / admin123')

if __name__ == '__main__':
    seed()
