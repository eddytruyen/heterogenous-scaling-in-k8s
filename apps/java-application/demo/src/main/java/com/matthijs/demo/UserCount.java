package com.matthijs.demo;

import com.matthijs.rabbit.Message;
import com.matthijs.rabbit.MessageSender;
import com.matthijs.rabbit.RabbitConfig;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import java.util.UUID;

@Component
public class UserCount {

    @Autowired
    private MessageSender sender;
    @Value("${pod.name}")
    private String podName;
    @Value("${pod.namespace}")
    private String namespace;

    private static final Logger log = LoggerFactory.getLogger(SimpleController.class);

    public UserCount() {
    }

    public void loginUser() {

        Message message = new Message(namespace, podName,"added");
        sender.sendMessage(message, RabbitConfig.ROUTING_KEY_JOB_ADDED);
//        log.info(message.toString());
        log.info("Added user.");

    }

    public void logoutUser() {

        Message message = new Message(namespace, podName,"completed");
        sender.sendMessage(message, RabbitConfig.ROUTING_KEY_JOB_COMPLETED);
//        log.info(message.toString());
        log.info("Removed user.");
    }
}
