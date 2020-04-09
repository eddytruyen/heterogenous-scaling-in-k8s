package helmwrap

import (
	"log"
	"os/exec"

	yaml "gopkg.in/yaml.v2"
)

//InstallChart install a given chart
// returns: nil if chart is installed.
func InstallChart(chartDir string, releaseName string) error {
	log.Printf("\t\t\tHelmwrap: installing chart: %v as release: %v", chartDir, releaseName)
	args := []string{
		"install",
		chartDir,
		"--name",
		releaseName,
		"--wait"}
	_, err := exec.Command("helm", args...).Output()
	if err != nil {
		log.Printf("error in Helmwrap InstallChart: %v", err)
		return err
	}

	return nil

}

// DeleteRelease deletes a given release
func DeleteRelease(releaseName string) error {
	log.Printf("\t\t\tHelmwrap: deleting release: %v", releaseName)
	args := []string{
		"delete",
		"--purge",
		releaseName}
	_, err := exec.Command("helm", args...).Output()
	if err != nil {
		log.Printf("error in Helmwrap DeleteRelease: %v", err)
		return err
	}
	return nil
}

// HelmStatus gives information on the status of a release.
type HelmStatus struct {
	Info struct {
		Description string
		Status      struct {
			Code int
		}
	}
	Name      string
	Namespace string
}

// ReleaseStatus returns the status of a given release.
func ReleaseStatus(releaseName string) (bool, HelmStatus) {
	status := HelmStatus{}
	args := []string{
		"status",
		"--output",
		"yaml",
		releaseName}
	res, err := exec.Command("helm", args...).Output()
	if err != nil {
		log.Panicf("error in Helmwrap Releasestatus: executing command: %v", err)
		return false, status
	}
	unmarshallError := yaml.Unmarshal(res, &status)
	if err != nil {
		log.Printf("error in Helmwrap Releasestatus: unmarhal: %v", unmarshallError)
	}

	return true, status
}

type kubeNamespace struct {
	Items []struct {
		Kind     string
		Metadata struct {
			Name string
		}
	}
}

type podList struct {
	Items []podDescription
}

type podDescription struct {
	Kind     string
	Metadata interface{}
	Spec     interface{}
	Status   struct {
		condititions []podCondition
	}
}

type podCondition struct {
	Type   string
	Status bool
}

func AllPodsReadyInNamespace(namespace string) bool {
	podList := podList{}
	args := []string{
		"-n",
		namespace,
		"get",
		"pods",
		"--output",
		"json"}
	res, err := exec.Command("kubectl", args...).Output()
	if err != nil {
		log.Panicf("error in Helmwrap kubenamespaces: executing command: %v, %v", err, res)
		return false
	}

	unmarshallError := yaml.Unmarshal(res, &podList)
	if err != nil {
		log.Printf("error in Helmwrap kubenamespaces: unmarhal: %v", unmarshallError)
	}

	for _, pd := range podList.Items {
		if !pd.podReady() {
			return false
		}
	}
	return true
}

func (pd podDescription) podReady() bool {
	for _, pc := range pd.Status.condititions {
		if pc.Type == "Ready" {
			return pc.Status
		}
	}
	return false
}

// NamespaceExists checks if a given namespace in Kubernets still exists.
func NamespaceExists(namespace string) bool {
	namespaces := kubeNamespace{}
	args := []string{
		"get",
		"namespaces",
		"--output",
		"yaml"}
	res, err := exec.Command("kubectl", args...).Output()
	if err != nil {
		log.Panicf("error in Helmwrap kubenamespaces: executing command: %v, %v", err, res)
		return false
	}

	unmarshallError := yaml.Unmarshal(res, &namespaces)
	if err != nil {
		log.Printf("error in Helmwrap kubenamespaces: unmarhal: %v", unmarshallError)
	}

	for _, v := range namespaces.Items {
		if v.Metadata.Name == namespace {
			return true
		}
	}
	return false

}
