package experiments

import (
	"fmt"
	"log"
	"reflect"
	"strconv"

	"k8-resource-optimizer/pkg/locustwrap"
	"k8-resource-optimizer/pkg/models"
)

//LocustBatchExperimentResult : ExperimentResult for all tenants of all Namespaces combined
type LocustBatchExperimentResult struct {
	Results locustwrap.Results
	Type    string
}

// CreateLocustBarchExperimentResult creates a new instance
func CreateLocustBarchExperimentResult(results locustwrap.Results) (out LocustBatchExperimentResult) {
	out.Results = results
	out.Type = "LocustBatchExperimentResult"
	return out
}

// GetType returns the type of the experiment
func (lber LocustBatchExperimentResult) GetType() string {
	return lber.Type
}

// Violates checks if a experiment result violates
// since the result is not sla specific see LocustBatchInnerExperimentResult it will always return false
func (lber LocustBatchExperimentResult) Violates(sla models.SLA) bool {
	return false
}

// GetResultForSLA returns the result of the experiments for tentants of a given SLA/namespace
func (lber LocustBatchExperimentResult) GetResultForSLA(sla models.SLA) models.ExperimentResult {
	result := LocustBatchInnerExperimentResult{}
	result.Type = "LocustBatchInnerExperimentResult"
	result.distResult = make(map[string]locustwrap.DistributionResult)
	result.reqResult = make(map[string]locustwrap.RequestResult)
	result.slaName = sla.Name
	for tenantNb := 0; tenantNb < sla.NbOfTenants; tenantNb++ {
		tenantName := sla.Name + "-" + strconv.Itoa(tenantNb)
		distResults, reqResults, err := lber.Results.ExtractResultsForRequestWithPrefix(tenantName)
		if err != nil {
			log.Panicf("LocustBatchExperimentResult: unable to extract results for sla %v", tenantName)
		}
		if len(distResults) != 1 || len(reqResults) != 1 {
			log.Panicf("LocustBatchExperimentResult: unable to extract results for sla %v", tenantName)
		}
		result.distResult[tenantName] = distResults[0]
		result.reqResult[tenantName] = reqResults[0]
	}

	return result
}

func (lber LocustBatchExperimentResult) Report(sla models.SLA) (string, string) {

	return "", ""
}

// LocustBatchInnerExperimentResult for all tenants of a specific namespace
type LocustBatchInnerExperimentResult struct {
	slaName    string
	distResult map[string]locustwrap.DistributionResult
	reqResult  map[string]locustwrap.RequestResult
	Type       string
}

func (lber LocustBatchInnerExperimentResult) GetType() string {
	return lber.Type
}

// Violates checks if a experiment result violates the required SLA
func (lber LocustBatchInnerExperimentResult) Violates(sla models.SLA) bool {
	test, err := sla.GetSLO("throughput")
	if err != nil {
		log.Panicf("LocustBatchInnerExperimentResult: unable to extract throughput SLO form sla %v", sla.Name)
	}
	requiredTroughput, ok := test.(float64)
	if !ok {
		log.Panicf("LocustBatchInnerExperimentResult: unable parse throughput SLO to float, %v, %v", test, reflect.TypeOf(test))
	}
	for tenantNb := 0; tenantNb < sla.NbOfTenants; tenantNb++ {
		tenantName := sla.Name + "-" + strconv.Itoa(tenantNb)
		if lber.reqResult[tenantName].Throughput < requiredTroughput {
			return true
		}
	}
	return false
}

// GetResultForSLA returns the result of the experiments for tentants of a given SLA/namespace
// in this case this is already the same result
func (lber LocustBatchInnerExperimentResult) GetResultForSLA(sla models.SLA) models.ExperimentResult {
	return lber
}

func (lber LocustBatchInnerExperimentResult) Report(sla models.SLA) (header string, data string) {
	for tenantNb := 0; tenantNb < sla.NbOfTenants; tenantNb++ {
		header += fmt.Sprintf("Tenant-%v Throughtput\tTenant-%v avg Latency\tTenant-%v #Failures\t", tenantNb, tenantNb, tenantNb)
		tenantName := sla.Name + "-" + strconv.Itoa(tenantNb)
		data += fmt.Sprintf("%v\t%v\t%v\t", lber.reqResult[tenantName].Throughput, lber.reqResult[tenantName].Average, lber.reqResult[tenantName].Failures)
	}
	return
}
