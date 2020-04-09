package utilityfunc

import (
	"strconv"

	"k8-resource-optimizer/pkg/models"
)

func AlphabetBasedUtilityFunc(sla models.SLA, result *models.ConfigResult) (score float64, err error) {
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
	cpuSetting1, _ := testedConfig.GetParameterSetting("worker1CPU")

	cpuSettingValue1, _ := strconv.Atoi(cpuSetting1.GetValue().String())

	replicaSetting1, _ := testedConfig.GetParameterSetting("worker1Replicas")
	replicaSettingValue1, _ := strconv.Atoi(replicaSetting1.GetValue().String())


	// max := float64(cpuPara.Searchspace.Max) * float64(replicaPara.Searchspace.Max)
	set1 := (float64(replicaSettingValue1) * float64(cpuSettingValue1))

	cpuSetting2, _ := testedConfig.GetParameterSetting("worker2CPU")
	cpuSettingValue2, _ := strconv.Atoi(cpuSetting2.GetValue().String())

	replicaSetting2, _ := testedConfig.GetParameterSetting("worker2Replicas")
	replicaSettingValue2, _ := strconv.Atoi(replicaSetting2.GetValue().String())

	// max := float64(cpuPara.Searchspace.Max) * float64(replicaPara.Searchspace.Max)
	set2 := (float64(replicaSettingValue2) * float64(cpuSettingValue2))


	cpuSetting3, _ := testedConfig.GetParameterSetting("worker3CPU")

	cpuSettingValue3, _ := strconv.Atoi(cpuSetting3.GetValue().String())

	replicaSetting3, _ := testedConfig.GetParameterSetting("worker3Replicas")
	replicaSettingValue3, _ := strconv.Atoi(replicaSetting3.GetValue().String())

	max_pos := 3*(cpuSettingValue1+cpuSettingValue2+cpuSettingValue3)
	// max := float64(cpuPara.Searchspace.Max) * float64(replicaPara.Searchspace.Max)
	set3 := (float64(replicaSettingValue3) * float64(cpuSettingValue3))

	
	score = 1 - (set1+set2+set3)/float64(max_pos)
	return
}
