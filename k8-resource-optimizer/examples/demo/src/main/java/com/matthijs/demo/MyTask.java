package com.matthijs.demo;
import java.util.Date;
import java.util.UUID;

public class MyTask {

    public UUID id;
    public long arrivalQueueTime;
    public long ackQueueTime;
    public long leaveQueueTime;
    public long responseTime;
    public UUID jobId;
    public String task;



    public MyTask(){
        this.id = UUID.randomUUID();
        this.task = "CPU";
        Date d = new Date();
        this.arrivalQueueTime = d.getTime();
        this.jobId = null;
    }

    public MyTask(UUID jobId){
        this.id = UUID.randomUUID();
        this.task = "CPU";
        Date d = new Date();
        this.arrivalQueueTime = d.getTime();
        this.jobId = jobId;
    }

    public void leftQueue(){
        Date d = new Date();
        this.leaveQueueTime = d.getTime();
    }



    public void markAck(){
        Date d = new Date();
        this.ackQueueTime =  d.getTime();
        this.responseTime =  this.ackQueueTime - this.arrivalQueueTime;
    }

    public MyTask(boolean empty){
        if(empty){
            this.id = null;
        }
    }

    public long getResponsTime(){
        return  this.responseTime;
    }

    @Override
    public String toString() {
        return "{id=" + this.id +
                ",task=" + this.task+
                "}";
    }
}
