for f in *.yaml; do
    export $(grep -v '^#' ../.env | xargs) && envsubst < $f | kubectl apply -f -;
done