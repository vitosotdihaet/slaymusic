def make_port_forward(var):
    return env_vars[var]+':'+env_vars[var]


allow_k8s_contexts('minikube')

env_vars = dict()
for line in str(read_file('.env')).splitlines():
    if line.strip() and not line.startswith('#'):
        key, value = line.strip().split('=', 1)
        env_vars[key] = value

yaml_files = [
    'k8s/backend.yaml',
    'k8s/setup-job.yaml',
    'k8s/psql-music.yaml',
    'k8s/minio.yaml',
    'k8s/mongo-user-activity.yaml',
    'k8s/redis-track-queue.yaml',
    'k8s/redis-track-queue-config.yaml',
]

for file in yaml_files:
    yaml_content = str(read_file(file))
    for key, value in env_vars.items():
        yaml_content = yaml_content.replace('$%s' % key, value)
    k8s_yaml(blob(yaml_content))

k8s_resource(
    'setup-job',
    resource_deps=[
        'minio',
        'postgres-music',
    ],
)

# Set up port forwarding
k8s_resource(
    'slaymusic-backend',
    port_forwards=[
        make_port_forward('BACKEND_PORT')
    ],
    resource_deps=[
        'minio',
        'postgres-music',
        'mongodb-user-activity',
        'redis-track-queue',
        'setup-job'
    ]
)

k8s_resource(
    'minio',
    port_forwards=[
        env_vars['MINIO_WEBUI_PORT']+':9001'
    ]
)

# Docker build configuration
docker_build(
    'slaymusic-backend-image',
    '.',
    dockerfile='./backend/dockerfile',
    build_args={'BACKEND_PORT': env_vars['BACKEND_PORT']},
    only=['backend', '.env'],
    live_update=[
        sync('backend/', '/app/'),
        run('cd /app && pip install -r requirements.txt',
            trigger='./backend/requirements.txt'),
    ]
)

docker_build(
    'slaymusic-setup-job-image',
    '.',
    dockerfile='./backend/dockerfile',
    build_args={'BACKEND_PORT': env_vars['BACKEND_PORT']},
    only=['backend', '.env']
)
