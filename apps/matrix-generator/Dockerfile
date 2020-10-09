FROM ubuntu:20.04
COPY requirements.txt /
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get install -y default-jre golang-go gnuplot curl python3 python3-pip
RUN ["/bin/bash", "-c", "curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl && chmod +x ./kubectl && mv ./kubectl /usr/local/bin/kubectl"]
RUN ["/bin/bash", "-c", "curl -LO https://kubernetes-helm.storage.googleapis.com/helm-v2.8.2-linux-amd64.tar.gz && tar -xvzf helm-v2.8.2-linux-amd64.tar.gz && chmod +x ./linux-amd64/helm && mv ./linux-amd64/helm /usr/local/bin/helm"]
RUN ["/bin/bash", "-c", "pip3 install --upgrade pip"]
#RUN pip3 install -r /requirements.txt
RUN pip3 install locust
COPY . .
CMD ["python3", "server.py"]
