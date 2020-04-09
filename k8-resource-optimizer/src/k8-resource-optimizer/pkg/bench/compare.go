package bench

func (b *Bench) Equal(b2 *Bench) bool {
	if len(b.Namespaces) != len(b2.Namespaces) {
		return false
	}
	for _, ns := range b.Namespaces {
		if !b2.contains(ns) {
			return false
		}
	}
	return true
}

func (b *Bench) contains(ns2 Namespace) bool {
	for _, ns := range b.Namespaces {
		if ns.Equal(ns2) {
			return true
		}
	}
	return false
}

func (ns *Namespace) Equal(ns2 Namespace) bool {
	if ns.Name == ns.Name && ns.Chart.Equal(ns2.Chart) && ns.Config.Equal(&ns2.Config) {
		return true
	}
	return false
}
