package locustwrap

func Test() {
	users := []User{
		{
			TenantID: "user1",
			Name:     "Gold",
			URL:      "http://demo.gold.svc.cluster.local:80/pushJob/700",
			Amount:   1,
			MinWait:  1,
			MaxWait:  1,
		},
		{
			TenantID: "user2",
			Name:     "silver",
			URL:      "http://demo.silver.svc.cluster.local:80/pushJob/400",
			Amount:   1,
			MinWait:  1,
			MaxWait:  1,
		},
	}

	CreateRunScript(users, "test-locust")
	c := Config{
		Name:              "go-test",
		ScriptPath:        "/tmp/test-locust",
		Users:             4,
		HatchRate:         3,
		DurationInSeconds: 100,
	}
	c.Run("/tmp/locust_test")
}
