package com.matthijs.consumer;

import com.ryantenney.metrics.spring.config.annotation.EnableMetrics;
import com.ryantenney.metrics.spring.config.annotation.MetricsConfigurerAdapter;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.EnableAutoConfiguration;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.scheduling.annotation.EnableScheduling;


@SpringBootApplication
@EnableScheduling
//@ComponentScan(basePackageClasses = ConsumerController.class)
//@ComponentScan(basePackageClasses = SpringConfiguringClass.class)
//@EnableMetrics(proxyTargetClass = true)
public class ConsumerApplication extends MetricsConfigurerAdapter {

	public static void main(String[] args) {
		SpringApplication.run(ConsumerApplication.class, args);
	}
}
