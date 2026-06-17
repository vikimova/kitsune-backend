from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity
)
from models import db, User

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


def bad(msg, code=400):
    return jsonify({'error': msg}), code


# ── POST /api/auth/register ──────────────────────
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json(silent=True) or {}

    username = (data.get('username') or '').strip()
    email    = (data.get('email')    or '').strip().lower()
    password =  data.get('password') or ''

    if not username or not email or not password:
        return bad('Заполните все поля')
    if len(username) < 3:
        return bad('Имя пользователя минимум 3 символа')
    if len(password) < 6:
        return bad('Пароль минимум 6 символов')
    if '@' not in email:
        return bad('Некорректный email')

    if User.query.filter_by(username=username).first():
        return bad('Имя пользователя уже занято')
    if User.query.filter_by(email=email).first():
        return bad('Email уже зарегистрирован')

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return jsonify({'token': token, 'user': user.to_dict()}), 201


# ── POST /api/auth/login ─────────────────────────
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}

    login_id = (data.get('username') or data.get('email') or '').strip()
    password =  data.get('password') or ''

    if not login_id or not password:
        return bad('Введите логин и пароль')

    # Ищем по username или email
    user = (
        User.query.filter_by(username=login_id).first() or
        User.query.filter_by(email=login_id.lower()).first()
    )

    if not user or not user.check_password(password):
        return bad('Неверный логин или пароль', 401)
    if not user.is_active:
        return bad('Аккаунт заблокирован', 403)

    token = create_access_token(identity=str(user.id))
    return jsonify({'token': token, 'user': user.to_dict()})


# ── GET /api/auth/me ─────────────────────────────
@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user:
        return bad('Пользователь не найден', 404)
    return jsonify(user.to_dict())


# ── PATCH /api/auth/me ───────────────────────────
@auth_bp.route('/me', methods=['PATCH'])
@jwt_required()
def update_me():
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user:
        return bad('Пользователь не найден', 404)

    data = request.get_json(silent=True) or {}

    if 'username' in data:
        new_name = data['username'].strip()
        if len(new_name) < 3:
            return bad('Имя минимум 3 символа')
        existing = User.query.filter_by(username=new_name).first()
        if existing and existing.id != user.id:
            return bad('Имя уже занято')
        user.username = new_name

    if 'avatar_url' in data:
        user.avatar_url = data['avatar_url']

    db.session.commit()
    return jsonify(user.to_dict())


# ── POST /api/auth/change-password ──────────────
@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user:
        return bad('Пользователь не найден', 404)

    data = request.get_json(silent=True) or {}
    old_password = data.get('old_password') or ''
    new_password = data.get('new_password') or ''

    if not user.check_password(old_password):
        return bad('Неверный текущий пароль', 401)
    if len(new_password) < 6:
        return bad('Новый пароль минимум 6 символов')

    user.set_password(new_password)
    db.session.commit()
    return jsonify({'message': 'Пароль изменён'})
