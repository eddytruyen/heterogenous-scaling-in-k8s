package models

type ExperimentResult interface {
	Violates(sla SLA) bool
	GetResultForSLA(sla SLA) ExperimentResult
	GetType() string
	Report(sla SLA) (string, string)
}

type Experiment interface {
	Run() (ExperimentResult, error)
	GetType() string
	SetIterationAndSample(iteration int, sample int)
	SetOutputDir(dir string)
}
