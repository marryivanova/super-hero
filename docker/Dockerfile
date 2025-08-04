FROM repo.saber3d.net/docker/library/python:3.12-bookworm

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-u", "main.py"]