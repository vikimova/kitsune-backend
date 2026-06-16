from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# ════════════════════════════════════════════════
# Вспомогательная таблица: аниме ↔ жанры (many-to-many)
# ════════════════════════════════════════════════
anime_genres = db.Table(
    'anime_genres',
    db.Column('anime_id', db.Integer, db.ForeignKey('anime.id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'), primary_key=True),
)

# ════════════════════════════════════════════════
# GENRE
# ════════════════════════════════════════════════
class Genre(db.Model):
    __tablename__ = 'genre'

    id   = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    name_ru = db.Column(db.String(64))  # русское название жанра

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'name_ru': self.name_ru}

# ════════════════════════════════════════════════
# ANIME
# ════════════════════════════════════════════════
class Anime(db.Model):
    __tablename__ = 'anime'

    id          = db.Column(db.Integer, primary_key=True)
    mal_id      = db.Column(db.Integer, unique=True)          # ID на MyAnimeList
    title       = db.Column(db.String(256), nullable=False)   # русское название
    title_orig  = db.Column(db.String(256))                   # японское / английское
    description = db.Column(db.Text)
    image_url   = db.Column(db.String(512))
    trailer_url = db.Column(db.String(512))                   # embed-ссылка плеера

    status      = db.Column(db.String(16), default='finished')
    # 'ongoing' | 'finished' | 'announced'

    year        = db.Column(db.Integer)
    episodes    = db.Column(db.Integer)
    duration    = db.Column(db.Integer)    # минут на эпизод
    studio      = db.Column(db.String(128))
    rating      = db.Column(db.Float, default=0.0)
    members     = db.Column(db.Integer, default=0)  # число пользователей MAL
    is_published = db.Column(db.Boolean, default=True)

    created_at  = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at  = db.Column(db.DateTime,
                            default=lambda: datetime.now(timezone.utc),
                            onupdate=lambda: datetime.now(timezone.utc))

    # Связи
    genres      = db.relationship('Genre', secondary=anime_genres, backref='anime_list', lazy='subquery')
    streams     = db.relationship('StreamLink', backref='anime', lazy='subquery', cascade='all, delete-orphan')
    schedule    = db.relationship('ScheduleEntry', backref='anime', lazy='subquery', cascade='all, delete-orphan')

    def to_dict(self, short=False):
        base = {
            'id':         self.id,
            'mal_id':     self.mal_id,
            'title':      self.title,
            'title_orig': self.title_orig,
            'image_url':  self.image_url,
            'status':     self.status,
            'year':       self.year,
            'episodes':   self.episodes,
            'rating':     self.rating,
            'studio':     self.studio,
            'genres':     [g.name for g in self.genres],
        }
        if not short:
            base.update({
                'description': self.description,
                'trailer_url': self.trailer_url,
                'duration':    self.duration,
                'members':     self.members,
                'streams':     [s.to_dict() for s in self.streams],
            })
        return base

# ════════════════════════════════════════════════
# STREAM LINK — ссылки на стриминговые сервисы
# ════════════════════════════════════════════════
class StreamLink(db.Model):
    __tablename__ = 'stream_link'

    id       = db.Column(db.Integer, primary_key=True)
    anime_id = db.Column(db.Integer, db.ForeignKey('anime.id'), nullable=False)
    platform = db.Column(db.String(64))   # AniLibria, Crunchyroll, Netflix…
    url      = db.Column(db.String(512))
    lang     = db.Column(db.String(32))   # рус. озвучка / субтитры / EN sub

    def to_dict(self):
        return {'platform': self.platform, 'url': self.url, 'lang': self.lang}

# ════════════════════════════════════════════════
# SCHEDULE ENTRY — расписание выхода серий
# ════════════════════════════════════════════════
class ScheduleEntry(db.Model):
    __tablename__ = 'schedule_entry'

    id         = db.Column(db.Integer, primary_key=True)
    anime_id   = db.Column(db.Integer, db.ForeignKey('anime.id'), nullable=False)
    day_of_week = db.Column(db.String(3))   # 'Пн' | 'Вт' | ... | 'Вс'
    air_time   = db.Column(db.String(5))    # '18:30'
    episode    = db.Column(db.String(32))   # 'Сер. 5' или '4 сез. · Сер. 8'

    def to_dict(self):
        return {
            'anime_id':    self.anime_id,
            'day_of_week': self.day_of_week,
            'air_time':    self.air_time,
            'episode':     self.episode,
        }

# ════════════════════════════════════════════════
# USER
# ════════════════════════════════════════════════
class User(db.Model):
    __tablename__ = 'user'

    id           = db.Column(db.Integer, primary_key=True)
    username     = db.Column(db.String(64), unique=True, nullable=False)
    email        = db.Column(db.String(128), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role         = db.Column(db.String(16), default='user')  # 'user' | 'admin'
    avatar_url   = db.Column(db.String(512))
    created_at   = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    is_active    = db.Column(db.Boolean, default=True)

    # Связи
    collections = db.relationship('Collection', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    ratings     = db.relationship('Rating',     backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id':         self.id,
            'username':   self.username,
            'email':      self.email,
            'role':       self.role,
            'avatar_url': self.avatar_url,
            'created_at': self.created_at.isoformat(),
            'stats': {
                'watched':  self.collections.filter_by(status='watched').count(),
                'watching': self.collections.filter_by(status='watching').count(),
                'planned':  self.collections.filter_by(status='planned').count(),
            }
        }

# ════════════════════════════════════════════════
# COLLECTION — список аниме пользователя
# ════════════════════════════════════════════════
class Collection(db.Model):
    __tablename__ = 'collection'

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    anime_id   = db.Column(db.Integer, db.ForeignKey('anime.id'), nullable=False)
    status     = db.Column(db.String(16), nullable=False)
    # 'watching' | 'planned' | 'watched' | 'dropped' | 'hold' | 'fav'
    episodes_watched = db.Column(db.Integer, default=0)
    added_at   = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime,
                           default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    # Уникальность: один пользователь — одна запись на аниме
    __table_args__ = (
        db.UniqueConstraint('user_id', 'anime_id', name='uq_user_anime'),
    )

    anime = db.relationship('Anime', lazy='joined')

    def to_dict(self):
        return {
            'id':               self.id,
            'anime_id':         self.anime_id,
            'status':           self.status,
            'episodes_watched': self.episodes_watched,
            'added_at':         self.added_at.isoformat(),
            'anime':            self.anime.to_dict(short=True) if self.anime else None,
        }

# ════════════════════════════════════════════════
# RATING — оценка аниме пользователем (1–10)
# ════════════════════════════════════════════════
class Rating(db.Model):
    __tablename__ = 'rating'

    id       = db.Column(db.Integer, primary_key=True)
    user_id  = db.Column(db.Integer, db.ForeignKey('user.id'),  nullable=False)
    anime_id = db.Column(db.Integer, db.ForeignKey('anime.id'), nullable=False)
    score    = db.Column(db.Integer, nullable=False)  # 1–10

    __table_args__ = (
        db.UniqueConstraint('user_id', 'anime_id', name='uq_user_anime_rating'),
        db.CheckConstraint('score >= 1 AND score <= 10', name='ck_score_range'),
    )

    def to_dict(self):
        return {'anime_id': self.anime_id, 'score': self.score}
