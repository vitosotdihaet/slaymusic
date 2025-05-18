deploy:
	kubectl apply -f backend.yaml; \
	envsubst < minio.yaml | kubectl apply -f -; \
	envsubst < psql-music.yaml | kubectl apply -f -; \
	envsubst < psql-user-activity.yaml | kubectl apply -f -; \
	envsubst < psql-replication/config.yaml | kubectl apply -f -; \
	envsubst < psql-replication/headless.yaml | kubectl apply -f -; \
	envsubst < psql-replication/secrets.yaml | kubectl apply -f -; \
	envsubst < psql-replication/stateful.yaml | kubectl apply -f -;

stop:
	kubectl delete all --all
