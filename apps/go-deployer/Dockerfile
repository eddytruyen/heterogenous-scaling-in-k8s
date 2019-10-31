FROM arguez/go-service-base:latest
WORKDIR /go/src/app
COPY ./app .
RUN go install -v
CMD ["app"]
