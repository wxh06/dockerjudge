FROM docker

LABEL maintainer="汪心禾 <wangxinhe06@gmail.com>"


RUN [ "apk", "add", "--no-cache", "py3-pip", "make" ]

COPY . .
RUN make pip && make install && rm -rf dockerjudge
