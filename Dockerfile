FROM python:3-alpine

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY plex-ambiance.py .

ENTRYPOINT [ "python", "./plex-ambiance.py" ]