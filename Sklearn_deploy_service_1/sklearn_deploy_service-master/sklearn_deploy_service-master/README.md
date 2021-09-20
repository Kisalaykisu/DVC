# flask-sklearn

Application to deploy sklearn models


## Build

```bash
docker build -t mlrepa/sklearn_deploy_service:latest .
```

## Run

```bash
docker run \
    --name=deploy-sklearn \
    --rm \
    -v <path/to/model/on/host:/path/to/model/in/docker \
    -e MODEL_PATH=/path/to/model/in/docker \
    -p <port>:9000 \
        mlrepa/sklearn_deploy_service:latest
```

