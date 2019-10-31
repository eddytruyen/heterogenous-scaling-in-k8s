package com.matthijs.demo;

import com.matthijs.rabbit.Message;
import com.matthijs.rabbit.MessageSender;
import com.matthijs.rabbit.RabbitConfig;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;


import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;

public class MyQueue {
    private static final Logger log = LoggerFactory.getLogger(MyQueue.class);
    private ArrayList<MyTask> queue;
    private HashMap<UUID, MyTask> ackSet;
    public HashMap<UUID, MyJob> ackJobs;
    private ArrayList<MyTask> finishedTasks;


//    @Autowired
//    private MessageSender sender;
//    @Value("${pod.name}")
//    private String podName;
//    @Value("${pod.namespace}")
//    private String namespace;

    public MyQueue() {
        this.queue = new ArrayList<>();
        this.ackSet = new HashMap<>();
        this.finishedTasks = new ArrayList<>();
        this.ackJobs = new HashMap<>();
    }

    public int getLength() {
        return this.queue.size();
    }

    public double getArrivalRate() {
        MyTask t;
        int size = this.queue.size();
        if (size == 0) return 0.0;
        if (size == 1) return 1.0;
        double firstInQueue = (t = this.queue.get(0)) != null ? t.arrivalQueueTime : 0;
        double lastInQueue = (t = this.queue.get(size - 1)) != null ? t.arrivalQueueTime : 0;
        log.info("arrival rate {},{},{}" + firstInQueue, lastInQueue, (lastInQueue - firstInQueue));
        return ((double) size) / ((lastInQueue - firstInQueue) / 60000);
    }

    public double getProcessingRate() {
        MyTask t;
        int size = this.finishedTasks.size();
        if (size == 0) return 0.0;
        if (size == 1) return 1.0;
        double firstInQueue = (t = this.finishedTasks.get(0)) != null ? t.ackQueueTime : 0;
        double lastInQueue = (t = this.finishedTasks.get(size - 1)) != null ? t.ackQueueTime : 0;
        log.info("processing rate {},{},{}" + firstInQueue, lastInQueue, (lastInQueue - firstInQueue));
        return ((double) size) / ((lastInQueue - firstInQueue) / 60000);
    }

    public double getResponseTime() {
        long totalResponseTime = 0l;
        int total = 0;
//        for(MyTask t: finishedTasks){
//            totalResponseTime += t.getResponsTime();
//            total++;
//        }

        if (!finishedTasks.isEmpty()) {
            total++;
            totalResponseTime = finishedTasks.get(finishedTasks.size() - 1).getResponsTime();
        }
        if (total == 0) return 0;
        return ((double) totalResponseTime) / total;
    }

    public double getQueueOutputRate() {
        MyTask t;
        int size = this.finishedTasks.size();
        if (size == 0) return 0.0;
        if (size == 1) return 1.0;
        double firstInQueue = (t = this.finishedTasks.get(0)) != null ? t.leaveQueueTime : 0;
        double lastInQueue = (t = this.finishedTasks.get(size - 1)) != null ? t.leaveQueueTime : 0;
        log.info("output rate {},{},{}" + firstInQueue, lastInQueue, (lastInQueue - firstInQueue));
        return ((double) size) / ((lastInQueue - firstInQueue) / 60000);
    }


    public void addNewTask(int tasks) {

        for (int i = 0; i < tasks; i++) {
            this.queue.add(new MyTask());
        }
        UUID id = UUID.randomUUID();
//        Message message = new Message(id, tasks, namespace, podName,"added");
//        sender.sendMessage(message, RabbitConfig.ROUTING_KEY_JOB_ADDED);
//        log.info(message.toString());
        log.info("Added " + tasks + " tasks.");

    }

    private synchronized void addTask(MyTask t) {
        this.queue.add(t);
    }

    private synchronized MyTask getFirstTask() {
        if (!this.queue.isEmpty()) {

            return this.queue.remove(0);
    }
    else{
        return null;
        }
    }

    public void addNewJob(MyJob job) {
        this.ackJobs.put(job.id, job);
        for (int i = 0; i < job.totalTasks; i++) {
            addTask(new MyTask(job.id));
        }
//        Message message = new Message(job.id, job.totalTasks, namespace, podName,"added");
//        sender.sendMessage(message, RabbitConfig.ROUTING_KEY_JOB_ADDED);
        log.info("New job added with " + job.totalTasks + "tasks");
    }


    public MyTask getFirstTask(UUID piggybackedAck) {
        if (piggybackedAck != null) this.markAck(piggybackedAck);
        if (!this.queue.isEmpty()) {
            MyTask t = getFirstTask();
            if (t != null) {
                t.leftQueue();
                this.ackSet.put(t.id, t);
                return t;
            }

        }
        return null;
    }

    private void markAck(UUID ack) {
        MyTask t = this.ackSet.remove(ack);
        if (t != null && t.jobId != null) checkJobCompleted(t.jobId);
        if (t != null) t.markAck();
        //this.finishedTasks.add(t);
    }

    private void checkJobCompleted(UUID jobid) {
        MyJob job = this.ackJobs.get(jobid);
        if (job != null) {
            job.completeTask();
            if (job.isCompleted()) {
//                Message message = new Message(job.id, job.totalTasks, namespace, podName,"completed");
//                sender.sendMessage(message, RabbitConfig.ROUTING_KEY_JOB_COMPLETED);
                this.ackJobs.remove(jobid);
            }
        }
    }
}
