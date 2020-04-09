package locustwrap

import (
	"log"
	"os"
	"os/exec"
	"strconv"
	"strings"
	"time"

	"k8-resource-optimizer/pkg/utils"
)

const tmpDir = "/tmp/locustwrap/"

type Config struct {
	Name              string
	ScriptPath        string
	Users             int
	HatchRate         int
	DurationInSeconds int
}

type User struct {
	TenantID string
	Name     string
	URL      string
	Amount   int
	MinWait  int
	MaxWait  int
}

func check(e error) {
	if e != nil {
		log.Panicf("Error: %v", e)
	}
}

func CreateRunScript(users []User, name string) string {

	scriptPath := tmpDir + name + ".py"
	utils.CreateDirWithNecessaryParentsIfnotExists(tmpDir)
	f, err := os.Create(scriptPath)
	check(err)
	f.WriteString("from locust import HttpLocust, TaskSet, task \n")
	amount := 0
	check(err)
	for _, user := range users {
		userString := strings.Replace(userTemplate, "#TENANTID", user.TenantID, -1)
		userString = strings.Replace(userString, "#URL", user.URL, -1)
		userString = strings.Replace(userString, "#NAME", user.Name, -1)
		userString = strings.Replace(userString, "#MIN", strconv.Itoa(user.MinWait), -1)
		userString = strings.Replace(userString, "#MAX", strconv.Itoa(user.MaxWait), -1)
		userString = strings.Replace(userString, "#WEIGHT", strconv.Itoa(user.Amount), -1)
		amount += user.Amount
		f.WriteString(userString)
		f.WriteString("\n")
	}

	f.Sync()
	return scriptPath
}

func (c Config) Run(outputDir string) Results {
	//create running and parsing script
	utils.CreateDirWithNecessaryParentsIfnotExists(tmpDir)
	createNecessaryFiles(tmpDir)
	//create output dir
	utils.CreateDirWithNecessaryParentsIfnotExists(outputDir)

	if !strings.HasSuffix(outputDir, "/") {
		outputDir = outputDir + "/"
	}
	arg := []string{
		tmpDir + "runAndParse.sh",
		c.ScriptPath,
		outputDir + "results",
		strconv.Itoa(c.Users),
		strconv.Itoa(c.HatchRate),
		strconv.Itoa(c.DurationInSeconds),
		tmpDir + "parser.py",
	}
	log.Printf("\t\tLocust: running with parameters: %v", arg)
	start := time.Now()
	com := exec.Command("/bin/sh", arg...)
	out, err := com.Output()
	if err != nil {
		log.Panicf("Error starting locust: %v, %v", err, out)
	}
	end := time.Now()

	results := readResultsFromJSON(outputDir+"results_distribution.csv.json", outputDir+"results_requests.csv.json")
	results.Name = c.Name
	results.Duration = end.Sub(start)
	// log.Printf("results: %v", results)
	return results
}
