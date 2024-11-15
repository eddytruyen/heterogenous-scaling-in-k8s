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

plotOffLineData<-function(timings, cropLength, title, xl, yl, extend_y_lim=FALSE, y_lim_addition = 0, scalefactor=5, pc, lt, color="black")  {
  z=timings
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
}

L=10
x=read.csv(file="timings/sql.csv", header= FALSE)  
#de completion time  van 1 tot 10 tenants
y=unlist(x)
title="Off-line data"
xl="Number of tenants"
#yl=paste("95th ", metric," of response latency (ms)", sep="");
yl=paste("0.95 quantile", " of job completion time (s)", sep="");
fitted=FALSE

pch1 = c(9,19,18,2,25)
lty1 = c(1,6,25,29,134)
col1 = c(25,134,450,25,6)

plotOffLineData(y, L, title, xl, yl, pc=pch1[1], lt=lty1[1], color=col1[1], extend_y_lim = TRUE, y_lim_addition = -400, scalefactor = 1) 

#Dit genereert de volgende plot (zie attachment)

#Op basis van die plot gaan we op zoek naar een goede fitting functie in https://www.statforbiology.com/nonlinearregression/usefulequations

#Dat geeft de volgende functie(x)= A * exp(B * x) + C

#Nu moeten we enkel nog goede waarden vinden voor A, B,C


y=unname(y[1:L])

z = (1:L)
frame=data.frame(z,y)


computeFunction <- function(y,z,frame) {
  c <- min(y)*0.5
  model.0 <- lm(log(y - c) ~ z, data=frame)
  start <- list(A=exp(coef(model.0)[1]), B=coef(model.0)[2], C=c)
  f = fitModel(y ~ A * exp(B * z) + C, data = frame, start = start)  
  return(f)
}



z=(1:L)
f<-computeFunction(y,z,frame)
coef(f)
plotPoints(y~z)

plotFun(f(z)~z, z.lim = range(1:L), add = TRUE, col="blue")
