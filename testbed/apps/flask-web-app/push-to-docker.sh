sudo docker build -t flask-test:latest .
sudo docker tag flask-test:latest avl4kul/flask-web-app:latest
sudo docker push avl4kul/flask-web-app:latest