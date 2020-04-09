package sockshop

// import (
// 	"fmt"
// 	"strconv"
// 	"strings"

// 	"github.com/MatthijsKaminski/k8-resource-optimizer/pkg/locustwrap"
// 	"github.com/MatthijsKaminski/k8-resource-optimizer/pkg/models"
// )

// //LocustRequestExperiment : Locust experiment for all tenants of all namespaces
// type LocustSockShopExperiment struct {
// 	Iteration    int
// 	Sample       int
// 	Locustconfig locustwrap.Config
// 	OutputDir    string
// 	Type         string
// }

// func createLocustSockShopExperiment(slas []models.SLA) models.Experiment {
// 	// var e models.Experiment
// 	e := &LocustSockShopExperiment{}
// 	e.Locustconfig.DurationInSeconds = experimentDurationInSeconds
// 	e.Locustconfig.
// 		// create script
// 		e.Locustconfig.ScriptPath = locustwrap.CreateRunScript(users, "locust_exp")

// 	e.Type = "LocustRequestExperiment"

// 	return e
// }

// func createLocustRequestExperimentParameters(s models.SLA, jobsize int, tenantNb int) locustwrap.User {
// 	user := locustwrap.User{}
// 	user.TenantID = s.Name + strconv.Itoa(tenantNb)
// 	user.Name = s.Name + "-" + strconv.Itoa(tenantNb)
// 	user.URL = "http://consumer." + s.Name + ".svc.cluster.local:80/cpu/" //+ strconv.Itoa(jobsize)
// 	user.Amount = 1
// 	user.MaxWait = 0
// 	user.MinWait = 0
// 	return user
// }

// //Type returns the type of the experiment
// func (lbe *LocustRequestExperiment) GetType() string {
// 	return lbe.Type
// }

// // SetOutputDir set the output directory for raw locust experiment results
// func (lbe *LocustRequestExperiment) SetOutputDir(directory string) {
// 	if !strings.HasSuffix(directory, "/") {
// 		directory = directory + "/"
// 	}
// 	lbe.OutputDir = directory
// }

// // SetIterationAndSample sets the current iteration and sample being evaluated
// func (lbe *LocustRequestExperiment) SetIterationAndSample(iter int, sample int) {
// 	lbe.Iteration = iter
// 	lbe.Sample = sample
// }

// //Run : runs the experiment
// func (lbe *LocustRequestExperiment) Run() (models.ExperimentResult, error) {
// 	results := lbe.Locustconfig.Run(fmt.Sprintf("%v%v-%v", lbe.OutputDir, lbe.Iteration, lbe.Sample))
// 	result := CreateLocustBarchExperimentResult(results)
// 	return result, nil
// }
