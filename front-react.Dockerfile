FROM node:20.12.1-alpine

RUN echo "step 1 > Set timezone"
ENV TZ=Asia/Seoul
RUN ln -snf /usr/share/zoneinfo/Asia/Seoul /etc/localtime

RUN echo "step 2 > Make source directory"
RUN mkdir -p /home/src/iae-setter

WORKDIR /home/src/iae-setter

RUN echo "step 3 > Install typescript"
RUN npm i -g typescript ts-node @types/node

RUN echo "step 4 > Copy package.json"
COPY ./front-react/src/package.json /home/src/iae-setter
RUN npm init -y
RUN npm i

RUN echo "step 5 > Copy source"
COPY ./front-react/src /home/src/iae-setter
WORKDIR /home/src/iae-setter

RUN npm run build

ENV IS_INSIDE_IN_DOCKER_NOT_VALUE_FOR_USER=True
ENV LANGUAGE=en
# ENV FRONT_BACK_HOST
ENV BACK_API_TIMEOUT=30000

EXPOSE 3000

RUN echo "step 7 > Service App"
RUN npm i -g serve

RUN mkdir /entrypointsh
COPY ./front-react/entrypoint /entrypointsh
RUN chmod -R 777 /entrypointsh

ENTRYPOINT [ "/entrypointsh/entry.sh" ]
CMD [ "serve", "-s", "build" ]