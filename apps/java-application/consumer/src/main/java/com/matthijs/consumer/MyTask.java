package com.matthijs.consumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.UUID;

public class MyTask {

    public UUID id;
    public String task;




    @Override
    public String toString() {

        return "{id=" + this.id +
                ",task=" + this.task+
                "}";
    }


}

