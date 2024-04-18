# Image Auto Editor

[1. How to use](#how-to-use)  
[2. Docker images](#docker-images)  
[2-1. `ptjkjm1/iae-front`](#ptjkjm1iae-front)  
[2-2. `ptjkjm1/iae-back`](#ptjkjm1iae-back)  
[3. Example](#example)  




Docker 기반의 자동화 이미지 처리 툴  
따로 미리 저장해둔 제거해야할 이미지들을 기준으로 입력받은 이미지를 자동으로 처리해주는 작업을 하는 API

## How to use
Docker 이미지가 2개를 포함하고 있습니다   
_Front: Reactjs (`ptjkjm1/iae-front`)_  
_Back: Python Fastapi (`ptjkjm1/iae-back`)_

```
docker pull ptjkjm1/iae-front
docker pull ptjkjm1/iae-back
```

<br>

## Docker images
### `ptjkjm1/iae-front`
- React로 구성한 front-end입니다. `ptjkjm1/iae-back` 이미지에 의존하며 처리된 이미지들을 관리, 확인할 수 있는 UI툴 입니다  

    #### Environments
    - __LANGUAGE__  
        언어 (en: english, ko: 한국어)

### `ptjkjm1/iae-back`
- Python Fastapi로 구성한 back-end입니다. `mongo db`에 의존합니다.

    #### Environments
    - __LANGUAGE__  
        언어 (en: english, ko: 한국어)

    - __PARALLEL_PROC__  
        none : 병렬처리 사용 X  
        proc : 멀티 프로세스를 이용합니다. CPU 코어가 높은데서 효율적입니다.  
        <!-- kafka: 카프카 분산처리 -> CPU 코어가 낮은데서 효율적  
        gcpbucket: GCP의 버킷에 저장한 후 분산처리 -> GCP를 사용중이고 instance 관리 없이 사용하고 싶은 경우   -->

    - __MAX_MULTI_PROCESS__  
        멀티 프로세스 최대 수를 정합니다. PARALLEL_PROC 이 proc일때만 사용 가능합니다.  
        cpu_core : cpu의 코어 갯수만큼 알아서 배치합니다.  
        > 숫자 입력으로 멀티프로세스를 사용할 cpu core 갯수를 조정 가능합니다.

    - __MONGO_HOST__
        mongodb host
        > host.docker.internal:27017

    - __MONGO_USER__
        moongodb username
        다만, 이때 user는 `readWriteAnyDatabase` 권한이 있어야 합니다.
        > 실 배포 환경에서 이런 식으로 ROOT 계정 사용하는 것은 <span style="color: red">보안에 취약할 위험</span>이 큽니다.  
        > local에서만 접근가능한 user를 별도로 두는 등 여러 다른 방식을 고안해야만 합니다.  
        > 외부 mongodb를 사용한다면 별도의 middleware 백엔드 서버를 두는것도 대안이 될 수 있습니다.

    - __MONGO_PW__  
        mongodb password

    - __MONGO_AUTHMECHANISM__
        mongodb auth mechanism  
        > Check [pymongo documentation](https://pymongo.readthedocs.io/en/stable/examples/authentication.html)

    - __MONGO_COLLECTION__  
        mongodb collection name to use
        > default: "main"

<br>

## Example

docker-compose.yml
```YAML
version: '3.8'
services:
    db-mongo:
        image: mongo:6.0.13
        container_name: db-mongo
        restart: on-failure
        ports:
        - "8004:27017"
        environment:
        - MONGO_INITDB_SCRIPTS_DIR=/docker-entrypoint-initdb.d
        - MONGO_INITDB_ROOT_USERNAME=root
        - MONGO_INITDB_ROOT_PASSWORD=rootpw!

    iae-bk:
        image: ptjkjm1/iae-back:1.0.0
        container_name: iae-back
        ports:
        - "8000:8000"
        depends_on:
        - db-mongo
        environment:
        - LANGUAGE=ko
        - PARALLEL_PROC=proc
        - MAX_MULTI_PROCESS=cpu_core
        - MONGO_USER=root
        - MONGO_PW=rootpw!
        - MONGO_HOST=host.docker.internal:8004
        - MONGO_AUTHMECHANISM=SCRAM-SHA-256
        - MONGO_COLLECTION=main

    iae-front:
        image: ptjkjm1/iae-front:1.0.0
        container_name: iae-front
        ports:
        - "3000:3000"
        depends_on:
        - db-mongo
        environment:
        - LANGUAGE=ko
        - FRONT_BACK_HOST=http://localhost:8000
```

> __API DOCS__  
> localhost:8000/redoc

> __IAE MANAGE UI TOOL__  
> localhost:3000