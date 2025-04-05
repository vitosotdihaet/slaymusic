## Запуск minicube

```bash
minikube start --driver=docker
```

## Запуск tilt (и всех сервисов)

```bash
tilt up
```

### backend доступен по http://localhost:8000/

### minio webui доступен по http://localhost:9101/

## Остановка minikube (и всех сервисов)

```bash
minikube stop
```

## Удаление всех ресурсов tilt

```bash
tilt down
```

### Чтобы работала синхронизация локальных файлов с теми что в кубах в WSL, нужно держать локальные файлы в файловой системе Linux: \\wsl.localhost\ 