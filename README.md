# 공지사항 이메일 알림 시스템

이 프로젝트는 웹사이트의 공지사항을 실시간으로 모니터링하고, 새로운 공지사항이 등록되면 이메일로 알림을 보내는 시스템입니다.

## 기능

- 웹사이트 공지사항 자동 모니터링
- 이메일 알림 시스템
- 관리자 인터페이스를 통한 사이트 목록 관리
- 이메일 구독자 관리

## 설치 방법

1. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

2. 환경 변수 설정:
```
# .env 파일에 다음 내용을 추가
EMAIL_SENDER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
```

3. 데이터베이스 초기화:
```bash
python
from app import db
from app import app
with app.app_context():
    db.create_all()
```

4. 애플리케이션 실행:
```bash
python app.py
```

## API 문서

### 사이트 관리

- GET /api/sites: 등록된 사이트 목록 조회
- POST /api/sites: 새로운 사이트 등록
- DELETE /api/sites/<id>: 사이트 삭제

### 이메일 구독 관리

- POST /api/subscriptions: 새로운 이메일 구독자 등록
- DELETE /api/subscriptions: 이메일 구독 취소

## 주의사항

- Gmail을 사용하여 이메일을 보내려면 앱 비밀번호를 생성해야 합니다.
- 사이트의 HTML 구조가 변경될 경우 선택자(selector)를 업데이트해야 할 수 있습니다.

## 기술 스택

- Python
- Flask
- SQLAlchemy
- BeautifulSoup
- Gmail SMTP
