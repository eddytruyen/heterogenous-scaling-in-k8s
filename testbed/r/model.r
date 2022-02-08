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

# Function for plotting data points and function
myPlotFunction <- function(f, start=FALSE, startValues=0, xvar, yvar, data) {
  if (start == TRUE) {
    fr = fitModel(f, data = data, start=startValues) 
  } else {
    fr = fitModel(f, data = data)
  }
  plotFun(fr(xvar)~xvar, add=TRUE, col="red")
}

# Load data
x=read.csv(file="/home/arno/Documents/res/summary_linear.csv", header = TRUE) 

# Linear
plotPoints(Avg.CPU~Tenants, data = x, main="Linear")
fl = fitModel(Avg.CPU~A*Tenants, data = x)
plotFun(fl(Tenants)~Tenants, add=TRUE, col="red")

# Quadratic
plotPoints(Avg.CPU~Tenants, data = x, xlim=c(0,20), main="Quadratic")
fq = fitModel(Avg.CPU~A*Tenants^2+B*Tenants + C, data = x)
plotFun(fq(Tenants)~Tenants, add=TRUE, col="red")


plotPoints(Avg.CPU~Tenants, data = x, xlim=c(0,20), main="Exp")
c <- min(x["Avg.CPU"])*0.5
model.0 <- lm(log(Avg.CPU - c) ~ Tenants, data=x)
start <- list(A=exp(coef(model.0)[1]), B=coef(model.0)[2], C=c)
fe = fitModel(Avg.CPU~A * exp(B * Tenants) + C, data = x, start=start)
plotFun(fe(Tenants)~Tenants, add=TRUE, col="red")

plotPoints(X95.~Tenants, data = x, xlim=c(0,20), main="Exp")
c <- min(x["X95."])*0.5
model.0 <- lm(log(X95. - c) ~ Tenants, data=x)
start <- list(A=exp(coef(model.0)[1]), B=coef(model.0)[2], C=c)
fz = fitModel(Avg.CPU~A*Tenants, data = x, start=start)
plotFun(fz(Tenants)~Tenants, add=TRUE, col="red")f

