FROM quay.io/fedora/fedora:latest

RUN dnf install -y butane mkpasswd
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin

RUN mkdir /app
RUN mkdir /data

WORKDIR /app

COPY . .

RUN uv sync

CMD [ "uv", "run", "main.py" ]
