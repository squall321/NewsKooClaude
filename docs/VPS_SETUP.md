# VPS 설정 가이드

## VPS 선택 옵션

### 추천 VPS 제공업체

1. **Contabo** (가장 저렴)
   - 가격: €4.99/월
   - 스펙: 4 vCPU, 6GB RAM, 200GB NVMe
   - 장점: 저렴한 가격, 높은 스펙
   - 단점: 고객 지원 느림

2. **Hetzner**
   - 가격: €4.15/월
   - 스펙: 2 vCPU, 4GB RAM, 40GB SSD
   - 장점: 빠른 네트워크, 좋은 평판
   - 단점: 한국에서 약간 느릴 수 있음

3. **Oracle Cloud Free Tier** (무료!)
   - 가격: $0/월 (평생 무료)
   - 스펙: 2 vCPU, 12GB RAM, 100GB Storage
   - 장점: 완전 무료, 충분한 스펙
   - 단점: 계정 생성 까다로움

4. **DigitalOcean**
   - 가격: $6/월
   - 스펙: 1 vCPU, 1GB RAM, 25GB SSD
   - 장점: 쉬운 사용, 좋은 문서
   - 단점: 가격 대비 스펙 낮음

### 추천 선택

- **개발/테스트**: Oracle Cloud Free Tier
- **프로덕션 (저비용)**: Contabo
- **프로덕션 (안정성)**: Hetzner

## 서버 초기 설정

### 1. Ubuntu 22.04 LTS 설치

```bash
# SSH 접속
ssh root@your-server-ip

# 시스템 업데이트
apt update && apt upgrade -y

# 필수 패키지 설치
apt install -y curl wget git vim ufw fail2ban
```

### 2. 사용자 생성

```bash
# 새 사용자 생성
adduser deploy
usermod -aG sudo deploy

# SSH 키 설정
mkdir -p /home/deploy/.ssh
cp ~/.ssh/authorized_keys /home/deploy/.ssh/
chown -R deploy:deploy /home/deploy/.ssh
chmod 700 /home/deploy/.ssh
chmod 600 /home/deploy/.ssh/authorized_keys
```

### 3. 방화벽 설정

```bash
# UFW 방화벽 설정
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable

# 상태 확인
ufw status
```

### 4. Fail2Ban 설정

```bash
# Fail2Ban 설정
cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local

# SSH 보호 활성화
cat >> /etc/fail2ban/jail.local << 'EOF'
[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600
EOF

# Fail2Ban 재시작
systemctl restart fail2ban
systemctl enable fail2ban
```

### 5. Docker 설치

```bash
# Docker 설치 스크립트
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Docker Compose 설치
mkdir -p ~/.docker/cli-plugins/
curl -SL https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-linux-x86_64 -o ~/.docker/cli-plugins/docker-compose
chmod +x ~/.docker/cli-plugins/docker-compose

# deploy 사용자에게 Docker 권한 부여
usermod -aG docker deploy

# Docker 서비스 시작
systemctl start docker
systemctl enable docker

# 설치 확인
docker --version
docker compose version
```

### 6. Nginx 리버스 프록시 (Docker 외부)

```bash
# Nginx 설치 (선택적 - Docker로 실행할 수도 있음)
apt install -y nginx

# Nginx 시작
systemctl start nginx
systemctl enable nginx
```

### 7. Let's Encrypt SSL 인증서

```bash
# Certbot 설치
apt install -y certbot python3-certbot-nginx

# SSL 인증서 발급 (도메인 연결 후)
certbot --nginx -d newskoo.com -d www.newskoo.com

# 자동 갱신 설정 (이미 cron에 추가됨)
certbot renew --dry-run
```

## 배포 스크립트

### 프로젝트 클론

```bash
# deploy 사용자로 전환
su - deploy

# 프로젝트 디렉토리 생성
mkdir -p ~/projects
cd ~/projects

# Git 클론
git clone https://github.com/yourusername/NewsKooClaude.git
cd NewsKooClaude
```

### 환경 변수 설정

```bash
# .env.production 파일 생성
cp .env.production.example .env.production
nano .env.production

# 필수 값 설정:
# - SECRET_KEY
# - JWT_SECRET_KEY
# - POSTGRES_PASSWORD
# - REDDIT_CLIENT_ID/SECRET
```

### Docker Compose 실행

```bash
# Docker Compose로 빌드 및 실행
docker compose -f docker-compose.yml up -d --build

# 로그 확인
docker compose logs -f

# 컨테이너 상태 확인
docker compose ps
```

## 모니터링

### 시스템 리소스 확인

```bash
# CPU/메모리 사용량
htop

# 디스크 사용량
df -h

# Docker 컨테이너 리소스
docker stats
```

### 로그 확인

```bash
# Nginx 로그
docker compose logs nginx

# Backend 로그
docker compose logs backend

# 전체 로그
docker compose logs -f
```

## 백업

### 데이터베이스 백업

```bash
# PostgreSQL 백업
docker compose exec postgres pg_dump -U newskoo newskoo > backup_$(date +%Y%m%d).sql

# 백업 파일 압축
gzip backup_$(date +%Y%m%d).sql
```

### 자동 백업 스크립트

```bash
# /home/deploy/backup.sh
#!/bin/bash
BACKUP_DIR="/home/deploy/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# PostgreSQL 백업
docker compose exec -T postgres pg_dump -U newskoo newskoo | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# 오래된 백업 삭제 (30일 이상)
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +30 -delete

echo "Backup completed: db_$DATE.sql.gz"
```

### Cron 설정

```bash
# Crontab 편집
crontab -e

# 매일 새벽 2시 백업
0 2 * * * /home/deploy/backup.sh >> /home/deploy/backup.log 2>&1
```

## 트러블슈팅

### 포트 충돌

```bash
# 포트 사용 확인
sudo lsof -i :80
sudo lsof -i :443
sudo lsof -i :5000
```

### 컨테이너 재시작

```bash
# 특정 컨테이너 재시작
docker compose restart backend

# 전체 재시작
docker compose down && docker compose up -d
```

### 디스크 공간 부족

```bash
# Docker 정리
docker system prune -a --volumes

# 로그 파일 정리
find /var/log -name "*.log" -mtime +7 -delete
```

## 성능 최적화

### Swap 메모리 설정

```bash
# 2GB Swap 생성
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile

# 영구 설정
echo '/swapfile none swap sw 0 0' >> /etc/fstab
```

### PostgreSQL 튜닝

```bash
# PostgreSQL 설정 최적화
docker compose exec postgres psql -U newskoo -c "ALTER SYSTEM SET shared_buffers = '256MB';"
docker compose exec postgres psql -U newskoo -c "ALTER SYSTEM SET effective_cache_size = '1GB';"
docker compose restart postgres
```
