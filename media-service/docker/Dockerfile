FROM python:3.10.14-slim
RUN apt-get update && apt-get -y upgrade
WORKDIR /app
COPY docker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8001