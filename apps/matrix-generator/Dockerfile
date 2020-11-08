FROM decomads/k8-resource-optimizer:k8s-v1.18-ground-zero
COPY requirements.txt /
RUN apt-get update
RUN pip3 install -r /requirements.txt
COPY . .
RUN cp /exp/k8-resource-optimizer /bin/k8-resource-optimizer
CMD ["python3", "server.py"]
