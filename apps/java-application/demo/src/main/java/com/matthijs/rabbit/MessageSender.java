package com.matthijs.rabbit;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class MessageSender {

    private final RabbitTemplate rabbitTemplate;
    private static final Logger logger = LoggerFactory.getLogger(MessageSender.class);

    @Autowired
    public MessageSender(RabbitTemplate rabbitTemplate) {
        this.rabbitTemplate = rabbitTemplate;
    }

    public void sendMessage(Message message, String routingKey) {
        String exchangeName = RabbitConfig.EXCHANGE_NAME;
        logger.info("Sending message in exchange: "+exchangeName+" with topic: "+routingKey);
        try{
        this.rabbitTemplate.convertAndSend(exchangeName, routingKey, message);}
        catch (Exception e){
            logger.info("There was an error when sending the message: "+e);
        }
    }
}
