package com.matthijs.demo;


import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.RequestMapping;


import java.util.UUID;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.Future;

@RestController
public class SimpleController {
    @Autowired
    private MyQueue q;

    private static final Logger log = LoggerFactory.getLogger(SimpleController.class);

    @RequestMapping("/push")
    public String push() {
        q.addNewTask();
        return "Queue length " + q.getLength();
    }


    @RequestMapping("/pushJob/{amount}")
    public Future<String> pushJob(@PathVariable int amount){
        MyJob job = new MyJob(amount);
        q.addNewJob(job);
        return job.getFuture();
    }


    @RequestMapping("/pull")
    public MyTask pull(@RequestParam(value = "ack", defaultValue = "") String ack){
        UUID ackUUID = this.getUUIDFromString(ack);
//        if(ackUUID != null )
//            log.info("piggybacked uuid " + ackUUID);
        MyTask t = q.getFirstTask(ackUUID);
        if(t != null)
            return t;
        else
            return new MyTask(true);
    }



    @RequestMapping("/status")
    public QueueStatus QueueStatus(){
        QueueStatus s = new QueueStatus();
        s.queueLength = q.getLength();
        s.acklength = q.ackJobs.size();
        s.arrivalRate = q.getArrivalRate();
        s.processingRate = q.getProcessingRate();
        s.outputRate = q.getQueueOutputRate();
        s.reponseTime = q.getResponseTime();
        s.jobs = q.ackJobs.values();
        return s;
    }



    private UUID getUUIDFromString(String input){
        UUID ackUUID = null;
        try {
             ackUUID = UUID.fromString(input);
        }catch(IllegalArgumentException e){
            return null;
        }
        return ackUUID;
    }





}
