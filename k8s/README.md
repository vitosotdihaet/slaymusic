# Установка tilt

[туториал](https://docs.tilt.dev/install.html)

На линуксе:
```bash
curl -fsSL https://raw.githubusercontent.com/tilt-dev/tilt/master/scripts/install.sh | bash
```

# Запуск minikube

```bash
minikube start --driver=docker
```

# Запуск tilt (и всех сервисов)

```bash
tilt up
```

Backend доступен по http://localhost:8000/

Minio WEBUI доступен по http://localhost:9101/

(чекайте `.env`)

# Остановка minikube (и всех сервисов)

```bash
minikube stop
```

# Удаление всех ресурсов tilt

```bash
tilt down
```

Если запускать кубы в WSL, то, чтобы работала синхронизация локальных файлов с теми, что В кубах, нужно держать локальные файлы в файловой системе Linux: `\wsl.localhost\`