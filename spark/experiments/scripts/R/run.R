rm(list=ls())


library("reshape2")
library("ggplot2")
library("gridExtra")
library("plyr")

source(file="get_files.R")

options(scipen = 999)
directory="../../auto-hpa-150cpu-nop-dwl2"
workload="spark-bench"
operations=c("select * from csv", "select * from parquet", "select c from csv", "select c from parquet")
deployment="hpa-100cpu"
workloadfile="./workloads-spark.rds"


checkInputWorkloads <- function() { 
  workloads.names <- c()
  workloads <- vector("list", 0)
  names(workloads) <- workloads.names
  if (file.exists(workloadfile)) {
    workloads <- readRDS(file=workloadfile)
  }
  if (workload %in% names(workloads)) {
    if (deployment %in% names(workloads[[workload]])) {
      wl_operations=names(workloads[[workload]][[deployment]]$raw)
      if ( length(Reduce(intersect,list(wl_operations,operations)))>0) {
        stop(paste("Workload file", workload, "already has operations for deployment", deployment, "that overlap with the given operations variable"))
      }
    }
  }
  return (workloads)
}

ggplotHighestDeployment<-function(workload, deployment, metric, operation, cropLength, title, xl, yl, extend_y_lim=FALSE, y_lim_addition = 0, scalefactor=5, pc, lt, color="black",  fittedPoints = TRUE)  {
  data=get(metric, get(deployment, get(workload, workloads)))
  z=unlist(get(operation, data))
  z=z[1:cropLength]
  m1 <- matrix(c(z), ncol=cropLength, byrow=FALSE)
  d1 <- as.data.frame(m1, stringsAsFactors=FALSE)
  x=(1:cropLength)*scalefactor
  ggplot(data=d1, mapping = aes(x,z)) + 
    geom_point() +
    geom_smooth(method = "loess", span = 0.20, method.args = list(degree=1))
  return(d1)
}

plotHighestDeployment<-function(workload, deployment, metric, operation, cropLength, title, xl, yl, extend_y_lim=FALSE, y_lim_addition = 0, scalefactor=5, pc, lt, color="black")  {
  data=get(metric, get(deployment, get(workload, workloads)))
  z=unlist(get(operation, data))
  z=z[1:cropLength]
  x=(1:cropLength)*scalefactor
  #fit <- lm(z ~ x + I(x^2))
  if (extend_y_lim == TRUE) { 
    y_lim=min(unlist(z))-y_lim_addition
    plot(z~x, main=title, xlab=xl,ylab=yl, xaxp  = c(1,length(x),length(x)-1),pch=pc, lty=lt, col=color, ylim=c(0, y_lim))
  } else {
    plot(z~x, main=title, xlab=xl,ylab=yl, pch=pc, lty=lt, col=color)
  }
  lines(x, z, pch=pc, lty=lt, col=color)
  return(data)
}

plotHighestVpaDeployment<-function(workload, deployment, metric, operation, cropLength, title, xl, yl, extend_y_lim=FALSE, y_lim_addition = 0, scalefactor=5, pc, lt, color="black")  {
  data=get(metric, get(deployment, get(workload, workloads)))
  z=unlist(get(operation, data))
  z=z[1:cropLength]
  x=(1:cropLength)*scalefactor
  x2=names(get("raw", get(deployment, get(workload, workloads))))
  x3=rbind(x,x2)
  #fit <- lm(z ~ x + I(x^2))
  if (extend_y_lim == TRUE) { 
    y_lim=min(unlist(z))-y_lim_addition
    plot(z~x3, main=title, xlab=xl,ylab=yl, xaxp  = c(1,length(x),length(x)-1),pch=pc, lty=lt, col=color, ylim=c(0, y_lim))
  } else {
    plot(z~x3, main=title, xlab=xl,ylab=yl, pch=pc, lty=lt, col=color)
  }
  lines(x, z, pch=pc, lty=lt, col=color)
  return(data)
}


plotOtherDeploymentasLine<-function(workloaddata, operation, cropLength, pc, lt, scalefactor=5, color= "black") {
  z=unlist(get(operation, workloaddata))
  z=z[1:cropLength]
  x=(1:cropLength)*scalefactor
  #fit <- lm(z ~ x + I(x^2))
  points(x,z, pch=pc, lty=lt, col=color)
  lines(x,z, pch=pc, lty=lt, col=color)
}

plotOtherasLine<-function(workload, deployment, metric, operation, cropLength, pc, lt, scalefactor=5, color="black") {
  data=get(metric, get(deployment, get(workload, workloads)))
  z=unlist(get(operation, data))
  z=z[1:cropLength]
  x=(1:cropLength)*scalefactor
  #fit <- lm(z ~ x + I(x^2))
  points(x,z, pch=pc, lty=lt, col=color)
  lines(x,z, pch=pc, lty=lt, col=color)
}

plotReplicas<-function(workload, deployment, cropLength, pc, lt, scalefactor=5, color="black") {
  replicas=get("pod_replicas", get(deployment, get(workload, workloads)))
  z=unlist(replicas)
  z=z[1:cropLength]
  x=(1:cropLength)*scalefactor
  #fit <- lm(z ~ x + I(x^2))
  points(x,z, pch=pc, lty=lt, col=color)
  lines(x,z, pch=pc, lty=lt, col=color)
}

workloads=checkInputWorkloads()


runs = get_sorted_runs(directory)

for (j in operations) {
  rawdata <- vector("list", length(runs))
  rawdata.names <- names(runs)
  names(rawdata) <- rawdata.names
  for (i in names(runs)) {
    rundata <- unlist(runs[i])
    rawdata[[i]] <- c()
    for (r in rundata) {
      print(r)
      filename=paste(directory,"/",r,sep="")
      data = readLines(filename)
      number <- unlist(strsplit(data[startsWith(data,j)][1],split=",")) #[2]only retrieve metric ns
      sec <- as.numeric(number[3])/1000000000 # the number of nanoseconds is stored in the 3rd field
      print(sec)
      rawdata[[i]] <- c(rawdata[[i]],sec)
    }
  }
  workloads[[workload]][[deployment]]$raw[[j]] <- rawdata
  workloads[[workload]][[deployment]]$mean[[j]]<- lapply(rawdata, mean)
  workloads[[workload]][[deployment]]$median[[j]] <- lapply(rawdata, median)
  workloads[[workload]][[deployment]]$stdev[[j]]<- lapply(rawdata,sd)
}

replicas <- c(2,3,3,4,4,4,5,5,5,5) #auto-hpa-cpu100
workloads$`spark-bench`$`hpa-100cpu`$pod_replicas <- replicas

L=10
metric="mean"
#workload
deployment="hpa-100cpu"
operation=operations[1]
title="Horizontal auto-scaling cpu-threshold 80%"
xl="Number of tenants"
#yl=paste("95th ", metric," of response latency (ms)", sep="");
yl=paste("0.95 quantile", " of job completion time (s)", sep="");

pch1 = c(9,19,18,2,25) 
lty1 = c(1,6,25,29,134) 
col1 = c(25,134,450,25,6)


data=plotHighestDeployment(workload, deployment, metric, operation, L, title, xl, yl, pc=pch1[1], lt=lty1[1], 
                           color=col1[1], extend_y_lim = TRUE, y_lim_addition = -40, scalefactor = 1)
#redish

plotOtherDeploymentasLine(data, operations[2], L, pch1[2], lty1[2], color=col1[2], scalefactor = 1)
#magenta


plotOtherDeploymentasLine(data, operations[3], L, pch1[3], lty1[3], color=col1[3], scalefactor=1)
#black

plotOtherDeploymentasLine(data,  operations[4], L, pch1[4], lty1[4], color=col1[4], scalefactor=1)
#azur blue

plotReplicas(workload,  deployment, L, pch1[5], lty1[5], color=col1[5], scalefactor=1)


legend(x="topright", legend=c(operations,"number of pods"), 
       pch = pch1, lty = lty1, 
       col = col1, bty="n")

for (i in c(1:4)) {
  foo <- data.frame(mean=unlist(workloads[[workload]][[deployment]]$mean[[operations[i]]]),
                    sd=unlist(workloads[[workload]][[deployment]]$stdev[[operations[i]]]))
  
  segments(rbind(1:10),rbind(foo$mean - foo$sd),rbind(1:10), rbind(foo$mean + foo$sd), col=col1[i], lty=lty1[i])
  segments(rbind(0.9:9.9,0.9:9.9),rbind(foo$mean + foo$sd, foo$mean - foo$sd), rbind(1.1:10.1,1.1:10.1), rbind(foo$mean + foo$sd, foo$mean - foo$sd), col=col1[i])
  
}


#saveRDS(workloads,"workloads-spark.rds")
