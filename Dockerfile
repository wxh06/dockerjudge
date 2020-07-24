FROM python:3

LABEL maintainer="汪心禾 <wangxinhe06@gmail.com>"


COPY . .
RUN make pip && make install && rm -rf dockerjudge
