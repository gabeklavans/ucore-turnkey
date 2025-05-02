#!/usr/bin/bash

mkdir data && podman run -it -v ./data:/data:z ghcr.io/gabeklavans/ucore-turnkey
