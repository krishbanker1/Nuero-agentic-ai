"""Docker Deploy - Complete containerization and deployment"""
from typing import Dict, Any
class DockerDeploy:
    def build(self, description: str, stack: str = "node-react") -> Dict[str, Any]:
        return {
            "Dockerfile.app": self._dockerfile_app(),
            "Dockerfile.db": self._dockerfile_db(),
            "docker-compose.yml": self._docker_compose(),
            "nginx.conf": self._nginx_conf(),
            ".dockerignore": self._dockerignore(),
        }
    def _dockerfile_app(self) -> str:
        return '''FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
FROM node:18-alpine AS production
WORKDIR /app
RUN addgroup -g 1001 -S nodejs && adduser -S nodejs -u 1001
COPY --from=builder --chown=nodejs:nodejs /app/node_modules ./node_modules
COPY --chown=nodejs:nodejs . .
USER nodejs
EXPOSE 3000
CMD ["node", "server.js"]'''
    def _dockerfile_db(self) -> str:
        return '''FROM postgres:15-alpine
RUN apk add --no-cache postgresql-contrib
COPY init.sql /docker-entrypoint-initdb.d/
EXPOSE 5432
ENV POSTGRES_DB=app
ENV POSTGRES_USER=app
ENV POSTGRES_PASSWORD=changeme'''
    def _docker_compose(self) -> str:
        return '''version: "3.8"
services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgres://app:changeme@db:5432/app
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped
  db:
    image: postgres:15-alpine
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DB=app
      - POSTGRES_USER=app
      - POSTGRES_PASSWORD=changeme
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    depends_on:
      - app
    restart: unless-stopped
volumes:
  pgdata:'''
    def _nginx_conf(self) -> str:
        return '''events { worker_connections 1024; }
http {
    upstream app { server app:3000; keepalive 32; }
    server {
        listen 80;
        server_name localhost;
        location / {
            proxy_pass http://app;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}'''
    def _dockerignore(self) -> str:
        return '''node_modules
npm-debug.log
.env
.git
.vscode
*.log'''

def docker_deploy(description: str, stack: str = "node-react") -> Dict[str, Any]:
    return DockerDeploy().build(description, stack)
