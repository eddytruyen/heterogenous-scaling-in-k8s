package com.matthijs.consumer;

import com.codahale.metrics.MetricRegistry;
import com.codahale.metrics.annotation.Counted;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class ConsumerController {


//    @Counted
    @RequestMapping("/cpu")
    public float performCPUStress(){
        CPUStress test = new CPUStress(150);
        return  test.run();
    }

    @RequestMapping("/podname")
    public String podname(){
        String name = System.getenv("MY_POD_NAME");
        return  name;
    }
}
