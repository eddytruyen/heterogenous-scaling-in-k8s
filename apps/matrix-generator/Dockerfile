FROM decomads/k8-resource-optimizer:latest
COPY requirements.txt /
RUN apt-get update
RUN pip3 install -r /requirements.txt
COPY . .
RUN cp /exp/k8-resource-optimizer /bin/k8-resource-optimizer
CMD ["python3", "server.py"]
