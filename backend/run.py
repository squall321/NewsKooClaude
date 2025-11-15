"""
Flask 애플리케이션 실행 스크립트
개발 서버를 시작합니다
"""
import os
from app import create_app, db

# 환경 설정 (기본값: development)
config_name = os.getenv('FLASK_ENV', 'development')

# 앱 생성
app = create_app(config_name)


@app.shell_context_processor
def make_shell_context():
    """Flask shell 컨텍스트에 자동으로 import할 객체들"""
    return {
        'db': db,
        'app': app,
    }


if __name__ == '__main__':
    # 개발 서버 실행
    port = int(os.getenv('PORT', 5000))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=app.config['DEBUG']
    )
