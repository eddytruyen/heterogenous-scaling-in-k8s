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
    workloads[[workload]]$operations <- vector("list", 0)
    workloads[[workload]]$operations.names <-  c()
    names(workloads[[workload]]$operations) = workloads[[workload]]$operations.names
  }
  print(workloads)
  tmp.names = operations
  tmp <- vector("list", length(tmp.names))
  names(tmp) <- tmp.names
  wl_operations=workloads[[workload]]$operations
  #workloads[[workload]]$operations.names = append(wl_operations.names, tmp.names)
  workloads[[workload]]$operations = append(wl_operations, tmp)
  #names(workloads[[workload]]$operations) = workloads[[workload]]$operations.names
  print(workloads)
  return (workloads)
}

workloads=allocateWorkloadsVector()

files = get_files(directory)

for (j in names(workloads[[workload]]$operations)) {
  for (i in names(files)) {
    print(i)
    rundata <- unlist(files[i])
    for (r in rundata) {
      filename=paste(directory,"/",r,sep="")
      data = readLines(filename)
      number <- unlist(strsplit(data[startsWith(data,j)][2],split=",")) #[2]only retrieve metric s
      print(number[3]) # the number of seconds is stored in the 3rd field
      workloads[[workload]]$operations[[j]]$raw$deployment[[deployment]][[paste("tenant-",i,sep="")]] <- append(workloads[[workload]]$operations[[j]]$raw$deployment[[deployment]][[paste("tenant-",i,sep="")]], number[3])
    }
  }
}