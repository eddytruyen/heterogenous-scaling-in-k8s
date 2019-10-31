package com.matthijs;

import com.matthijs.demo.MyQueue;
import com.matthijs.demo.UserCount;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;

@SpringBootApplication
public class DemoApplication {


	public static void main(String[] args) {
		SpringApplication.run(DemoApplication.class, args);
	}

	@Bean
	public MyQueue getQueue(){
		return new MyQueue();
	}

	@Bean
	public UserCount getUserCount(){
		return new UserCount();
	}
}
