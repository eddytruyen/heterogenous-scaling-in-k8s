# Go parameters
GOCMD=go
GOBUILD=$(GOCMD) build
GOCLEAN=$(GOCMD) clean
GOTEST=$(GOCMD) test
GOGET=$(GOCMD) get
BINARY_NAME=bin/go-deployer
BINARY_MAC=$(BINARY_NAME)_MAC
CMD=app
DOCKERACCOUNT="decomads"

get:
	./go-get.sh

build: 
	cd $(CMD) && go build -o ../bin/go-deployer
test: 
	$(GOTEST) -v ./...
clean: 
	$(GOCLEAN)
	rm -f $(BINARY_NAME)
	rm -f $(BINARY_UNIX)
run:
	$(GOBUILD) -o $(BINARY_NAME) -v ./...
	./$(BINARY_NAME)

    
    
# Cross compilation
build-mac:
	cd $(CMD) && env GOOS=darwin GOARCH=amd64 go build -o ../bin/go-deployer-mac
build-linux:
	cd $(CMD) && env GOOS=linux go build -o ../bin/go-deployer
docker-build:
	docker build . -f ./Dockerfile -t $(DOCKERACCOUNT)/go-deployer:latest
docker-push:
	docker push $(DOCKERACCOUNT)/go-deployer:latest
