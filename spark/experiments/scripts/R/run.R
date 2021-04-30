rm(list=ls())


library("reshape2")
library("ggplot2")
library("gridExtra")
library("plyr")
library(mosaic)
library(mosaicCore)
library(mosaicData)
library(mosaicCalc)
library(data.table)

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
  w2=get(deployment, get(workload, workloads))
  data=get(metric,w2)
  nb_of_tenants<-names(data$total)
  pod_replicas<-unname(w2$pod_replicas)
  cpus<-unname(w2$cpus)
  memGB<-unname(w2$mem)
  plist <- vector("list", length(pod_replicas))
  for (i in 1:length(pod_replicas)) {
    plist[[i]] <- c(paste(pod_replicas[i],"r", sep=""),paste(cpus[i],"c",sep=""))
  }
  z=unlist(get(operation, data))
  z=z[1:cropLength]
  x=(1:cropLength)*scalefactor
  x2=names(get("total",get("median", get(deployment, get(workload, workloads)))))
  #x3=rbind(x,x2)
  #frame=data.frame(x2, unname(z))
  #fit <- lm(z ~ x + I(x^2))
  if (extend_y_lim == TRUE) { 
    y_lim=min(unlist(z))-y_lim_addition
    plot(axes=FALSE, z~x, main=title, xlab=xl,ylab=yl, xaxp  = c(1,length(x),length(x)-1),pch=pc, lty=lt, col=color, ylim=c(0, y_lim))
    #plotPoints(z~x2)
  } else {
    plot(z~x, axes=FALSE,main=title, xlab=xl,ylab=yl, pch=pc, lty=lt, col=color)
        #plotPoints(z~x2)
  }
  axis(2)
  axis(1, at=seq_along(z),labels=as.character(nb_of_tenants), las=1)
  axis(3, at=seq_along(z),labels=as.character(plist),las=1)
  box()
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


L=10
metric="mean"
workload="spark-bench"
deployment="vps"


synthesize<-function(workload, deployment, metric, cropLength)  {
  operations=get(metric, get(deployment, get(workload, workloads)))
  total <- unname(unlist(operations[1]))
  for (op in operations[2:length(operations)]) {
      total <- total + unlist(op)
  }
  
 return(total)
}

workloads[[workload]][[deployment]]$mean[["total"]] <- synthesize(workload,deployment,"mean",L)
workloads[[workload]][[deployment]]$median[["total"]] <- synthesize(workload,deployment,"median",L)

    

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

replicas <- c(1,1,1,1,2,3,4,5,7,9) #auto-hpa-11Gimem
workloads$`spark-bench`$`hpa-11Gimem`$pod_replicas <- replicas

replicas <-c(2,2,2,4,4,5,3) #vps
workloads$`spark-bench`$`vps`$pod_replicas <- replicas
cpus <- c(1,2,3,2,3,2,4)
workloads$`spark-bench`$`vps`$cpus <- cpus
mems <- c(7,14,30,14,14,14,30)
workloads$`spark-bench`$`vps`$mems <- mems



workloads = readRDS(file=workloadfile)



L=10
metric="mean"
workload="spark-bench"
deployment="hps"
operation="total"
title="Horizontal auto-scaling cpu-threshold 80%"
xl="Number of tenants"
#yl=paste("95th ", metric," of response latency (ms)", sep="");
yl=paste("0.95 quantile", " of job completion time (s)", sep="");

data=(get(metric, get(deployment, get(workload, workloads))))
y=unlist(get(operation, data))
y=unname(y[1:L])
print(y)


z = (1:L)
frame=data.frame(z,y)

#f <- nls(y ~ A * exp(B * z) + C, data = frame, start = start)


computeFunction <- function(y,z,frame) {
  c <- min(y)*0.5
  model.0 <- lm(log(y - c) ~ z, data=frame)
  start <- list(A=exp(coef(model.0)[1]), B=coef(model.0)[2], C=c)
  f = fitModel(y ~ A * exp(B * z) + C, data = frame, start = start)
  return(f)
}


z=(1:L)
plotPoints(y~z)
coef(f)
plotFun(f(z)~z, z.lim = range(1:L), add = TRUE, col="blue")

d=D(f(z)~z)

soln=integrateODE(dz~f(z),z=1,tdur=100)
plotFun(soln$z, tlim=range(1,100))


d(1)
d(2)
f(1)-(d(2)-d(1))


L=7
metric="median"
workload="spark-bench"
deployment="vps"
operation=operations[1]
title="Horizontal auto-scaling cpu-threshold 80%"
xl="Number of tenants"
#yl=paste("95th ", metric," of response latency (ms)", sep="");
yl=paste("0.95 quantile", " of job completion time (s)", sep="");



pch1 = c(9,19,18,2,25) 
lty1 = c(1,6,25,29,134) 
col1 = c(25,134,450,25,6)

#plotPoints(unlist(unname(workloads$`spark-bench`$vps$mean$`select * from parquet`))~(1:7))



data=plotHighestVpaDeployment(workload, deployment, metric, operation, L, title, xl, yl, pc=pch1[1], lt=lty1[1], 
                           color=col1[1], extend_y_lim = TRUE, y_lim_addition = -150, scalefactor = 1)
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
