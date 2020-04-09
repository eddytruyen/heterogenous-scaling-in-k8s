package utilityfunc

import (
	"log"

	"k8-resource-optimizer/pkg/models"
)

type UtilityFunc func(sla models.SLA, result *models.ConfigResult) (float64, error)

func InitializeUtilityFunc(name string) UtilityFunc {
	switch name {
	case "resourceBased":
		return ResourceBasedUtilityFunc
	case "resourceBasedTest":
		return ResourceBasedUtilityFuncTest
	case "alphabetBased":
		return AlphabetBasedUtilityFunc
	default:
		log.Printf("InitializeUtilityFunc: unknown function %v", name)
		return nil
	}
}
