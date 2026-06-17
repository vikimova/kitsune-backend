from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from models import db, Rating, Anime

ratings_bp = Blueprint('ratings', __name__, url_prefix='/api/ratings')


def bad(msg, code=400):
    return jsonify({'error': msg}), code


# ── GET /api/ratings ─────────────────────────────
# Все оценки текущего пользователя
@ratings_bp.route('', methods=['GET'])
@jwt_required()
def get_my_ratings():
    user_id = int(get_jwt_identity())
    ratings = Rating.query.filter_by(user_id=user_id).all()
    return jsonify([r.to_dict() for r in ratings])


# ── GET /api/ratings/<anime_id> ──────────────────
# Оценка текущего пользователя для конкретного аниме
@ratings_bp.route('/<int:anime_id>', methods=['GET'])
@jwt_required()
def get_rating(anime_id):
    user_id = int(get_jwt_identity())
    rating  = Rating.query.filter_by(user_id=user_id, anime_id=anime_id).first()
    if not rating:
        return jsonify({'anime_id': anime_id, 'score': None})
    return jsonify(rating.to_dict())


# ── POST /api/ratings ────────────────────────────
# Поставить или обновить оценку
# Body: { anime_id, score }
@ratings_bp.route('', methods=['POST'])
@jwt_required()
def set_rating():
    user_id = int(get_jwt_identity())
    data    = request.get_json(silent=True) or {}

    anime_id = data.get('anime_id')
    score    = data.get('score')

    if not anime_id or score is None:
        return bad('anime_id и score обязательны')
    if not isinstance(score, int) or not (1 <= score <= 10):
        return bad('score должен быть целым числом от 1 до 10')
    if not db.session.get(Anime, anime_id):
        return bad('Аниме не найдено', 404)

    rating = Rating.query.filter_by(
        user_id=user_id, anime_id=anime_id
    ).first()

    if rating:
        rating.score = score
    else:
        rating = Rating(user_id=user_id, anime_id=anime_id, score=score)
        db.session.add(rating)

    db.session.commit()

    # Пересчитываем средний рейтинг аниме
    _recalculate_anime_rating(anime_id)

    return jsonify(rating.to_dict()), 200


# ── DELETE /api/ratings/<anime_id> ───────────────
@ratings_bp.route('/<int:anime_id>', methods=['DELETE'])
@jwt_required()
def delete_rating(anime_id):
    user_id = int(get_jwt_identity())
    rating  = Rating.query.filter_by(
        user_id=user_id, anime_id=anime_id
    ).first()

    if not rating:
        return bad('Оценка не найдена', 404)

    db.session.delete(rating)
    db.session.commit()
    _recalculate_anime_rating(anime_id)
    return jsonify({'message': 'Оценка удалена'})


# ── GET /api/ratings/anime/<anime_id>/stats ───────
# Статистика оценок для аниме (публичный эндпоинт)
@ratings_bp.route('/anime/<int:anime_id>/stats', methods=['GET'])
def get_anime_rating_stats(anime_id):
    result = db.session.query(
        func.avg(Rating.score).label('avg'),
        func.count(Rating.id).label('count'),
    ).filter_by(anime_id=anime_id).first()

    # Распределение оценок 1–10
    distribution = {}
    for score in range(1, 11):
        count = Rating.query.filter_by(anime_id=anime_id, score=score).count()
        distribution[score] = count

    return jsonify({
        'anime_id':     anime_id,
        'average':      round(float(result.avg), 2) if result.avg else 0,
        'count':        result.count or 0,
        'distribution': distribution,
    })


# ── Внутренняя функция: пересчёт рейтинга аниме ──
def _recalculate_anime_rating(anime_id: int):
    result = db.session.query(
        func.avg(Rating.score)
    ).filter_by(anime_id=anime_id).scalar()

    anime = db.session.get(Anime, anime_id)
    if anime:
        anime.rating = round(float(result), 2) if result else 0.0
        db.session.commit()
