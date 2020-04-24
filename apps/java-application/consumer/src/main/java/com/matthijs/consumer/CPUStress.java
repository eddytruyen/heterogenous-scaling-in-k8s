package com.matthijs.consumer;


import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class CPUStress {

    private int stressSize;
    public static final Logger log = LoggerFactory.getLogger(CPUStress.class);
    private volatile long result;


    public CPUStress(int stresssize){
        this.stressSize = stresssize;

    }


    public float run(){
        if(this.stressSize != 0){
            result = 0l;
            for(int i =0 ; i < 100 * this.stressSize; i++){
                result = fac(30);
            }
        }
        return result;
    }

    private long fac(int n){
        if(n==1) {
            return 1;
        }
        else{
            long r =  fac(n-1);
            return r * n;
        }
    }
}
