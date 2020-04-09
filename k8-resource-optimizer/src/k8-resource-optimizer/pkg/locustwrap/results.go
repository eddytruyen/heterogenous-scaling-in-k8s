package locustwrap

import (
	"encoding/json"
	"errors"
	"fmt"
	"log"
	"strconv"
	"strings"
	"time"

	"k8-resource-optimizer/pkg/utils"
)

type Results struct {
	Name         string               `json:"name"`
	Distribution []DistributionResult `json:"Distribution"`
	Requests     []RequestResult      `json:"Requests"`
	Duration     time.Duration        `json:"Duration"`
}

type RequestResult struct {
	Name        string  `json:"Name"`
	Failures    float64 `json:"# failures,string"`
	Max         int     `json:"Max response time,string"`
	Median      int     `json:"Median response time,string"`
	Average     int     `json:"Average response time,string"`
	Min         int     `json:"Min response time,string"`
	Method      string  `json:"Method"`
	Throughput  float64 `json:"Requests/s,string"`
	Amount      int     `json:"# requests,string"`
	ContentSize int     `json:"Average Content Size,string"`
}

type DistributionResult struct {
	Name   string `json:"Name"`
	Amount int    `json:"# requests,string"`
	P50    int    `json:"50%,string"`
	P66    int    `json:"66%,string"`
	P75    int    `json:"75%,string"`
	P80    int    `json:"80%,string"`
	P90    int    `json:"90%,string"`
	P95    int    `json:"95%,string"`
	P98    int    `json:"98%,string"`
	P99    int    `json:"99%,string"`
	P100   int    `json:"100%,string"`
}

func readResultsFromJSON(pathDistribution string, pathRequests string) Results {
	var r = Results{}
	raw1 := utils.ReadRawFile(pathDistribution)
	s := string(raw1[:])
	s = strings.Replace(s, "N/A", "0", -1)
	raw1 = []byte(s)
	error1 := json.Unmarshal(raw1, &r.Distribution)
	raw2 := utils.ReadRawFile(pathRequests)
	error2 := json.Unmarshal(raw2, &r.Requests)
	if error1 != nil || error2 != nil {
		log.Panicf("Error executing json unmarshall: %v %v ", error1, error2)
	}
	return r
}

func (r Results) ExtractResultsForRequestWithPrefix(name string) ([]DistributionResult, []RequestResult, error) {
	distOut := []DistributionResult{}
	requestOut := []RequestResult{}
	found := false
	for _, d := range r.Distribution {

		if strings.HasPrefix(d.Name, ("GET " + name)) {
			found = true
			distOut = append(distOut, d)
		}
	}
	for _, d := range r.Requests {
		if strings.HasPrefix(d.Name, (name)) {
			requestOut = append(requestOut, d)
		}
	}
	if found {
		return distOut, requestOut, nil
	}

	return distOut, requestOut, errors.New("Didn't find a result for the given name %v")

}

func GetTenantDistResults(results []DistributionResult, sla string, usedNb int) DistributionResult {
	for _, r := range results {
		if r.Name == ("GET " + sla + "-" + strconv.Itoa(usedNb)) {
			return r
		}
	}
	return DistributionResult{}
}

func GetTenantReqResults(results []RequestResult, sla string, usedNb int) RequestResult {
	for _, r := range results {
		if r.Name == (sla + "-" + strconv.Itoa(usedNb)) {
			return r
		}
	}
	return RequestResult{}
}

func (r DistributionResult) String(header bool) string {
	out := ""
	if header {
		out += fmt.Sprintf("Percentage of the requests completed within given times")
		out += fmt.Sprintf("Name\t\t\t\t# reqs\t50%\t66%\t75%\t80%\t90%\t95%\t98%\t99%\t100%")
	}

	out += fmt.Sprintf("%v\t\t\t\t%v\t%v\t%v\t%v\t%v\t%v\t%v\t%v\t%v\t%v", r.Name, r.Amount, r.P50, r.P66, r.P75, r.P80, r.P90, r.P95, r.P98, r.P99, r.P100)
	return out
}

func (r RequestResult) String(header bool) string {
	out := ""
	if header {
		out += fmt.Sprintf("Name\t\t\t\t# reqs\t# fails\tAvg\t Min\tMax\tMedian\treq/s")
	}
	out += fmt.Sprintf("%v\t\t\t\t%v\t%v\t%v\t%v\t%v\t%v\t%v", r.Name, r.Amount, r.Failures, r.Average, r.Min, r.Max, r.Median, r.Throughput)
	return out
}

func getField(name string, rr RequestResult, dr DistributionResult) (error, string, int, float64) {
	if name == "50%" {
		return nil, "int", dr.P50, 0.0
	}
	if name == "66%" {
		return nil, "int", dr.P66, 0.0
	}
	if name == "75%" {
		return nil, "int", dr.P75, 0.0
	}
	if name == "80%" {
		return nil, "int", dr.P80, 0.0
	}
	if name == "90%" {
		return nil, "int", dr.P90, 0.0
	}
	if name == "95%" {
		return nil, "int", dr.P95, 0.0
	}
	if name == "98%" {
		return nil, "int", dr.P98, 0.0
	}
	if name == "99%" {
		return nil, "int", dr.P99, 0.0
	}
	if name == "100%" {
		return nil, "int", dr.P100, 0.0
	}

	if name == "Failures" {
		return nil, "float", 0, rr.Failures
	}
	if name == "Max" {
		return nil, "int", rr.Max, 0.0
	}
	if name == "Median" {
		return nil, "int", rr.Median, 0.0
	}
	if name == "Average" {
		return nil, "int", rr.Average, 0.0
	}
	if name == "Min" {
		return nil, "int", rr.Min, 0.0
	}

	if name == "Throughput" {
		return nil, "float", 0, rr.Throughput
	}
	if name == "Amount" {
		return nil, "int", rr.Amount, 0.0
	}
	if name == "ContentSize" {
		return nil, "int", rr.ContentSize, 0.0
	}

	return errors.New("field name not found"), "", 0, 0.0

}
