package models

import (
	"errors"
	"fmt"
	"log"
)

type SLA struct {
	Name        string                      `yaml:"name"`
	SLOs        map[interface{}]interface{} `yaml:"slos"`
	NbOfTenants int                         `yaml:"nbOfTenants"`
	ChartName   string                      `yaml:"chartName"`
	Parameters  []Parameter                 `yaml:"parameters"`
}

type Parameter struct {
	Name        string
	Resource    string
	Searchspace Searchspace
	Prefix      string
	Suffix      string
}

type Searchspace struct {
	Min         int
	Max         int
	Granularity int
}

func (s *Searchspace) getGranularity() int {
	if s.Granularity == 0 {
		return 1
	}
	return s.Granularity
}

type Chart struct {
	Name    string `yaml:"name"`
	DirPath string `yaml:"chartdir"`
}

func (s *SLA) GetSLO(name string) (interface{}, error) {
	if val, ok := s.SLOs[name]; ok {
		return val, nil
	}
	log.Printf("SLA did not contain SLO: %v map contains: %v", name, s.SLOs)
	return nil, errors.New("SLA did not contain SLO: " + name)
}

func (c Chart) Equal(c2 Chart) bool {
	return c.Name == c2.Name
}

func (s *SLA) ReportParametersHeader() string {
	out := ""
	for _, p := range s.Parameters {
		out += fmt.Sprintf("\t%v", p.Name)
	}
	return out
}
func (s *SLA) GetParameter(name string) (*Parameter, error) {
	for i, p := range s.Parameters {
		if p.Name == name {
			return &s.Parameters[i], nil
		}
	}
	return nil, fmt.Errorf("SLA: does not contain parameter: %v", name)
}
