# Нагрузочные тесты

Для запусков тестов поднимите сервис (см `/k8s`), установите, все что в `requirements.txt`, запустите

```sh
locust -f load_tests/locustfile.py
```