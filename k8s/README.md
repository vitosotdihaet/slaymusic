# Запуск

Я хотел всю конфигурацию засунуть в `.env`, но для кубов нет нормального способа это сделать, поэтому тут немного магии шелла:

```bash
export $(grep -v '^#' ../.env | xargs) && envsubst < deployment.yaml | kubectl apply -f -
```

Вместо `deployment.yaml` подставьте деплоймент сервиса, что хотите запустить


# Порты
Открытие портов во внешний мир (пока) происходит через команду:

```bash
kubectl port-forward service/name out:in out:in
```