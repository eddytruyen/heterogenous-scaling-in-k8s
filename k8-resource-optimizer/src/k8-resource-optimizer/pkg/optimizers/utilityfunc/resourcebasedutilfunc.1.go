package utilityfunc

import (
	"strconv"

	"k8-resource-optimizer/pkg/models"
)

func ResourceBasedUtilityFuncTest(sla models.SLA, result *models.ConfigResult) (score float64, err error) {
	if result.GetExperimentResult().Violates(sla) {
		return 0, nil
	}
	testedConfig := result.GetConfig()
	// for _, par := range sla.Parameters {
	// 	setting, err1 := testedConfig.GetParameterSetting(par.Name)
	// 	if err1 != nil {
	// 		err = errors.New("ResourceBasedUtilityFunc")
	// 		return
	// 	}
	// 	settingValue := setting.GetValue()
	// 	settingInt, err2 := strconv.Atoi(settingValue.String())
	// 	if err2 != nil {
	// 		err = errors.New("ResourceBasedUtilityFunc")
	// 		return
	// 	}
	// 	score += float64(par.Searchspace.Max) / float64(settingInt)
	// }
	cpuPara, err := sla.GetParameter("workerCPU")
	cpuSetting, _ := testedConfig.GetParameterSetting("workerCPU")

	cpuSettingValue, _ := strconv.Atoi(cpuSetting.GetValue().String())

	replicaPara, _ := sla.GetParameter("workerReplicas")
	replicaSetting, _ := testedConfig.GetParameterSetting("workerReplicas")
	replicaSettingValue, _ := strconv.Atoi(replicaSetting.GetValue().String())
	max := float64(cpuPara.Searchspace.Max) * float64(replicaPara.Searchspace.Max)
	set := (float64(replicaSettingValue) * float64(cpuSettingValue))
	score = 1 - (set / (max + 1))
	return
}
