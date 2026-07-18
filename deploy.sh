#!/bin/bash
echo "🚀 Деплой Reels Bot - ПОЛНАЯ АВТОМАТИЗАЦИЯ"
docker-compose down
docker-compose build
docker-compose up -d
docker-compose logs -f
