DATE := $(shell date +%Y-%m-%d)

build: update
	podman build -t menu-app:$(DATE) .

update: # update base image
	podman pull python:3.10-alpine
