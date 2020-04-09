package com.matthijs.consumer;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Async;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;
import org.springframework.web.client.ResourceAccessException;


import java.util.UUID;

@Component
public class Consumer {

    @Autowired
    private ConsumerService cs;
    private static final Logger log = LoggerFactory.getLogger(Consumer.class);


    public void consume(){
        log.info("check for tasks");
        UUID last_task = null;
        try{
            MyTask task = cs.pullTask(last_task);
            while(task.id != null) {
                //log.info(task.toString());
                if (task.task.equals("CPU")) {
                    //log.info("pulled task");
                    CPUStress test = new CPUStress(150);
                    test.run();
                }
                last_task = task.id;
                task = cs.pullTask(last_task);
            }
            log.info("stop check for tasks");

        }catch (ResourceAccessException e){
            log.info("could not connect to queue " + e.getMessage().toString());
        }
    }


    class ConsumerThread implements Runnable {
        private UUID last_task = null;
        private int nr;

        public ConsumerThread(int nr){
            this.nr = nr;
        }

        @Override
        public void run() {
            log.info("Running runnale " + this.nr);

        }
    }


}
