# K8-resource-optimizer



## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

What things you need to install the software and how to install them:

* GOLANG: https://golang.org/doc/install
* Docker: https://www.docker.com/get-started
* Dockerhub: https://hub.docker.com/


### Installing

Running and building the k8-resource-optimizer tool

Clone the project into your GOLANG GOPATH: most likely $HOME/go/src\
More info on setting your GOPATH: https://github.com/golang/go/wiki/SettingGOPATH

```
git clone ...
```

Once cloned, changed the *accountname* variable to your docker repository in the *scripts/build.sh* file.
Create a repository named *k8-resource-optimizer* in your dockerhub account.
Building the tool is as easy as running the script *build.sh* from the main folder.
This will build a linux binary and push it to your dockerhub repository.

```
./scripts/build.sh
```

## Deployment

### Setup Kubernetes on DNETCLOUD.

...

### Perparing your Kubernetes cluster


#### creating service account for tiller (HELM)
This assumes you have RBAC enabled on your k8 cluster.

```
cd deployments/k8/rbac
```
Service account for tiller:
```
kubectl create -f helm-rbac.yaml
```
Service account for k8-resource-optimizer.yaml
```
kubectl create -f serviceAccount.yaml
```
####  Installing HELM
Install HELM but: **do not run helm init** 

link: https://docs.helm.sh/using_helm/#installing-helm 

After installing run: 
```
helm init --service-account tiller
```

### Actually deploying K8-resource-optimizer
In the yaml file *deployments/tool-deployment.yaml* change the image to your image. 
Deploy the tool by: 
```
kubectl create -f deployments/k8/tool-deployment.yaml
```

### Developing without constantly pushing to DockerHub
If an instance of k8-resource-optimizer is **already deployed** in your k8-cluster, a local build of the binary can be easily copied to the pod by the script:
```
./scripts/buildandcp.sh
```
## Running the tool
Connect to your running deployment and start an interactive bash-shell
```
./scripts/connect.sh
```
Once connected move to the exp folder. 
```
cd exp
```
Run the binary with a given configuration. For example
```
./k8-resource-optimer conf/sladecompose.yaml
```

## Example 
An example Spring boot application is located in the *examples* folder.\
For the application, a example configuration for the tool sladecompose.yaml and helm chart can be found in the *conf* folder.






