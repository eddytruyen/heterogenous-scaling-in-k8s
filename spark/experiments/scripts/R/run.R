rm(list=ls())


library("reshape2")
library("ggplot2")
library("gridExtra")
library("plyr")

source(file="get_files.R")

options(scipen = 999)
directory="../../hpa-no-part"
workload="spark-bench-sql"
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
    wl_operations=workloads[[workload]]$operations
    if ( length(Reduce(intersect,list(wl_operations,operations)))>0) {
      quit(paste("Workload file", workload, "already refers to operations names that are included in", operations))
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
  print(names(workloads[[workload]]))
  tmp.names = operations
  tmp <- vector("list", length(tmp.names))
  names(tmp) <- tmp.names
  wl_operations=workloads[[workload]]
  #workloads[[workload]]$operations.names = append(wl_operations.names, tmp.names)
  workloads[[workload]] = append(wl_operations, tmp)
  #names(workloads[[workload]]$operations) = workloads[[workload]]$operations.names
  return (workloads)
}

workloads=allocateWorkloadsVector()

files = get_files(directory)

for (j in names(workloads[[workload]])) {
  for (i in names(files)) {
    rundata <- unlist(files[i])
    for (r in rundata) {
      filename=paste(directory,"/",r,sep="")
      data = readLines(filename)
      number <- unlist(strsplit(data[startsWith(data,j)][1],split=",")) #[2]only retrieve metric ns
      sec=as.numeric(number[3])/1000000000 # the number of nanoseconds is stored in the 3rd field
      workloads[[workload]][[j]]$raw[[deployment]][[paste(i,"-tenants",sep="")]] <- append(workloads[[workload]][[j]]$raw[[deployment]][[paste(i,"-tenants",sep="")]], sec)
    }
    rawdata = workloads[[workload]][[j]]$raw[[deployment]][[paste(i,"-tenants",sep="")]]
    workloads[[workload]][[j]]$mean[[deployment]][[paste(i,"-tenants",sep="")]] <- mean.default(rawdata)
    workloads[[workload]][[j]]$median[[deployment]][[paste(i,"-tenants",sep="")]] <- median(rawdata)
    workloads[[workload]][[j]]$stdev[[deployment]][[paste(i,"-tenants",sep="")]] <- sd(rawdata)
    
  }
}