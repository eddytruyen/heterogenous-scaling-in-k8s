FROM python:3.7-alpine
COPY requirements.txt /
RUN pip3 install -r /requirements.txt
COPY app/ app/
COPY run-app.sh /
EXPOSE 5000
CMD [ "python3", "app/app.py" ]