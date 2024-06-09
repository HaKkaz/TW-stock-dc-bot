FROM --platform=linux/amd64 python:3.8

WORKDIR /app

RUN apt-get update && apt-get install -y \
    python3-venv afl-fuzz
RUN python3 -m venv .venv
COPY requirements.txt /app/
RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY . /app

CMD ["python3", "./src/app.py"]
