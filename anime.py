from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_
from models import db, Anime, Genre, StreamLink, ScheduleEntry, User

anime_bp = Blueprint('anime', __name__, url_prefix='/api/anime')


def bad(msg, code=400):
    return jsonify({'error': msg}), code


def require_admin():
    """Проверяет что текущий пользователь — администратор."""
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user or user.role != 'admin':
        return None, (jsonify({'error': 'Нет прав'}), 403)
    return user, None


# ── GET /api/anime ───────────────────────────────
# Параметры: page, per_page, genre, status, year, studio,
#            min_rating, sort, q (поиск)
@anime_bp.route('', methods=['GET'])
def get_anime_list():
    q          = request.args.get('q', '').strip()
    genre      = request.args.get('genre', '')
    status     = request.args.get('status', '')
    year       = request.args.get('year', type=int)
    studio     = request.args.get('studio', '')
    min_rating = request.args.get('min_rating', type=float)
    sort       = request.args.get('sort', 'rating')       # rating|popular|year|name
    page       = request.args.get('page', 1, type=int)
    per_page   = min(request.args.get('per_page', 24, type=int), 100)

    query = Anime.query.filter_by(is_published=True)

    # Текстовый поиск по названию и описанию
    if q:
        like = f'%{q}%'
        query = query.filter(
            or_(
                Anime.title.ilike(like),
                Anime.title_orig.ilike(like),
                Anime.description.ilike(like),
            )
        )

    # Фильтры
    if genre:
        query = query.join(Anime.genres).filter(Genre.name == genre)
    if status:
        query = query.filter(Anime.status == status)
    if year:
        query = query.filter(Anime.year == year)
    if studio:
        query = query.filter(Anime.studio.ilike(f'%{studio}%'))
    if min_rating is not None:
        query = query.filter(Anime.rating >= min_rating)

    # Сортировка
    sort_map = {
        'rating':  Anime.rating.desc(),
        'popular': Anime.members.desc(),
        'year':    Anime.year.desc(),
        'name':    Anime.title.asc(),
    }
    query = query.order_by(sort_map.get(sort, Anime.rating.desc()))

    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'items':    [a.to_dict(short=True) for a in paginated.items],
        'total':    paginated.total,
        'page':     paginated.page,
        'pages':    paginated.pages,
        'per_page': per_page,
    })


# ── GET /api/anime/<id> ──────────────────────────
@anime_bp.route('/<int:anime_id>', methods=['GET'])
def get_anime(anime_id):
    anime = db.session.get(Anime, anime_id)
    if not anime or not anime.is_published:
        return bad('Аниме не найдено', 404)
    return jsonify(anime.to_dict())


# ── POST /api/anime ──────────────────────────────  (только админ)
@anime_bp.route('', methods=['POST'])
@jwt_required()
def create_anime():
    user, err = require_admin()
    if err: return err

    data = request.get_json(silent=True) or {}
    title = (data.get('title') or '').strip()
    if not title:
        return bad('Название обязательно')

    anime = Anime(
        title       = title,
        title_orig  = data.get('title_orig'),
        description = data.get('description'),
        image_url   = data.get('image_url'),
        trailer_url = data.get('trailer_url'),
        status      = data.get('status', 'finished'),
        year        = data.get('year'),
        episodes    = data.get('episodes'),
        duration    = data.get('duration'),
        studio      = data.get('studio'),
        rating      = data.get('rating', 0.0),
        members     = data.get('members', 0),
        mal_id      = data.get('mal_id'),
    )

    # Жанры
    for genre_name in (data.get('genres') or []):
        genre = Genre.query.filter_by(name=genre_name).first()
        if not genre:
            genre = Genre(name=genre_name)
            db.session.add(genre)
        anime.genres.append(genre)

    # Ссылки на стриминги
    for s in (data.get('streams') or []):
        anime.streams.append(StreamLink(
            platform=s.get('platform'), url=s.get('url'), lang=s.get('lang')
        ))

    db.session.add(anime)
    db.session.commit()
    return jsonify(anime.to_dict()), 201


# ── PUT /api/anime/<id> ──────────────────────────  (только админ)
@anime_bp.route('/<int:anime_id>', methods=['PUT'])
@jwt_required()
def update_anime(anime_id):
    user, err = require_admin()
    if err: return err

    anime = db.session.get(Anime, anime_id)
    if not anime:
        return bad('Аниме не найдено', 404)

    data = request.get_json(silent=True) or {}

    for field in ('title', 'title_orig', 'description', 'image_url',
                  'trailer_url', 'status', 'year', 'episodes',
                  'duration', 'studio', 'rating', 'members', 'mal_id'):
        if field in data:
            setattr(anime, field, data[field])

    if 'genres' in data:
        anime.genres.clear()
        for genre_name in data['genres']:
            genre = Genre.query.filter_by(name=genre_name).first()
            if not genre:
                genre = Genre(name=genre_name)
                db.session.add(genre)
            anime.genres.append(genre)

    if 'streams' in data:
        for s in anime.streams:
            db.session.delete(s)
        for s in data['streams']:
            anime.streams.append(StreamLink(
                platform=s.get('platform'), url=s.get('url'), lang=s.get('lang')
            ))

    db.session.commit()
    return jsonify(anime.to_dict())


# ── DELETE /api/anime/<id> ───────────────────────  (только админ)
@anime_bp.route('/<int:anime_id>', methods=['DELETE'])
@jwt_required()
def delete_anime(anime_id):
    user, err = require_admin()
    if err: return err

    anime = db.session.get(Anime, anime_id)
    if not anime:
        return bad('Аниме не найдено', 404)

    # Мягкое удаление — просто снимаем с публикации
    anime.is_published = False
    db.session.commit()
    return jsonify({'message': f'Аниме «{anime.title}» удалено'})


# ── GET /api/anime/schedule ──────────────────────
@anime_bp.route('/schedule', methods=['GET'])
def get_schedule():
    """Расписание по дням недели."""
    day = request.args.get('day', '')
    query = ScheduleEntry.query
    if day:
        query = query.filter_by(day_of_week=day)

    entries = query.all()
    result = {}
    for e in entries:
        result.setdefault(e.day_of_week, []).append({
            **e.to_dict(),
            'anime': e.anime.to_dict(short=True) if e.anime else None,
        })
    return jsonify(result)


# ── GET /api/genres ──────────────────────────────
@anime_bp.route('/genres', methods=['GET'])
def get_genres():
    from models import Genre
    genres = Genre.query.order_by(Genre.name).all()
    return jsonify([g.to_dict() for g in genres])
