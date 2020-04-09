package com.matthijs.consumer;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.UUID;

@Service
public class ConsumerService {

    @Value("$(DEMO_SERVICE_SERVICE_HOST)")
    private  String queueHost;

    @Value("${DNS_NAMESPACE}")
    private String namespace;

    private final RestTemplate restTemplate;
    private static final Logger log = LoggerFactory.getLogger(ConsumerService.class);

    public ConsumerService(RestTemplateBuilder restTemplateBuilder) {
        this.restTemplate = new RestTemplate();
    }

    @Autowired
    Consumer consumer;

    public MyTask pullTask(UUID piggyback) {
        //String namespace = System.getenv("DNS_NAMESPACE");
        //log.info("namespace : " + namespace);
        if(namespace != null)
            queueHost = "demo." + namespace + ".svc.cluster.local:80";
        else
            queueHost = "localhost:8080";
        //log.info("Host: " + queueHost);
        if(piggyback != null)
            return this.restTemplate.getForObject("http://"+queueHost+"/pull?ack="+piggyback.toString(), MyTask.class);
        else
            return this.restTemplate.getForObject("http://"+queueHost+"/pull", MyTask.class);
    }


    @Scheduled(fixedRate=1000)
    public void consumeTask(){
        log.info("schedule consume for tasks");
        consumer.consume();
    }

}
