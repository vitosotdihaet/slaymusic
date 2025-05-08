# Установка tilt

[туториал](https://docs.tilt.dev/install.html)

На линуксе:
```bash
curl -fsSL https://raw.githubusercontent.com/tilt-dev/tilt/master/scripts/install.sh | bash
```

# Запуск проекта

### Запуск minikube

```bash
minikube start
```

### Запуск tilt и всех сервисов

```bash
tilt up
```

Backend доступен по http://localhost:8000/

Minio WEBUI доступен по http://localhost:9101/

(чекайте `.env`)

Если запускать кубы в WSL, то, чтобы работала синхронизация локальных файлов с теми, что в кубах, нужно держать локальные файлы в файловой системе Linux: `\wsl.localhost\`

# Остановка проекта

### Удаление всех сервисов и контейнеров (pvc датабаз, образы остаются для следущего tilt up)

```bash
tilt down
```

### Остановка minikube

```bash
minikube stop
```