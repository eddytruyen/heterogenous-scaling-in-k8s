package models

import (
	"encoding/json"
	"errors"
	"fmt"
	"log"
	"math/rand"
	"strconv"
)

type ParameterValue interface {
	String() string
	Less(other ParameterValue) bool
	Greater(other ParameterValue) bool
	Equal(other ParameterValue) bool
	GetType() string
	GetValue() interface{}
}

func MinParSlice(v []ParameterValue) (ret ParameterValue) {
	if len(v) > 0 {
		ret = v[0]
	}
	for i := 1; i < len(v); i++ {
		if v[i].Less(ret) {
			ret = v[i]
		}
	}
	return
}

func MaxParSlice(v []ParameterValue) (ret ParameterValue) {
	if len(v) > 0 {
		ret = v[0]
	}
	for i := 1; i < len(v); i++ {
		if v[i].Greater(ret) {
			ret = v[i]
		}
	}
	return
}

func ShuffleParameterValue(values []ParameterValue) (ret []ParameterValue) {
	ret = make([]ParameterValue, len(values))
	perm := rand.Perm(len(values))
	for i, randIndex := range perm {
		ret[i] = values[randIndex]
	}
	return
}

type ParameterValueInt struct {
	Value int
	Type  string
}

func (p ParameterValueInt) String() string {
	return strconv.Itoa(p.Value)
}

func (p ParameterValueInt) GetType() string {
	return p.Type
}

func (p ParameterValueInt) GetValue() interface{} {
	return p.Value
}

func (p ParameterValueInt) Less(other ParameterValue) bool {
	if other.GetType() == "int" {
		intType, ok := other.(ParameterValueInt)
		if ok {
			return p.Value < intType.Value
		}

	}
	return p.String() < other.String()
}

func (p ParameterValueInt) Greater(other ParameterValue) bool {
	if other.GetType() == "int" {
		intType, ok := other.(ParameterValueInt)
		if ok {
			return p.Value > intType.Value
		}

	}
	return p.String() > other.String()
}

func (p ParameterValueInt) Equal(other ParameterValue) bool {
	if other.GetType() == "int" {
		intType, ok := other.(ParameterValueInt)
		if ok {
			return p.Value == intType.Value
		}

	}
	return p.String() == other.String()
}

func (pv *ParameterValueInt) InRange(min int, max int) bool {
	if pv.Value < min || pv.Value > max {
		return false
	}
	return true
}

func allParameterValuesInRange(min int, max int, in []ParameterValueInt) (ret []ParameterValueInt) {
	for _, pv := range in {
		if pv.InRange(min, max) {
			ret = append(ret, pv)
		}
	}
	return ret
}

type ParameterSetting struct {
	Parameter *Parameter
	Value     ParameterValue
}

func (ps *ParameterSetting) GetName() string {
	return ps.Parameter.Name
}

func (ps *ParameterSetting) GetValueAsSettingString() string {
	return ps.Parameter.Prefix + (ps.Value).String() + ps.Parameter.Suffix
}

func (ps *ParameterSetting) GetValue() ParameterValue {
	return ps.Value
}
func (ps *ParameterSetting) Equal(other ParameterSetting) bool {
	val := ps.Value
	otherVal := other.GetValue()
	return ((ps.Parameter.Name == other.Parameter.Name) && val.Equal(otherVal))
}

type Config struct {
	Settings []ParameterSetting
}

func (c *Config) AddParameterSetting(ps ParameterSetting) {
	c.Settings = append(c.Settings, ps)
}

func (c *Config) GetParameterSetting(name string) (ret ParameterSetting, err error) {

	for _, ps := range c.Settings {
		if ps.GetName() == name {
			return ps, nil
		}
	}
	err = errors.New("Config does not contain parameter: " + name)
	return
}
func (c *Config) Equal(other *Config) bool {
	for _, ps := range c.Settings {
		otherPs, err := other.GetParameterSetting(ps.GetName())
		if err != nil || !ps.Equal(otherPs) {
			return false
		}
	}
	return true
}

func (c *Config) PartOf(others []Config) bool {
	for _, other := range others {
		if c.Equal(&other) {
			return true
		}
	}
	return false
}

func (c *Config) GetParameterSettings() []ParameterSetting {
	return c.Settings
}

type ConfigResult struct {
	config *Config
	result ExperimentResult
}

func (cr *ConfigResult) GetConfig() *Config {
	return cr.config
}

func CreateConfigResult(c *Config, er ExperimentResult) (cr ConfigResult) {
	cr.config = c
	cr.result = er
	return cr
}

func (cr *ConfigResult) GetExperimentResult() ExperimentResult {
	return cr.result
}

func (s Searchspace) CreateSamples(nb int) ([]ParameterValue, error) {
	if nb <= 0 {
		return []ParameterValue{}, errors.New("nb of samples per iteration should be greater than 0")
	}
	out := make([]ParameterValue, nb)
	ranger := s.Max - s.Min // 3 - 1 = 2
	inc := ranger / nb      // 2 / 3 = 0
	if ranger < nb {
		inc = 1
		// spread
		for i := 0; i <= ranger; i++ {
			sample := s.Min + (i * inc)
			sample = (sample / s.getGranularity()) * s.getGranularity()

			out[i] = ParameterValueInt{sample, "int"}
		}
		// Remaining randomly pickec
		for i := ranger + 1; i < nb; i++ {
			sample := s.Min + rand.Intn(ranger+1)
			sample = (sample / s.getGranularity()) * s.getGranularity()
			out[i] = ParameterValueInt{sample, "int"}
		}

	} else {
		for i := 0; i < nb; i++ {
			sample := s.Min + (i * inc) + rand.Intn(inc+1)
			sample = (sample / s.getGranularity()) * s.getGranularity()
			out[i] = ParameterValueInt{sample, "int"}
		}
	}

	return out, nil
}

func (s Searchspace) Round(value int) int {
	return (value / s.getGranularity()) * s.getGranularity()
}

func (s Searchspace) EnumarateSampleSearchSpace() []ParameterValue {
	out := []ParameterValue{}
	curr := s.Min
	for curr <= s.Max {
		out = append(out, ParameterValueInt{Value: curr, Type: "int"})
		curr += s.getGranularity()
	}
	return out
}

// JSON UNMARSHALLING

func (pv *ParameterSetting) UnmarshalJSON(b []byte) error {
	// deserialize into map
	var objMap map[string]*json.RawMessage

	err := json.Unmarshal(b, &objMap)
	if err != nil {
		log.Printf("deserialized parameter error 1 %v", err)
		return err
	}

	//deserialize parameter
	var parameter Parameter
	parameter = Parameter{}
	err = json.Unmarshal(*objMap["Parameter"], &parameter)
	if err != nil {
		log.Printf("deserialized parameter error 2 %v, %v", err, pv)
		return err
	}
	pv.Parameter = &parameter

	var valueRaw map[string]*json.RawMessage
	err = json.Unmarshal(*objMap["Value"], &valueRaw)
	if err != nil {
		log.Printf("deserialized parameter error 3 %v, %v", err, pv)
		return err
	}

	var parameterType string
	err = json.Unmarshal(*valueRaw["Type"], &parameterType)

	if err != nil {
		log.Printf("deserialized parameter error 4 %v, %v", err, pv)
		return err
	}

	switch parameterType {
	case "int":
		var value ParameterValueInt
		value = ParameterValueInt{}
		err = json.Unmarshal(*objMap["Value"], &value)
		if err != nil {
			log.Printf("deserialized parameter error 5 %v, %v", err, pv)
			return err
		}
		var out ParameterValue
		out = value
		pv.Value = out

	}

	return nil

}

// Report
func (c *Config) Report() (header string, data string) {
	for i, ps := range c.Settings {
		header += fmt.Sprintf("%v", ps.GetName())
		data += fmt.Sprintf("%v", (ps.GetValue()).String())
		if (i + 1) < len(c.Settings) {
			header += "\t"
			data += "\t"
		}
	}
	return
}
