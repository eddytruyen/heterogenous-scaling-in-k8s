rm(list=ls())


library("reshape2")
library("ggplot2")
library("gridExtra")
library("plyr")

source(file="get_files.R")

options(scipen = 999)
directory="../../hpa-no-part"
workload="spark-bench"
operations=c("select * from csv", "select * from parquet", "select c from csv", "select c from parquet")
metrics=c("raw", "median", "mean", "quant")
deployment="hpa-no-part"
workloadfile="../workloaddata.rdf"


allocateWorkloadsVector <- function() { 
  workloads.names <- c()
  workloads <- vector("list", 0)
  names(workloads) <- workloads.names
  if (file.exists(workloadfile)) {
    workloads <- readRDS(file=workloadfile)
  }
  if (workload %in% names(workloads)) {
    if (deployment %in% names(workloads[[workload]])) {
      wl_operations=workloads[[workload]][[deployment]]$raw
      if ( length(Reduce(intersect,list(wl_operations,operations)))>0) {
        quit(paste("Workload file", workload, "already has operations for deployment", deployment, "that overlap with", operations))
      }
    }
  } else {
    tmp.names <- c(workload)
    tmp <- vector("list", 1)
    names(tmp) <- tmp.names
    workloads.names = append(workloads.names, tmp.names)
    workloads = append(workloads, tmp)
    names(workloads) = workloads.names
    names(workloads[[workload]]) <-  c()
  }
  return (workloads)
}

ggplotHighestDeployment<-function(workload, operation, metric, deployment, cropLength, title, xl, yl, extend_y_lim=FALSE, y_lim_addition = 0, scalefactor=5, pc, lt, color="black",  fittedPoints = TRUE)  {
  data=get(metric, get(operation, get(workload, workloads)))
  z=unlist(get(deployment, data))
  z=z[1:cropLength]
  m1 <- matrix(c(z), ncol=cropLength, byrow=FALSE)
  d1 <- as.data.frame(m1, stringsAsFactors=FALSE)
  x=(1:cropLength)*scalefactor
  ggplot(data=d1, mapping = aes(x,z)) + 
    geom_point() +
    geom_smooth(method = "loess", span = 0.20, method.args = list(degree=1))
  return(d1)
}

plotHighestDeployment<-function(workload, operation, metric, deployment, cropLength, title, xl, yl, extend_y_lim=FALSE, y_lim_addition = 0, scalefactor=5, pc, lt, color="black")  {
  data=get(metric, get(operation, get(workload, workloads)))
  z=unlist(get(deployment, data))
  z=z[1:cropLength]
  x=(1:cropLength)*scalefactor
  #fit <- lm(z ~ x + I(x^2))
  if (extend_y_lim == TRUE) { 
    y_lim=min(unlist(z))-y_lim_addition
    plot(z~x, main=title, xlab=xl,ylab=yl, pch=pc, lty=lt, col=color, ylim=c(0, y_lim))
  } else {
    plot(z~x, main=title, xlab=xl,ylab=yl, pch=pc, lty=lt, col=color)
  }
  lines(x, z, pch=pc, lty=lt, col=color)
  return(data)
}

plotOtherDeploymentasLine<-function(workloaddata, deployment, cropLength, pc, lt, scalefactor=5, color="black") {
  z=unlist(get(deployment, workloaddata))
  z=z[1:cropLength]
  x=(1:cropLength)*scalefactor
  #fit <- lm(z ~ x + I(x^2))
  points(x,z, pch=pc, lty=lt, col=color)
  lines(x,z, pch=pc, lty=lt, col=color)
}

plotOtherasLine<-function(workload, operation, metric, deployment, cropLength, pc, lt, scalefactor=5, color="black") {
  data=get(metric, get(operation, get(workload, workloads)))
  z=unlist(get(deployment, data))
  z=z[1:cropLength]
  x=(1:cropLength)*scalefactor
  #fit <- lm(z ~ x + I(x^2))
  points(x,z, pch=pc, lty=lt, col=color)
  lines(x,z, pch=pc, lty=lt, col=color)
}

workloads=allocateWorkloadsVector()

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




L=10
metric="median"
#workload
operation="hpa-no-part"
deployment=operations[1]
title="Linear horizontal scaling"
xl="Number of tenants"
#yl=paste("95th ", metric," of response latency (ms)", sep="");
yl=paste("0.95 quantile", " of job completion time (s)", sep="");



data=plotHighestDeployment(workload, operation, metric, deployment, L, title, xl, yl, pc=9, lt=1, 
                           color=25, extend_y_lim = TRUE, y_lim_addition = -80, scalefactor = 1)
#redish

plotOtherDeploymentasLine(data, operations[2], L, 19, 6, color=134, scalefactor = 1)
#magenta


plotOtherDeploymentasLine(data, operations[3], L, 18, 25, color=450, scalefactor=1)
#black

plotOtherDeploymentasLine(data,  operations[4], L, 2, 29, color=25, scalefactor=1)
#azur blue


legend(x="topright", legend=operations, 
       pch = c(9,19,18,2), lty = c(1,6,25,29), 
       col = c(25,134,450,25), bty="n")

for (i in c(3)) {
  print(operations[i])
 foo <- data.frame(mean=unlist(workloads[[workload]][[operation]]$mean[[operations[i]]]),
                   sd=unlist(workloads[[workload]][[operation]]$stdev[[operations[i]]]))
 
 lines(rbind(1:10,1:10,NA),rbind(foo$mean - foo$sd,foo$mean + foo$sd,NA))
}