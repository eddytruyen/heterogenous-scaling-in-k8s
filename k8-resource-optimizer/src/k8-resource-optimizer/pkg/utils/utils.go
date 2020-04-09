package utils

import (
	"encoding/json"
	"io/ioutil"
	"log"
	"os"
	"os/exec"
	"runtime"
	"strings"

	yaml "gopkg.in/yaml.v2"
)

// CreateDirWithNecessaryParentsIfnotExists creates a directory in the given path
// Including all necessary parents
func CreateDirWithNecessaryParentsIfnotExists(path string) error {
	err := os.MkdirAll(path, os.ModePerm)
	if err != nil {
		log.Printf("Utils: CreateDirWithNecessaryParentsIfnotExists: Error creating dir: %v \n error: %v ", path, err)
		return err
	}
	return nil
}

// CopyDirContentToOtherDir copies to contents of a given directory to another directory
func CopyDirContentToOtherDir(from string, to string) error {

	if runtime.GOOS == "linux" {
		if !strings.HasSuffix(from, "/") {
			from = from + "/."
		}
		if strings.HasSuffix(to, "/") {
			to = to + "."
		}

	} else {
		if !strings.HasSuffix(from, "/") {
			from = from + "/"
		}
	}

	arg := []string{
		"-r",
		from,
		to,
	}

	_, err := exec.Command("cp", arg...).Output()
	if err != nil {
		log.Printf("Utils: CopyDirContentToOtherDir: from: %v to: %v err: %v ", from, to, err)
		return err
	}

	return nil
}

// ReadYamlValuesFileAsMap loads a helm value file as a map
func ReadYamlValuesFileAsMap(path string) (map[interface{}]interface{}, error) {
	raw, err := ioutil.ReadFile(path)
	valuesAsMap := make(map[interface{}]interface{})
	err = yaml.Unmarshal(raw, &valuesAsMap)
	if err != nil {
		log.Printf("Utils: ReadYamlValuesFileAsMap: error unmarshaling chart values path: %v err: %v", path, err)
		return valuesAsMap, err
	}
	return valuesAsMap, nil
}

// WriteNewValuesToFile writes a YAML values map to a file at given path
func WriteNewValuesToFile(path string, in map[interface{}]interface{}) error {
	d, err := yaml.Marshal(&in)
	if err != nil {
		log.Printf("Utils: WriteNewValuesToFile: %v", err)
		return err
	}
	file, err2 := os.Create(path)
	if err2 != nil {
		log.Printf("Utils: WriteNewValuesToFile: file for path: %v", path)
		return err2
	}
	file.Write(d)
	defer file.Close()
	return nil
}

func RemoveDirectory(path string) error {
	err := os.RemoveAll(path)
	if err != nil {
		log.Printf("Utils: DeleteDirectory: unable to remove %v err: %v ", path, err)
		return err
	}
	return nil
}

func ReadRawFile(path string) []byte {
	raw, err := ioutil.ReadFile(path)
	if err != nil {
		log.Panicf(err.Error())
	}
	return raw
}

func WriteStringToFile(path string, towrite string) error {
	f, err := os.Create(path)
	defer f.Close()
	if err != nil {
		log.Printf("Utils: WriteStringToFile unable to write to file %v, error: %v ", path, err)
		return err
	}
	_, err2 := f.WriteString(towrite)
	if err2 != nil {
		log.Printf("Utils: WriteStringToFile unable to write to file %v, error: %v", path, err2)
		return err2
	}
	f.Sync()
	return nil
}

func WriteObjectToJSONFile(path string, obj interface{}) error {
	data, err1 := json.Marshal(obj)
	if err1 != nil {
		return err1
	}
	f, err := os.Create(path)
	defer f.Close()
	if err != nil {
		log.Printf("Utils: WriteObjectToJSONFile unable to write to file %v, error: %v ", path, err)
		return err
	}
	f.Write(data)
	return nil
}
