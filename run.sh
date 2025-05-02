#! /usr/bin/bash

mkdir -p data && podman run -it -v ./data:/data:z ghcr.io/gabeklavans/ucore-turnkey
