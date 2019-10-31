package main
import (
	"sync"
	"log"
)

type ApplicationState struct{
	tenants   	map[string]int
	mux 		sync.Mutex
}

var appState = ApplicationState{tenants: map[string]int{"gold": 0,"bronze":0}}

// func initAppState(){
// 	t := map[string]int{"gold": 0,"bronze":0}
// 	appState:= ApplicationState{tenants: t}
// }

// Inc increments the counter for the given key.
func (s *ApplicationState) increaseTenantCount(sla string) {
	s.mux.Lock()
	// Lock so only one goroutine at a time can access the map c.v.
	s.tenants[sla]++
	s.mux.Unlock()
}

func (s *ApplicationState) decreaseTenantCount(sla string) {
	s.mux.Lock()
	// Lock so only one goroutine at a time can access the map c.v.
	s.tenants[sla]--
	s.mux.Unlock()
}

func addTenant(sla string) {
	appState.increaseTenantCount(sla)
}

func removeTenant(sla string) {
	appState.decreaseTenantCount(sla)
}

func (s *ApplicationState) getTenantCount()  map[string]int{
	s.mux.Lock()
	// Lock so only one goroutine at a time can access the map c.v.
	defer s.mux.Unlock()
	return s.tenants
}

func getState()  map[string]int{
	state :=appState.getTenantCount()
	log.Printf("%v", state)	

	return state
}

