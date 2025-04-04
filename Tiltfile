allow_k8s_contexts('minikube')

env_vars = dict()
for line in str(read_file('.env')).split('\n'):
    if line.strip() and not line.startswith('#'):
        key, value = line.strip().split('=', 1)
        env_vars[key] = value

yaml_files = [
    'k8s/backend.yaml',
    'k8s/minio.yaml',
    'k8s/psql-accounts.yaml',
    'k8s/psql-music.yaml',
    'k8s/psql-user-activity.yaml'
]

for file in yaml_files:
    yaml_content = str(read_file(file))
    for key, value in env_vars.items():
        yaml_content = yaml_content.replace('${%s}' % key, value)
        yaml_content = yaml_content.replace('$%s' % key, value)
    k8s_yaml(blob(yaml_content))

# Set up port forwarding
k8s_resource( 
    'it-project-music-streaming-service-backend',
    port_forwards=['8000:8000'],
)

k8s_resource(
    'minio',
    port_forwards=['9101:9001']
) 

# Docker build configuration
docker_build(
    'it-project-music-streaming-service-backend-image',
    './backend',
    dockerfile='./backend/dockerfile',
    live_update=[
        sync('backend/main.py', '/app/main.py'),
        run('cd /app && pip install -r requirements.txt', 
            trigger='./backend/requirements.txt'),
    ]
)