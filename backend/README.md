# Запуск

# Сборка докер образа

Подключаем докер окружение миникуба

```bash
eval $(minikube -p minikube docker-env)
```

Собираем контейнер

```bash
docker build -t it-project-music-streaming-service-backend:latest .
```