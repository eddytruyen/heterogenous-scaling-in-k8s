package exhaustive

import (
	"log"

	"k8-resource-optimizer/pkg/models"
	"k8-resource-optimizer/pkg/optimizers/utilityfunc"
)

type ExhaustiveSearch struct {
	sla models.SLA
}

func CreateExhaustiveSearch(sla models.SLA) *ExhaustiveSearch {
	ret := ExhaustiveSearch{sla}
	return &ret
}

func (es *ExhaustiveSearch) GetNextConfigSamples(iteration int) ([]models.Config, error) {
	out := []models.Config{}
	for i, par := range es.sla.Parameters {
		if i == 0 {
			for _, ps := range createAllPossibleParameterSettings(par) {
				conf := models.Config{}
				conf.AddParameterSetting(ps)
				out = append(out, conf)
			}
		} else {
			newOut := []models.Config{}
			for _, ps := range createAllPossibleParameterSettings(par) {
				for _, conf := range out {
					//range should copy the value not pass reference, use index to pass reference
					conf.AddParameterSetting(ps)
					newOut = append(newOut, conf)
				}

			}
			out = newOut
		}
	}
	log.Printf("ExhaustiveSearch: generated %v possible configurations", len(out))
	return out, nil
}
func (es *ExhaustiveSearch) AddConfigResults(iteration int, results []models.ConfigResult) error {
	return nil
}

func (es *ExhaustiveSearch) SetUtilityFunction(utiltfunc utilityfunc.UtilityFunc) {

}

func createAllPossibleParameterSettings(par models.Parameter) []models.ParameterSetting {
	out := []models.ParameterSetting{}
	for _, pv := range par.Searchspace.EnumarateSampleSearchSpace() {
		var pvOut models.ParameterValue
		pvOut = pv
		out = append(out, models.ParameterSetting{&par, pvOut})
	}
	return out
}

func (es *ExhaustiveSearch) Report() string {
	return ""
}
