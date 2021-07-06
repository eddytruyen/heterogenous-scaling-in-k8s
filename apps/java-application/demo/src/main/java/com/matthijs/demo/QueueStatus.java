package com.matthijs.demo;


import java.util.ArrayList;
import java.util.Collection;

public class QueueStatus {

    public int queueLength;
    public int acklength;
    public double arrivalRate;
    public double processingRate;
    public double outputRate;
    public double reponseTime;
    public Collection<MyJob> jobs;

    public QueueStatus(){
        queueLength = 0;
        acklength = 0;
        arrivalRate = 0;
        processingRate = 0;
        outputRate = 0;
        jobs = null;
    }

}
