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

package main

import (
	"context"
	"fmt"
	"strings"

	corev1 "k8s.io/api/core/v1"
	"k8s.io/apimachinery/pkg/api/resource"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/rest"
	"k8s.io/client-go/util/retry"
)

type Clientset = kubernetes.Clientset

var clientset *Clientset

type DeploymentScaler struct {
	deploymentName      string
	deploymentNamespace string
	desiredReplicas     int32
	desiredCPU          string
	desiredMemory       string
}

func initDeployerConfig() {
	config, err := rest.InClusterConfig()
	if err != nil {
		panic(err.Error())
	}
	clientset, err = kubernetes.NewForConfig(config)
	if err != nil {
		panic(err.Error())
	}
}

func scaleDeployments(deployments []DeploymentScaler) {
	for _, deployment := range deployments {
		scaleResource(deployment)
	}
}

func scaleResource(s DeploymentScaler) {
	labelSelector := "app=" + s.deploymentName
	canResize, pods := checkInPlaceSupport(s.deploymentNamespace, labelSelector)

	if canResize {
		fmt.Printf(">>> IN-PLACE STRATEGY for %s\n", s.deploymentName)
		for _, pod := range pods {
			err := scalePodInPlace(&pod, s.desiredCPU, s.desiredMemory)
			if err != nil {
				fmt.Printf("Failed to resize pod %s: %v\n", pod.Name, err)
			}
		}
		err := scaleControllerReplicasOnly(s)
		if err != nil {
			fmt.Printf("Failed to update controller replicas for %s: %v\n", s.deploymentName, err)
		}
	} else {
		fmt.Printf(">>> STANDARD ROLLOUT STRATEGY for %s\n", s.deploymentName)
		err := scaleControllerFull(s)
		if err != nil {
			fmt.Printf("Failed standard scaling for %s: %v\n", s.deploymentName, err)
		}
	}
}

func checkInPlaceSupport(namespace string, labelSelector string) (bool, []corev1.Pod) {
	pods, err := clientset.CoreV1().Pods(namespace).List(context.TODO(), metav1.ListOptions{LabelSelector: labelSelector})
	if err != nil || len(pods.Items) == 0 {
		return false, nil
	}
	pod := pods.Items[0]
	if len(pod.Spec.Containers) > 0 && len(pod.Spec.Containers[0].ResizePolicy) > 0 {
		return true, pods.Items
	}
	return false, pods.Items
}

func getPodResources(namespace string, labelSelector string) (string, string) {
	pods, err := clientset.CoreV1().Pods(namespace).List(context.TODO(), metav1.ListOptions{LabelSelector: labelSelector})
	if err != nil || len(pods.Items) == 0 {
		return "0", "0"
	}
	container := pods.Items[0].Spec.Containers[0]
	cpu := container.Resources.Requests.Cpu().String()
	memory := container.Resources.Requests.Memory().String()
	return cpu, memory
}

func scaleControllerReplicasOnly(s DeploymentScaler) error {
	deployClient := clientset.AppsV1().Deployments(s.deploymentNamespace)
	err := retry.RetryOnConflict(retry.DefaultRetry, func() error {
		result, getErr := deployClient.Get(context.TODO(), s.deploymentName, metav1.GetOptions{})
		if getErr != nil {
			return getErr
		}
		result.Spec.Replicas = int32Ptr(s.desiredReplicas)
		_, updateErr := deployClient.Update(context.TODO(), result, metav1.UpdateOptions{})
		return updateErr
	})
	if err == nil {
		return nil
	}
	ssClient := clientset.AppsV1().StatefulSets(s.deploymentNamespace)
	return retry.RetryOnConflict(retry.DefaultRetry, func() error {
		result, getErr := ssClient.Get(context.TODO(), s.deploymentName, metav1.GetOptions{})
		if getErr != nil {
			return getErr
		}
		result.Spec.Replicas = int32Ptr(s.desiredReplicas)
		_, updateErr := ssClient.Update(context.TODO(), result, metav1.UpdateOptions{})
		return updateErr
	})
}

func scaleControllerFull(s DeploymentScaler) error {
	deployClient := clientset.AppsV1().Deployments(s.deploymentNamespace)
	err := retry.RetryOnConflict(retry.DefaultRetry, func() error {
		result, getErr := deployClient.Get(context.TODO(), s.deploymentName, metav1.GetOptions{})
		if getErr != nil {
			return getErr
		}
		result.Spec.Replicas = int32Ptr(s.desiredReplicas)
		updateContainerResources(&result.Spec.Template.Spec, s.desiredCPU, s.desiredMemory)
		_, updateErr := deployClient.Update(context.TODO(), result, metav1.UpdateOptions{})
		return updateErr
	})
	if err == nil {
		return nil
	}
	ssClient := clientset.AppsV1().StatefulSets(s.deploymentNamespace)
	return retry.RetryOnConflict(retry.DefaultRetry, func() error {
		result, getErr := ssClient.Get(context.TODO(), s.deploymentName, metav1.GetOptions{})
		if getErr != nil {
			return getErr
		}
		result.Spec.Replicas = int32Ptr(s.desiredReplicas)
		updateContainerResources(&result.Spec.Template.Spec, s.desiredCPU, s.desiredMemory)
		_, updateErr := ssClient.Update(context.TODO(), result, metav1.UpdateOptions{})
		return updateErr
	})
}

func updateContainerResources(podSpec *corev1.PodSpec, cpu string, memory string) {
	if len(podSpec.Containers) > 0 {
		res := corev1.ResourceList{
			corev1.ResourceCPU:    resource.MustParse(cpu),
			corev1.ResourceMemory: resource.MustParse(memory),
		}
		podSpec.Containers[0].Resources.Requests = res
		podSpec.Containers[0].Resources.Limits = res
	}
}

func scalePodInPlace(pod *corev1.Pod, cpu string, memory string) error {
	newResources := corev1.ResourceList{
		corev1.ResourceCPU:    resource.MustParse(cpu),
		corev1.ResourceMemory: resource.MustParse(memory),
	}
	return retry.RetryOnConflict(retry.DefaultRetry, func() error {
		latestPod, err := clientset.CoreV1().Pods(pod.Namespace).Get(context.TODO(), pod.Name, metav1.GetOptions{})
		if err != nil {
			return err
		}
		latestPod.Spec.Containers[0].Resources.Requests = newResources
		latestPod.Spec.Containers[0].Resources.Limits = newResources
		_, updateErr := clientset.CoreV1().Pods(pod.Namespace).Update(context.TODO(), latestPod, metav1.UpdateOptions{})
		return updateErr
	})
}

func getDeploymentState(namespaces []string) {
	for _, namespace := range namespaces {
		list, _ := clientset.AppsV1().Deployments(namespace).List(context.TODO(), metav1.ListOptions{})
		for _, d := range list.Items {
			fmt.Printf(" * Deployment %s (%d replicas)\n", d.Name, *d.Spec.Replicas)
		}
		ssList, _ := clientset.AppsV1().StatefulSets(namespace).List(context.TODO(), metav1.ListOptions{})
		for _, ss := range ssList.Items {
			fmt.Printf(" * StatefulSet %s (%d replicas)\n", ss.Name, *ss.Spec.Replicas)
		}
	}
}
