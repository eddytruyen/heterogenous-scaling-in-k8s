/*
Copyright 2016 The Kubernetes Authors.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

// Note: the example only works with the code within the same release/branch.
package main

import (
	"fmt"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/rest"
	"k8s.io/client-go/util/retry"
	//
	// Uncomment to load all auth plugins
	// _ "k8s.io/client-go/plugin/pkg/client/auth
	//
	// Or uncomment to load specific auth plugins
	// _ "k8s.io/client-go/plugin/pkg/client/auth/azure"
	// _ "k8s.io/client-go/plugin/pkg/client/auth/gcp"
	// _ "k8s.io/client-go/plugin/pkg/client/auth/oidc"
	// _ "k8s.io/client-go/plugin/pkg/client/auth/openstack"
)

type Clientset = kubernetes.Clientset

var clientset *Clientset


type DeploymentScaler struct {
    deploymentName string
	deploymentNamespace string
	desiredReplicas int32
}

func initDeployerConfig(){
	// creates the in-cluster config
	config, err := rest.InClusterConfig()
	if err != nil {
		panic(err.Error())
	}
	// creates the clientset
	clientset, _ = kubernetes.NewForConfig(config)
	if err != nil {
		panic(err.Error())
	}
}

func scaleDeployments(deployments []DeploymentScaler){
	for _, deployment := range deployments{
		scaleDeployment(deployment)
	}
}

func getDeploymentState(namespaces []string){
	for _, namespace :=range namespaces{
		deploymentsClient := clientset.AppsV1().Deployments(namespace)
		list, err := deploymentsClient.List(metav1.ListOptions{})
		if err != nil {
			panic(err)
		}
		for _, d := range list.Items {
			fmt.Printf(" * %s (%d replicas)\n", d.Name, *d.Spec.Replicas)
		}	
	}
}

func scaleDeployment(deploymentScaler DeploymentScaler) error{
	deploymentsClient := clientset.AppsV1().Deployments(deploymentScaler.deploymentNamespace)
	retryErr := retry.RetryOnConflict(retry.DefaultRetry, func() error {
		// Retrieve the latest version of Deployment before attempting update
		// RetryOnConflict uses exponential backoff to avoid exhausting the apiserver
		result, getErr := deploymentsClient.Get(deploymentScaler.deploymentName, metav1.GetOptions{})
		if getErr != nil {
			panic(fmt.Errorf("Failed to get latest version of Deployment: %v", getErr))
		}
		result.Spec.Replicas = int32Ptr(deploymentScaler.desiredReplicas)                           // update replica count
		_, updateErr := deploymentsClient.Update(result)
		return updateErr
	})
	if retryErr != nil {
		panic(fmt.Errorf("Update failed: %v", retryErr))
	}
	fmt.Println("Updated deployment...")

	return nil
}
