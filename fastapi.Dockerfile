FROM python:3.11.8

RUN echo "step 1 > Set timezone"
ENV TZ=Asia/Seoul
RUN ln -snf /usr/share/zoneinfo/Asia/Seoul /etc/localtime

RUN echo "step 2 > Make source directory"
RUN mkdir -p /home/src/ImageAutoEditor
RUN mkdir /home/logs
WORKDIR /home/src/ImageAutoEditor

RUN echo "step 3 > copy source"
COPY ./fastapi/src /home/src/ImageAutoEditor

RUN echo "step 4 > Install requirements.txt"
RUN pip install --no-cache-dir --upgrade -r requirements.txt

ENV IS_INSIDE_IN_DOCKER_NOT_VALUE_FOR_USER=True
ENV LANGUAGE=en
# ENV ALLOWED_IP
ENV PARALLEL_PROC=proc
ENV MAX_MULTI_PROCESS=cpu_core
ENV MONGO_USER=default
ENV MONGO_PW=default
ENV MONGO_HOST=host.docker.internal:27017
ENV MONGO_AUTHMECHANISM=DEFAULT
ENV MONGO_COLLECTION=main

RUN echo "step 5 > Run prebuild task"
RUN mkdir -p /home/src/prebuild
COPY ./fastapi/prebuild /home/src/prebuild
RUN python /home/src/prebuild/main.py

EXPOSE 8000

RUN echo "step 5 > Start backend program"
CMD ["uvicorn", "index:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "10"]