package bench

import (
	"encoding/json"
	"log"
	"math/rand"
	"os"
	"os/signal"
	"strconv"
	"syscall"
	"time"

	"k8-resource-optimizer/pkg/experiments"
	"k8-resource-optimizer/pkg/helmwrap"
	"k8-resource-optimizer/pkg/models"
	"k8-resource-optimizer/pkg/utils"
)

const TmpDir = "/tmp/k8-resource-optimizer/charts/"
const WaitAfterInstallSeconds = 30
const WaitForNamespacesToBeDeleted = 20
const WaitForReadyMax = 180
const WaitTimeOut = 3

type Bench struct {
	Namespaces []Namespace       `json:"namespaces"`
	Experiment models.Experiment `json:"experiment"`
}

type Namespace struct {
	Name   string        `json:"name"`
	Chart  models.Chart  `json:"chart"`
	Config models.Config `json:"config"`
}

type chartWithValues struct {
	tempDir     string
	releaseName string
	namespace   string
}

func (b Bench) Execute() models.ExperimentResult {

	// create chart copies with values of configs injected
	injectedCharts := b.createInjectedCharts()
	b.handleSysInterupts(injectedCharts)
	defer deleleteCharts(injectedCharts)
	installCharts(injectedCharts)
	log.Printf("\t\tBench: Installed  %v charts via helm. Initially waiting %v seconds for setup...", len(injectedCharts), WaitAfterInstallSeconds)
	time.Sleep(WaitAfterInstallSeconds * time.Second)
	podsReady := true // waitForAllPodsReady(injectedCharts)
	var result models.ExperimentResult
	var err error
	if podsReady {
		// run experiment
		log.Printf("\t\tBench: running experiment of type: %v", b.Experiment.GetType())
		result, err = b.Experiment.Run()
		check(err)
	} else {
		log.Printf("\t\tBench: waited max time for pods to be ready")
	}

	return result
}

func (b Bench) createInjectedCharts() []chartWithValues {
	log.Print("\t\tBench: injecting charts values with chosen configurations")
	out := make([]chartWithValues, len(b.Namespaces))
	for i, ns := range b.Namespaces {
		log.Printf("\t\t\tinjecting chart %v/%v", i+1, len(b.Namespaces))
		out[i] = ns.createInjectedChart()
	}
	return out
}

func (ns Namespace) createInjectedChart() chartWithValues {
	out := chartWithValues{}
	out.releaseName = ns.Name + "-" + ns.Chart.Name + "-" + strconv.Itoa(rand.Intn(99999))
	out.tempDir = TmpDir + out.releaseName
	out.namespace = ns.Name
	// create new dir
	err1 := utils.CreateDirWithNecessaryParentsIfnotExists(out.tempDir)
	check(err1)
	// copy chart info
	if ns.Chart.DirPath == "" || ns.Chart.DirPath == "/" {
		log.Panicf("Bench: copying chart from %v", ns.Chart.DirPath)
	}
	err2 := utils.CopyDirContentToOtherDir(ns.Chart.DirPath, out.tempDir)
	check(err2)
	// inject values into values.yaml file of dir

	values, err3 := utils.ReadYamlValuesFileAsMap(out.tempDir + "/values.yaml")

	check(err3)
	// update values in map to config settings
	values["namespace"] = ns.Name
	for _, ps := range ns.Config.GetParameterSettings() {
		name := ps.GetName()
		values[name] = ps.GetValueAsSettingString()
	}
	// write the updated values to the previously created chart dir
	// this operation will truncate the original values file.
	err4 := utils.WriteNewValuesToFile(out.tempDir+"/values.yaml", values)
	check(err4)

	return out
}

func installCharts(charts []chartWithValues) {
	log.Printf("\t\tBench: intalling  %v injected charts ", len(charts))
	for i, chart := range charts {
		log.Printf("\t\t\tintalling chart %v/%v ", i+1, len(charts))
		err := helmwrap.InstallChart(chart.tempDir, chart.releaseName)
		check(err)
	}

}

func waitForAllPodsReady(charts []chartWithValues) bool {
	ready := false
	waited := 0
	log.Printf("\t\tBench: Installed  %v charts via helm. Initially waiting %v seconds for setup...", len(charts), WaitAfterInstallSeconds)
	time.Sleep(WaitAfterInstallSeconds * time.Second)
	for !ready {
		//assume ready
		ready = true
		for _, chart := range charts {
			// if one not ready, ready will flip to false
			ready = ready && helmwrap.AllPodsReadyInNamespace(chart.namespace)
		}

		// waiting periode before recheck
		if !ready && waited >= WaitForReadyMax {
			log.Printf("\t\tBench: not all pods ready of charts, waiting %v more seconds", WaitTimeOut)
			waited += WaitTimeOut
			time.Sleep(WaitTimeOut)
		} else if !ready {
			log.Printf("\t\tBench: waited maximum time for pods to be ready")
			break
		}
	}
	return ready

}

func deleleteCharts(charts []chartWithValues) {
	// delete the releases in Helm
	log.Printf("\t\tBench: Deleting %v Helm charts", len(charts))
	for _, chart := range charts {
		helmwrap.DeleteRelease(chart.releaseName)
	}
	// check if namespaces are actually deleted
	stillExists := true
	for stillExists {
		stillExists = false
		for _, chart := range charts {
			// if one exists it will flip to true and remain true
			stillExists = stillExists || helmwrap.NamespaceExists(chart.namespace)
		}
		// if not deleted wait some longer
		if stillExists {
			log.Printf("\t\tBench: waiting for deleting of %v charts", len(charts))
			time.Sleep(WaitForNamespacesToBeDeleted * time.Second)
		}
	}
	log.Printf("\t\tBench: Deleted %v Helm charts", len(charts))
	// remove created chart directories
	// for _, charts := range charts {
	// 	err := utils.RemoveDirectory(charts.tempDir)
	// 	check(err)
	// }
}

func check(err error) {
	if err != nil {
		panic(err)
	}
}

func (b *Bench) handleSysInterupts(charts []chartWithValues) {
	c := make(chan os.Signal, 2)
	signal.Notify(c, os.Interrupt, syscall.SIGTERM)
	go func() {
		<-c
		log.Printf("INTERRUPT: terminating:  cleaning namespaces")
		deleleteCharts(charts)
		log.Fatal("Stopping execution of bench")
	}()
}

// functions on Bench struct

func (b *Bench) AddNamespace(ns Namespace) {
	b.Namespaces = append(b.Namespaces, ns)
}

func (b *Bench) AddExperiment(e models.Experiment) {
	b.Experiment = e
}

func CreateNamespace(name string, chart models.Chart, config models.Config) (ns Namespace) {
	ns.Name = name
	ns.Chart = chart
	ns.Config = config
	return ns
}

func (be *Bench) UnmarshalJSON(b []byte) error {
	// deserialize into map
	var objMap map[string]*json.RawMessage
	err := json.Unmarshal(b, &objMap)
	if err != nil {
		return err
	}

	//deserialize namespaces
	err = json.Unmarshal(*objMap["namespaces"], &be.Namespaces)
	if err != nil {
		return nil
	}

	be.Experiment, err = experiments.ExperimentUnmarshalJSON(objMap["experiment"])
	if err != nil {
		return err
	}
	return nil
}
