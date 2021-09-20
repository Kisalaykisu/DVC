

## 1. Fork this repository & clone to your local machine

```bash
git clone https://github.com/Kisalaykisu/DVC.git
cd dvc-4-ci-mlops
```

## 2. Create and activate virtual environment

Create virtual environment named `dvc-venv` (you may use other name)
```bash
python3 -m venv dvc-venv
echo "export PYTHONPATH=$PWD" >> dvc-venv/bin/activate
source dvc-venv/bin/activate
```

## 3. Install python libraries

```bash
pip install -r requirements.txt
```

## 4. Init DVC

```bash
dvc init
git add .dvc
git commit -m "dvc init"
```

## 5. Setup dvc remote

```bash
dvc remote add -d local /tmp/dvc/dvc-4-ci-mlops
git add .dvc/config
git commit -m "add dvc remote"
```

## 6. Create a ML experiment pipeline

### 6.1. Build DVC pipeline

* Get data

Create stage:

```bash
dvc run -n data_load \
    -d src/pipelines/data_load.py \
    -o data/raw/iris.csv \
    -p base,data_load \
    python src/pipelines/data_load.py \
        --config=params.yaml
```
Reproduce stage: `dvc repro data_load`
    
* Features extraction

Create stage:

```bash
dvc run -n featurize \
    -d src/pipelines/featurize.py \
    -d data/raw/iris.csv \
    -o data/processed/features.csv \
    -p base,data_load,featurize \
    python src/pipelines/featurize.py \
        --config=params.yaml
```

Reproduce stage: `dvc repro featurize`

        
* Split train/test datasets

Create stage:

```bash
dvc run -n data_split \
    -d src/pipelines/data_split.py \
    -d data/processed/features.csv \
    -o data/processed/train.csv \
    -o data/processed/test.csv \
    -p base,featurize,data_split \
    python src/pipelines/data_split.py \
        --config=params.yaml
```

Reproduce stage: `dvc repro data_split`


* Train model 

Create stage:

```bash
dvc run -n train \
    -d src/pipelines/train.py \
    -d data/processed/train.csv \
    -o experiments/models/model.joblib \
    -p base,featurize.target_column,data_split.train_path,train \
    python src/pipelines/train.py \
        --config=params.yaml
```

Reproduce stage: `dvc repro train`


* Evaluate model

Create stage:

```bash
dvc run -n evaluate \
    -d src/pipelines/evaluate.py \
    -d data/processed/test.csv \
    -d experiments/models/model.joblib \
    -o experiments/confusion_matrix.png \
    -m experiments/metrics.json \
    --plots experiments/classess.csv \
    -p base,featurize.target_column,data_split.test_path,evaluate \
    python src/pipelines/evaluate.py \
        --config=params.yaml
```

Reproduce stage: `dvc repro evaluate`

### 6.2. Commit pipeline

```bash
git add .
git commit -m "Build DVC pipeline"
```


## 7. Setup Gitlab Runners
GitLab Runner is the agent that runs your build jobs and sends the results back to a GitLab instance
Mode details in [GitLab Runner Docs](https://docs.gitlab.com/runner/)

### 7.1 Add credential variables

1. At the repository page go to **Settings** -> **CI / CD** -> **Variables**;
2. Click **Expand**;
3. Add variable:

```dotenv
repo_token=<access_token>
```

**Note**: remove flag `Protect variable`.

### 7.2 Disable shared runners 

1. go to **Settings** -> **CI / CD** -> **Runners** -> **Shared Runners**;
2. click `Disable shared Runners`.

### 7.3  Install gitlab-runner

Please, follow these [installation instructions](https://docs.gitlab.com/runner/install/)

### 7.4 Register a gitlab-runner

Get registration token: 

1. go to **Settings** -> **CI / CD** -> **Specific Runners** -> **Set up a specific Runner manually**;
2. copy  registration token from `3.Use the following registration token during setup:`;
3. create env var:

```bash
export REGISTRATION_TOKEN=<registration_token>
```

Register new gitlab-runner (with shell executor) 

```bash
gitlab-runner register \
            --non-interactive \
            -u https://gitlab.com/ \
            -r $REGISTRATION_TOKEN \
            --tag-list dvc-4-ci-mlops \
            --executor shell 
```

__Notes__:
* *--non-interactive* - to avoid gitlab-runner prompts;
* *-u* - CI server URL.

### 7.5 Register a docker-based runner for stage `cml_run`

```bash
gitlab-runner register \
            --non-interactive \
            -u https://gitlab.com/ \
            -r $REGISTRATION_TOKEN \
            --tag-list dvc-4-ci-mlops-cml \
            --executor docker \
            --docker-image mlrepa/cml:latest \
            --docker-disable-cache \
            --docker-volumes "/tmp:/tmp"
```

__Notes__:
* *--docker-image* - docker image which will be used by default to 
run CI job if another image will not be specified in job definition;
* *--docker-disable-cache* - avoid caching repository and data in container's volume,
volume will not be stored; it guarantees repository is fresh at every `cml` run;
if cache enabled repository can stay outdated;
* *--docker-volumes* - mount folders from host to docker container; 
it gives access to local DVC remote.

## 7.6. Run gitlab-runners

```bash
gitlab-runner run 
```


## 8. Setup CI/CD pipeline  (.gitlab-ci.yml)

### 8.1 Variables and stages

```yaml
variables:
  DEPLOY_IMAGE: mlrepa/sklearn_deploy_service:latest
  DEPLOY_PORT: 9000
  CML_MAGE: mlrepa/cml:latest
  PROJECT_MODEL_PATH: experiments/models/model.joblib
  DOCKER_MODEL_PATH: /home/deploy/models/model.joblib

stages:
  - build
  - test
  - deploy
  - cml_run
```

### 8.2 Build stage

```yaml
build:
  tags:
    - dvc-4-ci-mlops
  only:
    refs:
      - merge_requests
    variables:
      - $CI_MERGE_REQUEST_TARGET_BRANCH_NAME == "master"
  stage: build
  script:
    - docker pull $DEPLOY_IMAGE
    - |
      if [ ! -d "/tmp/$CI_PROJECT_NAME" ]; then
        project_url=${CI_PROJECT_URL//"https://"/}
        git clone \
            https://oauth2:$repo_token@${project_url}.git \
            "/tmp/$CI_PROJECT_NAME"
      fi
      cd /tmp/$CI_PROJECT_NAME
      git fetch
      git checkout $CI_COMMIT_REF_NAME --no-guess
      git pull origin $CI_COMMIT_REF_NAME
      dvc pull
```

How it works:
* Pull deploy docker image (*sklearn_deploy_service:lastest*)
* Clone repo if it does not exist locally
* Enter local repo
* Checkout branch $CI_COMMIT_REF_NAME
* Pull changes
* Pull all artifacts from DVC remote

**Note**: deploy service repository: https://github.com/Kisalaykisu/DVC/tree/main/Sklearn_deploy_service_1/sklearn_deploy_service-master/sklearn_deploy_service-master


### 8.3 Test stage

```yaml
test:
  tags:
    - dvc-4-ci-mlops
  only:
    refs:
      - merge_requests
    variables:
      - $CI_MERGE_REQUEST_TARGET_BRANCH_NAME == "master"
  stage: test
  script:
    - cd /tmp/$CI_PROJECT_NAME
    - |
      docker run \
            --name=deploy-sklearn-test \
            --rm \
            -v $(pwd)/tests:/home/deploy/tests \
            -v $(pwd)/$PROJECT_MODEL_PATH:$DOCKER_MODEL_PATH \
            -e MODEL_PATH=$DOCKER_MODEL_PATH \
                $DEPLOY_IMAGE /bin/bash -c "
                    pytest /home/deploy/tests/test_model.py
                "
```

How it works:
* Enter local repo
* Run tests in the docker deploy container

### 8.4 Deploy stage

```yaml
deploy:
  tags:
    - dvc-4-ci-mlops
  only:
    refs:
      - merge_requests
    variables:
      - $CI_MERGE_REQUEST_TARGET_BRANCH_NAME == "master"
  stage: deploy
  script:
    - cd /tmp/$CI_PROJECT_NAME
    - pwd
    - |
      if ! curl http://localhost:9000/healthcheck; then
        docker run \
            -d \
            --name=deploy-sklearn-$(date +"%Y-%m-%d-%H-%M-%S") \
            -v $(pwd)/$PROJECT_MODEL_PATH:$DOCKER_MODEL_PATH \
            -e MODEL_PATH=$DOCKER_MODEL_PATH \
            -p $DEPLOY_PORT:9000 \
                $DEPLOY_IMAGE
      else
        curl -X POST http://localhost:9000/reload-model
      fi
```

How it works:
* Enter local repo
* Get name of current directory
* Run deploy container if it is not running
* If the container is running - make request to reload model

__Note__:
* We specified a runner by tag here:

```yaml
tags:
    - dvc-4-ci-mlops
```
it means that just runner with tag `dvc-4-ci-mlops` will executes CI pipeline


### 8.5. CML stage

```yaml
cml:
  tags:
    - dvc-4-ci-mlops-cml
  stage: cml_run
  image: mlrepa/cml:latest
  only:
    refs:
      - merge_requests
    variables:
      - $CI_MERGE_REQUEST_TARGET_BRANCH_NAME == "experiments"
  script:
    - apt-get install -y jq
    - git fetch
    - git checkout $CI_COMMIT_REF_NAME --no-guess
    - git pull origin $CI_COMMIT_REF_NAME
    - dvc pull --all-commits -q

    # Report metrics
    - echo "## Metrics" >> report.md
    - |
      echo "## f1_score: $(cat experiments/metrics.json | jq '.f1_score')" >> report.md
    - dvc metrics diff --show-md --all experiments  >> report.md
    - echo >> report.md
    - cml-publish experiments/confusion_matrix.png --md >> report.md

    # Publish confusion matrix diff
    - cml-send-comment report.md

```

How it works:

1 - Prepare 
* Install `jq` for parsing json from CLI
* Fetch repository
* Checkout the experiment branch (that is merged into `experiments`) by variable $CI_COMMIT_REF_NAME 
* Pull updates from the experiment branch 
* Pull DVC artifacts from remote (for all commit `--all-commits`) in a quiet (`-q`) mode

2 - Create a report 
* Get `f1` score from `experiments/metrics.json` and write it in `report.md`
* Write DVC metrics diff in `report.md` with `--all` key to list all metrics, even those without changes
* Publish confusion matrix image and add link to `report.md`

3 - Publish report to the commit message
* Add a commit message/comment from the `report.md` content

__Note__:
- This stage Only if merge request target branch is `experiments` 
- To trigger job `cml` just create *Merge Request* from any branch to `experiments`
- `dvc pull --all-commits` may be very expensive operation (in terms of time/IO/disk space) if there is a lot of artifacts stored in the remote storage


## 9. Run CI/CD pipeline

To run CI pipeline you must push your changes to remote repository:

```bash
git add .gitlab-ci.yml
git commit -m "Build CI pipeline"
git push origin master
```

Create `experiments` branch

```bash
git checkout -b experiments
git push origin experiments
```

## 9. Run Experiments / Reproduce pipeline



Create new experiment branch:

```bash
git checkout -b exp-1
```

Edit `params.yml` and run reproduce command:

```bash
dvc repro
```

Push artifacts to the DVC remote storage & commit changes

```bash
dvc push
```

Commit run changes

```bash
git add .
git commit -m "Commit exp-1 experiment run results"
```

Push experiment to remote Git repo (`origin` by default)

```bash
git push origin exp-1:exp-1
```

## 10. Activate CI/CD pipelines with commit / merge events

### Create branch `experiments`

```bash
git checkout master
git checkout -b experiments
git push origin experiments
```

### Create merge request from `exp-1` to `experiments` branch 

This should invoke CML stage on CI/CD pipeline: 
* cml.


### Merge the `exp-1` experiment to `master` branch

This should invoke the following sequence of stages in CI/CD pipeline: 
* build; 
* test; 
* deploy.  

As a result - a web-based service would be deployed and available on `http://localhost:9000` 


## 11. Test the deployed service by API

### 11.1. Check connection

````bash
curl http://localhost:9000/healthcheck
````

if service is available it will return:
```bash
OK
```

### 11.2. Get predictions

```bash
curl http://localhost:9000/predict \
    -d '{"data":[[value11,value12,...,value1N],...,[value1M,valueM2,...,valueMN]]}'
```

where:
* M - number if rows to predict;
* N - number if columns.

Columns order is the same as in train dataset.


example:

```bash
curl -POST http://localhost:9000/predict -d '{"data":[[4,3,2,1,0,0],[1,2,3,4,2,2]]}'
```

result:

```bash
{"predictions": [1,1]}
```

Predictions legend: ('setosa', 0), ('versicolor', 1), ('virginica', 2)
