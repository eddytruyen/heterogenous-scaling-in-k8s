FROM python:3.7-alpine
COPY requirements.txt /
RUN pip3 install -r /requirements.txt
COPY src/ /app
WORKDIR /app
CMD ["python", "scheduler.py"]