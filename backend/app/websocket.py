"""
WebSocket 이벤트 핸들러
실시간 알림, 댓글, 좋아요 업데이트 등
"""

from flask import request
from flask_socketio import SocketIO, emit, join_room, leave_room, rooms
from flask_jwt_extended import decode_token
from functools import wraps
import logging

logger = logging.getLogger(__name__)

# SocketIO 인스턴스 (app/__init__.py에서 초기화)
socketio = None

# 온라인 사용자 추적
online_users = set()
room_users = {}  # {room_id: set(user_ids)}


def init_socketio(app):
    """SocketIO 초기화"""
    global socketio

    socketio = SocketIO(
        app,
        cors_allowed_origins=app.config.get('CORS_ORIGINS', '*'),
        async_mode='gevent',
        logger=True,
        engineio_logger=True,
        ping_timeout=60,
        ping_interval=25,
    )

    register_handlers(socketio)
    logger.info('SocketIO initialized')

    return socketio


def authenticated_only(f):
    """WebSocket 인증 데코레이터"""
    @wraps(f)
    def wrapped(*args, **kwargs):
        # JWT 토큰 확인
        token = request.args.get('token')
        if not token:
            emit('error', {'message': 'Authentication required'})
            return

        try:
            decoded = decode_token(token)
            request.user_id = decoded['sub']
            return f(*args, **kwargs)
        except Exception as e:
            emit('error', {'message': 'Invalid token'})
            return

    return wrapped


def register_handlers(socketio):
    """WebSocket 이벤트 핸들러 등록"""

    @socketio.on('connect')
    def handle_connect():
        """클라이언트 연결"""
        logger.info(f'Client connected: {request.sid}')

        # 토큰이 있으면 인증된 사용자
        token = request.args.get('token')
        if token:
            try:
                decoded = decode_token(token)
                user_id = decoded['sub']
                online_users.add(user_id)

                # 온라인 사용자 수 브로드캐스트
                emit('online_users_count', {
                    'count': len(online_users)
                }, broadcast=True)

                logger.info(f'User {user_id} connected')
            except Exception as e:
                logger.error(f'Token decode error: {e}')

    @socketio.on('disconnect')
    def handle_disconnect():
        """클라이언트 연결 해제"""
        logger.info(f'Client disconnected: {request.sid}')

        # 인증된 사용자였다면 온라인 목록에서 제거
        token = request.args.get('token')
        if token:
            try:
                decoded = decode_token(token)
                user_id = decoded['sub']
                online_users.discard(user_id)

                # 모든 룸에서 제거
                for room_id, users in room_users.items():
                    users.discard(user_id)

                # 온라인 사용자 수 브로드캐스트
                emit('online_users_count', {
                    'count': len(online_users)
                }, broadcast=True)

                logger.info(f'User {user_id} disconnected')
            except Exception:
                pass

    @socketio.on('join_post')
    def handle_join_post(data):
        """게시물 룸 참여 (실시간 댓글/좋아요 업데이트)"""
        post_id = data.get('post_id')
        if not post_id:
            return

        room = f'post_{post_id}'
        join_room(room)

        # 룸 사용자 추적
        token = request.args.get('token')
        if token:
            try:
                decoded = decode_token(token)
                user_id = decoded['sub']

                if room not in room_users:
                    room_users[room] = set()
                room_users[room].add(user_id)

                # 현재 룸의 사용자 수 전송
                emit('room_users_count', {
                    'post_id': post_id,
                    'count': len(room_users[room])
                }, room=room)

            except Exception:
                pass

        logger.info(f'Client {request.sid} joined post room {post_id}')

    @socketio.on('leave_post')
    def handle_leave_post(data):
        """게시물 룸 나가기"""
        post_id = data.get('post_id')
        if not post_id:
            return

        room = f'post_{post_id}'
        leave_room(room)

        # 룸 사용자 추적에서 제거
        token = request.args.get('token')
        if token and room in room_users:
            try:
                decoded = decode_token(token)
                user_id = decoded['sub']
                room_users[room].discard(user_id)

                # 현재 룸의 사용자 수 전송
                emit('room_users_count', {
                    'post_id': post_id,
                    'count': len(room_users[room])
                }, room=room)

            except Exception:
                pass

        logger.info(f'Client {request.sid} left post room {post_id}')

    @socketio.on('typing')
    @authenticated_only
    def handle_typing(data):
        """댓글 작성 중 표시"""
        post_id = data.get('post_id')
        username = data.get('username', 'Anonymous')

        if not post_id:
            return

        room = f'post_{post_id}'

        # 자신을 제외한 룸의 다른 사용자에게 전송
        emit('user_typing', {
            'user_id': request.user_id,
            'username': username,
            'post_id': post_id
        }, room=room, include_self=False)

    @socketio.on('stop_typing')
    @authenticated_only
    def handle_stop_typing(data):
        """댓글 작성 중단"""
        post_id = data.get('post_id')

        if not post_id:
            return

        room = f'post_{post_id}'

        emit('user_stop_typing', {
            'user_id': request.user_id,
            'post_id': post_id
        }, room=room, include_self=False)


def emit_new_comment(post_id, comment_data):
    """새 댓글 알림 전송"""
    if socketio:
        socketio.emit('new_comment', {
            'post_id': post_id,
            'comment': comment_data
        }, room=f'post_{post_id}')


def emit_comment_deleted(post_id, comment_id):
    """댓글 삭제 알림 전송"""
    if socketio:
        socketio.emit('comment_deleted', {
            'post_id': post_id,
            'comment_id': comment_id
        }, room=f'post_{post_id}')


def emit_post_liked(post_id, likes_count):
    """게시물 좋아요 업데이트"""
    if socketio:
        socketio.emit('post_liked', {
            'post_id': post_id,
            'likes_count': likes_count
        }, room=f'post_{post_id}')


def emit_post_viewed(post_id, views_count):
    """게시물 조회수 업데이트"""
    if socketio:
        socketio.emit('post_viewed', {
            'post_id': post_id,
            'views_count': views_count
        }, room=f'post_{post_id}')


def emit_notification(user_id, notification_data):
    """사용자별 알림 전송"""
    if socketio:
        socketio.emit('notification', notification_data, room=f'user_{user_id}')
