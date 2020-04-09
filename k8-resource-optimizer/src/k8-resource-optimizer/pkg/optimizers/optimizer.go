package optimizers

import (
	"errors"
	"log"

	"k8-resource-optimizer/pkg/models"
	"k8-resource-optimizer/pkg/optimizers/bayesianopt"
	"k8-resource-optimizer/pkg/optimizers/bestconfig"
	"k8-resource-optimizer/pkg/optimizers/exhaustive"
	"k8-resource-optimizer/pkg/optimizers/utilityfunc"
)

type Optimizer interface {
	GetNextConfigSamples(iteration int) ([]models.Config, error)
	AddConfigResults(iteration int, results []models.ConfigResult) error
	SetUtilityFunction(utiltfunc utilityfunc.UtilityFunc)
	Report() string
}

func InitializeOptimizer(name string, sla models.SLA, nbOfiterations int, nbOfSamplesPerIteration int) (Optimizer, error) {
	switch optimizer := name; optimizer {
	case "bestconfig":
		return bestconfig.CreateBestConfigOptimzer(sla, nbOfiterations, nbOfSamplesPerIteration), nil
	case "bayesianoptimization":
		log.Fatal("Optimizer: initializeOptimizer: not yet supported")
	case "exhaustive":
		return exhaustive.CreateExhaustiveSearch(sla), nil
	case "bayesianopt":
		return bayesianopt.CreateBayesianOptimzer(sla, nbOfiterations, nbOfSamplesPerIteration), nil
	default:
		log.Fatal("Optimizer: initializeOptimizer: unknown optimizer specified")

	}
	return bestconfig.CreateBestConfigOptimzer(sla, nbOfiterations, nbOfSamplesPerIteration), errors.New("Optimizer: initializeOptimizer: unknown optimizer specified")
}
