#### Setup ####

# Clear workspace
rm(list = ls())

# Import packages
library("reshape2")
library("ggplot2")
library("gridExtra")
library("plyr")
library(mosaic)
library(mosaicCore)
library(mosaicData)
library(mosaicCalc)
library(data.table)

# Directory of r-file
setwd("/home/arno/docker-thesis/r/")

#### Data aggregation ####

# Load raw CSV
x=read.csv(file="./data/10-15/cpu_data.csv", header = TRUE) 
y=read.csv(file="./data/10-15/response_data.csv", header = TRUE)

# Create some data to simplify 
cpu_usage = unlist(x["Usage.GOLD.consumer"])
cpu_request = unlist(x["Request.GOLD.consumer"])
cpu_tenants = unlist(x["Tenants"])
response_tenants = unlist(y["Tenants"])
response_time = unlist(y["Response_Time"])
cpu_perc = cpu_usage / cpu_request
cpu_frame = data.frame(cpu_tenants, cpu_usage, cpu_request)
response_frame = data.frame(response_tenants, response_time)
percentile_frame <- aggregate(response_time ~ response_tenants, data=response_frame, FUN=quantile, c(.99))
avg_cpu_frame <- aggregate(cpu_perc ~ cpu_tenants, data=cpu_frame, mean)

#### Function calculation####

# Function response data tenants
f_resp_tenants = fitModel(response_time~A*response_tenants+B, data = percentile_frame)

# Function CPU% tenants
f_cpu_perc <- fitModel(cpu_perc ~ (A*cpu_tenants)/(cpu_tenants+B), data=avg_cpu_frame)

# Function CPU usage tenants
f_cpu_usage = fitModel(cpu_usage~A*cpu_tenants + B, data = cpu_frame)
f_cpu_req = fitModel(cpu_request~A*cpu_tenants + B, data = cpu_frame)

#### Plotting ####

# Plot f_resp_tenants
plotPoints(response_time~response_tenants, xlim=c(0,20), ylim=c(0,2800), add=FALSE, col="blue", data=response_frame)
plotPoints(response_time~response_tenants, xlim=c(0,20), ylim=c(0,2800), add=TRUE, col="red", data=percentile_frame)
plotFun(f_resp_tenants(response_tenants)~response_tenants, add=TRUE, col="red")

# Plot CPU percentage
plotPoints(cpu_perc~cpu_tenants, main="cpu ls", xlim=c(0,12), add=FALSE, data=cpu_frame)
plotPoints(cpu_perc~cpu_tenants, main="cpu ls", ylimlim=c(0,4000), add=TRUE, data=cpu_frame)
plotFun(f_cpu_perc(cpu_tenants)~cpu_tenants, add=TRUE, col="red")

# Plot CPU limit and request
plotPoints(cpu_usage~cpu_tenants, main="Linear", xlim=c(0,19), ylim=c(0,4000))
plotPoints(cpu_usage~cpu_tenants, main="Linear", add=TRUE, ylim=c(0,4000))
plotPoints(cpu_request~cpu_tenants, xlim=c(0,20), add=TRUE, col="red")
plotFun(f_cpu_usage(cpu_tenants)~cpu_tenants, add=TRUE, col="green")
plotFun(f_cpu_req(cpu_tenants)~cpu_tenants, add=TRUE, col="orange")

## Let's say 15 users:

ten = 15

s <- f_cpu_usage(ten)
t <- f_resp_tenants(ten)
u <- f_cpu_req(ten)
v <- f_cpu_perc(ten)

cpu_req <- (s*t)/2500
cpu_lim1 <- f_cpu_req(ten)
cpu_lim2 <- cpu_req/v
cpu_lim <- min(c(cpu_lim1, cpu_lim2))

pods <- cpu_lim%/%250

if (cpu_lim%%250 > 50) {
  pods <- pods+1
}

coef(f_cpu_perc)
coef(f_cpu_req)
coef(f_cpu_usage)
coef(f_resp_tenants)

