#!/bin/sh
set -v
docker pull bash  # For bash
docker pull clangbuiltlinux/ubuntu:llvm10-latest  # For clang-10 & clang++-10
docker pull clangbuiltlinux/ubuntu:llvm11-latest  # For clang-11 & clang++-11
docker pull gcc:4.8  # For gcc & g++
docker pull gcc:4.9  # For gccgo
docker pull golang:1  # For go
docker pull mono  # For csc, vbnc & mono
docker pull node:12  # For node
docker pull openjdk  # For javac and java
docker pull php  # For php
docker pull pypy:2  # For pypy2
docker pull pypy:3  # For pypy3
docker pull python:2  # For python2
docker pull python:3  # For python3
docker pull ruby  # For ruby
docker pull swift  # For swiftc
