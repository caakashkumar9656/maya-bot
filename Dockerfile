FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt tzdata
COPY maya ./maya
VOLUME /data
ENV DB_PATH=/data/maya.db
CMD ["python", "-m", "maya"]
