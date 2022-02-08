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

setwd("/home/arno/docker-thesis/r/")

# Function to plot data points and connecting a line through it (linear)
plotOffLineData <- function(timings, cropLength, title, xl, yl, extend_y_lim=FALSE, y_lim_addition = 0, scalefactor=5, pc, lt, color="black") {
  z=timings
  z=z[1:cropLength]
  x=(1:cropLength)*scalefactor
  if (extend_y_lim == TRUE) {
    y_lim=min(unlist(z))-y_lim_addition
    plot(z~x, main=title, xlab=xl,ylab=yl, xaxp  = c(1,length(x),length(x)-1),pch=pc, lty=lt, col=color, ylim=c(0, y_lim))
  } else {
    plot(z~x, main=title, xlab=xl,ylab=yl, pch=pc, lty=lt, col=color)
  }
  lines(x, z, pch=pc, lty=lt, col=color)
}

L=10

x=read.csv(file="timings.csv", header= FALSE) 
#de completion time  van 1 tot 10 tenants
y=unlist(x)
title="Off-line data"
xl="Number of tenants"
yl=paste("0.95 quantile", " of job completion time (s)", sep="");
fitted=FALSE

# Bunch of variables to make plots look nice
pch1 = c(9,19,18,2,25)
lty1 = c(1,6,25,29,134)
col1 = c(25,134,450,25,6)

# Plot the raw data!
plotOffLineData(y, L, title, xl, yl, pc=pch1[1], lt=lty1[1], color=col1[1], extend_y_lim = FALSE, y_lim_addition = -150, scalefactor = 1) 

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

#Dit geeft als waarde
#         A           B           C
#667.1840993  -0.8232555 136.4046126


plotPoints(y~z)

plotFun(f(z)~z, z.lim = range(1:L), add = TRUE, col="blue")
