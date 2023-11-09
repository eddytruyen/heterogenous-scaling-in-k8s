FROM python:3.7-slim-bullseye
COPY --from=openjdk:8-jre-slim /usr/local/openjdk-8 /usr/local/openjdk-8
ENV JAVA_HOME /usr/local/openjdk-8
RUN update-alternatives --install /usr/bin/java java /usr/local/openjdk-8/bin/java 1
COPY requirements.txt /
RUN pip3 install -r /requirements.txt
COPY src-kyuubi/ /app
WORKDIR /app
CMD ["python", "scheduler.py"]
