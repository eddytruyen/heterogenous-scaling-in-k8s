package main

import (
	"encoding/json"
	"fmt"
	"log"
	"math"
	"os"
	"sort"
	"strconv"

	locustwrap "github.com/MatthijsKaminski/k8-resource-optimizer/locustwrap"
)

func (sla SLA) StringSLAresults(sample int, r LocustSLAResult) string {
	out := fmt.Sprintf("SLA: %v Sample: %v \n", sla.Name, sample)
	out += "Parameters: \n " + parameterHeader() + "\n"

	for _, p := range sla.Parameters {
		out += p.string(sample) + "\n"
	}

	var keys []int

	for k, _ := range r.DistributionResults {
		keys = append(keys, k)
	}

	out += "results sorted by jobsize:\n"
	out += "Jobsize\tName\t\t\t\t# reqs\t50\t66\t75\t80\t90\t95\t98\t99\t100 \n"

	sort.Ints(keys)

	for _, k := range keys {
		for u := 0; u < sla.Amount; u++ {

			out += fmt.Sprintf("%v\t%v\n", k, locustwrap.GetTenantDistResults(r.DistributionResults[k], sla.Name, u).String(false))
		}

	}
	out += "\n"
	out += "Jobsize\tName\t\t\t\t# reqs\t# fails\tAvg\t Min\tMax\tMedian\treq/s\n"
	for _, k := range keys {
		for u := 0; u < sla.Amount; u++ {
			out += fmt.Sprintf("%v\t%v\n", k, locustwrap.GetTenantReqResults(r.RequestResults[k], sla.Name, u).String(false))
		}
	}

	out += "results sorted by tenant:\n"
	out += "Jobsize\tName\t\t\t\t# reqs\t50\t66\t75\t80\t90\t95\t98\t99\t100 \n"

	for u := 0; u < sla.Amount; u++ {
		for _, k := range keys {

			out += fmt.Sprintf("%v\t%v\n", k, locustwrap.GetTenantDistResults(r.DistributionResults[k], sla.Name, u).String(false))

		}
	}
	out += "\n"
	out += "Jobsize\tName\t\t\t\t# reqs\t# fails\tAvg\t Min\tMax\tMedian\treq/s\n"
	for u := 0; u < sla.Amount; u++ {
		for _, k := range keys {

			out += fmt.Sprintf("%v\t%v\n", k, locustwrap.GetTenantReqResults(r.RequestResults[k], sla.Name, u).String(false))
		}
	}
	return out
}

func (d *SLADecomposer) reportToFile(path string) {
	f, err := os.Create(path + "_report.txt")
	check(err)
	n3, err := f.WriteString(d.report)
	check(err)
	fmt.Printf("wrote %d bytes\n", n3)
}

func (d *SLADecomposer) appendToreport(info string) {
	d.report = d.report + info
}

func (d *SLADecomposer) summary() {
	text := "Summary per SLA\n"

	for j := range d.Slas {
		sla := &d.Slas[j]
		text += fmt.Sprintf("SLA\t%v \n", sla.Name)

		for _, p := range sla.Parameters {
			name := "Name\t"
			value := "Setting\t"
			score := "Score\t"
			throughput := "Throughput (Req/s)\t"
			iteration := "Iteration\t"
			text += fmt.Sprintf("%v%v%v%v%v\n", name, value, score, throughput, iteration)
			name = p.Name
			sort.Slice(p.PastSamples, func(i, j int) bool {
				return p.PastSamples[i].Value < p.PastSamples[j].Value
			})
			for _, sample := range p.PastSamples {
				value = fmt.Sprintf("%v\t", sample.Value)
				score = fmt.Sprintf("%v\t", math.Round(sample.Score*100)/100)
				throughput = fmt.Sprintf("%v\t", sample.LocustResult.RequestResults[sla.Jobsize][0].Throughput)
				iteration = fmt.Sprintf("%v\t", sample.Iteration+1)
				text += fmt.Sprintf("%v\t%v%v%v%v\n", name, value, score, throughput, iteration)

			}
		}

		text += "\nITERATIONS PER PARAMETER: \n\n"
		scores := []float64{}
		for i := 0; i < d.Iterations; i++ {
			text += fmt.Sprintf("ITERATION: %v \n", i+1)
			bestScore := 0.0
			for _, p := range sla.Parameters {
				name := "Name\t"
				value := "Setting\t"
				score := "Score\t"
				throughput := "Throughput (Req/s)\t"
				iteration := "Iteration\t"
				text += fmt.Sprintf("%v%v%v%v%v\n", name, value, score, throughput, iteration)
				name = p.Name
				sort.Slice(p.PastSamples, func(i, j int) bool {
					return p.PastSamples[i].Value < p.PastSamples[j].Value
				})
				for _, sample := range p.PastSamples {
					if sample.Iteration == i {
						value = fmt.Sprintf("%v\t", sample.Value)
						score = fmt.Sprintf("%v\t", math.Round(sample.Score*100)/100)
						if sample.Score > bestScore {
							bestScore = sample.Score
						}
						throughput = fmt.Sprintf("%v\t", sample.LocustResult.RequestResults[sla.Jobsize][0].Throughput)
						iteration = fmt.Sprintf("%v\t", sample.Iteration+1)
						text += fmt.Sprintf("%v\t%v%v%v%v\n", name, value, score, throughput, iteration)
					}

				}
				// text += fmt.Sprintf("%v\n%v\n%v\n%v\n%v\n\n", name, value, score, throughput, iteration)
			}
			scores = append(scores, bestScore)

		}
		text += " best scores throughout iterations \n"
		text += "iteration\tscore\tincrease\n"

		for i := 0; i < d.Iterations; i++ {
			score := math.Round(scores[i]*100) / 100
			increase := 0.0
			if i != 0 {
				increase = math.Round((score/(math.Round(scores[i-1]*100)/100) - 1) * 100)
			}
			text += fmt.Sprintf("%v\t%v\t%v\n", i, math.Round(scores[i]*100)/100, increase)
		}

		text += "\nITERATIONS PER SAMPLE: \n\n"
		for i := 0; i < d.Iterations; i++ {
			text += fmt.Sprintf("\nITERATION: %v \n", i+1)
			header := "Score\tThroughput (Req/s)\tIteration\tSample\n"
			for j := 0; j < d.Samples; j++ {

				score := float64(0.0)
				throughput := float32(0.0)
				data := ""
				for _, p := range sla.Parameters {
					header = p.Name + "\t" + header

					for _, sample := range p.PastSamples {
						if sample.Iteration == i && sample.Nb == j {
							data = fmt.Sprintf("%v\t", sample.Value) + data
							score = math.Round(sample.Score*100) / 100

							throughput = sample.LocustResult.RequestResults[sla.Jobsize][0].Throughput

						}

					}
					// text += fmt.Sprintf("%v\n%v\n%v\n%v\n%v\n\n", name, value, score, throughput, iteration)
				}
				if j == 0 {
					text += header
				}
				data = data + fmt.Sprintf("%v\t%v\t%v\t%v\n", score, throughput, i+1, j+1)
				text += data

			}
		}
	}
	d.appendToreport(text)
}

func (d *SLADecomposer) AppendReport(text string) {
	d.report = d.report + text
}

func (d *SLADecomposer) saveJSON(iteration int) {

	m, err := json.Marshal(&d)
	if err != nil {
		log.Fatalf("error: %v", err)
	}
	// err1 := os.Remove(c.tempDir + "/values.yaml")
	path := "benchsetup-" + strconv.Itoa(iteration)
	file, err2 := os.Create(path)
	if err2 != nil {
		log.Fatalf("Scalar: could create benchResult file : %v", path)
	}
	file.Write(m)
	defer file.Close()

}

/// Pretty print

func (p Parameter) string(sample int) string {
	out := ""
	out += p.Name + "\t"
	out += strconv.Itoa(p.CurrentSamples[sample].Value) + "\t"
	out += fmt.Sprintf("%v", p.CurrentSamples[sample].Score)
	return out
}

func parameterHeader() string {
	return "Name\tValue\tScore"
}
