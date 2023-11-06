FROM python:3.7-slim-bullseye
COPY requirements.txt /
RUN pip3 install -r /requirements.txt
COPY src-kyuubi/ /app
WORKDIR /app
CMD ["python", "scheduler.py"]
