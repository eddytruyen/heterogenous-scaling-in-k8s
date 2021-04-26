package com.matthijs.rabbit;

import java.io.Serializable;
import java.util.UUID;

public class Message implements Serializable {
    private String namespace;
    private String sender;
//    private UUID jobID;
//    private int jobSize;
    private String type;

    public Message(String namespace, String sender, String type) {
//        this.jobID = jobID;
//        this.jobSize = jobSize;
        this.sender = sender;
        this.namespace = namespace;
        this.type = type;

    }

    @Override
    public String toString() {
        return "Message{" +
                "namespace='" + namespace + '\'' +
                ", sender='" + sender + '\'' +
                ", type='" + type + '\'' +
                '}';
    }

    public String getNamespace() {
        return namespace;
    }

    public void setNamespace(String namespace) {
        this.namespace = namespace;
    }

    public String getSender() {
        return sender;
    }

    public void setSender(String sender) {
        this.sender = sender;
    }

    public String getType() {
        return type;
    }

    public void setType(String type) {
        this.type = type;
    }
}



