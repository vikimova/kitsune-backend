from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Collection, Anime

collections_bp = Blueprint('collections', __name__, url_prefix='/api/collections')

VALID_STATUSES = {'watching', 'planned', 'watched', 'dropped', 'hold', 'fav'}


def bad(msg, code=400):
    return jsonify({'error': msg}), code


# ── GET /api/collections ─────────────────────────
# Возвращает всю коллекцию текущего пользователя
# Параметры: status (фильтр), page, per_page
@collections_bp.route('', methods=['GET'])
@jwt_required()
def get_collections():
    user_id  = int(get_jwt_identity())
    status   = request.args.get('status', '')
    page     = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 50, type=int), 100)

    query = Collection.query.filter_by(user_id=user_id)
    if status and status in VALID_STATUSES:
        query = query.filter_by(status=status)

    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'items':    [c.to_dict() for c in paginated.items],
        'total':    paginated.total,
        'page':     paginated.page,
        'pages':    paginated.pages,
    })


# ── GET /api/collections/stats ───────────────────
# Счётчики по каждому статусу
@collections_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    user_id = int(get_jwt_identity())
    result = {}
    for status in VALID_STATUSES:
        result[status] = Collection.query.filter_by(
            user_id=user_id, status=status
        ).count()
    return jsonify(result)


# ── POST /api/collections ────────────────────────
# Добавить или обновить запись
# Body: { anime_id, status, episodes_watched? }
@collections_bp.route('', methods=['POST'])
@jwt_required()
def upsert_collection():
    user_id = int(get_jwt_identity())
    data    = request.get_json(silent=True) or {}

    anime_id = data.get('anime_id')
    status   = data.get('status')

    if not anime_id or not status:
        return bad('anime_id и status обязательны')
    if status not in VALID_STATUSES:
        return bad(f'Недопустимый статус. Допустимы: {", ".join(VALID_STATUSES)}')
    if not db.session.get(Anime, anime_id):
        return bad('Аниме не найдено', 404)

    # Ищем существующую запись
    entry = Collection.query.filter_by(
        user_id=user_id, anime_id=anime_id
    ).first()

    if entry:
        entry.status = status
        if 'episodes_watched' in data:
            entry.episodes_watched = data['episodes_watched']
    else:
        entry = Collection(
            user_id=user_id,
            anime_id=anime_id,
            status=status,
            episodes_watched=data.get('episodes_watched', 0),
        )
        db.session.add(entry)

    db.session.commit()
    return jsonify(entry.to_dict()), 200


# ── DELETE /api/collections/<anime_id> ───────────
@collections_bp.route('/<int:anime_id>', methods=['DELETE'])
@jwt_required()
def remove_from_collection(anime_id):
    user_id = int(get_jwt_identity())
    entry   = Collection.query.filter_by(
        user_id=user_id, anime_id=anime_id
    ).first()

    if not entry:
        return bad('Запись не найдена', 404)

    db.session.delete(entry)
    db.session.commit()
    return jsonify({'message': 'Удалено из коллекции'})


# ── PATCH /api/collections/<anime_id>/progress ───
# Обновить прогресс просмотра (кол-во просмотренных серий)
@collections_bp.route('/<int:anime_id>/progress', methods=['PATCH'])
@jwt_required()
def update_progress(anime_id):
    user_id  = int(get_jwt_identity())
    data     = request.get_json(silent=True) or {}
    episodes = data.get('episodes_watched')

    if episodes is None or not isinstance(episodes, int) or episodes < 0:
        return bad('episodes_watched должен быть целым числом ≥ 0')

    entry = Collection.query.filter_by(
        user_id=user_id, anime_id=anime_id
    ).first()

    if not entry:
        return bad('Сначала добавьте аниме в коллекцию', 404)

    entry.episodes_watched = episodes

    # Если досмотрели все серии — автоматически ставим "Просмотрено"
    anime = db.session.get(Anime, anime_id)
    if anime and anime.episodes and episodes >= anime.episodes:
        entry.status = 'watched'

    db.session.commit()
    return jsonify(entry.to_dict())
