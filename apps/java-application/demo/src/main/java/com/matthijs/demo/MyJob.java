package com.matthijs.demo;


import java.util.UUID;
import java.util.concurrent.CompletableFuture;

public class MyJob {

    private CompletableFuture<String> future;
    public int todos = 0;
    public int totalTasks = 0;
    public UUID id;


    public MyJob(int amountOfTasks){
        this.totalTasks = amountOfTasks;
        this.todos = amountOfTasks;
        this.future = new CompletableFuture<>();
        this.id = UUID.randomUUID();
    }

    public synchronized void completeTask(){
        this.todos--;
        if(todos <= 0){
            this.future.complete("completed all tasks");
        }
    }

    public synchronized boolean isCompleted() {
        return todos <= 0;
    }

    public CompletableFuture<String> getFuture() {
        return future;
    }
}
