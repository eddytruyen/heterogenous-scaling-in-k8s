FROM decomads/k8-resource-optimizer:latest
COPY requirements.txt /
RUN apt-get update
RUN pip3 install -r /requirements.txt
COPY . .
CMD ["python3", "server.py"]
