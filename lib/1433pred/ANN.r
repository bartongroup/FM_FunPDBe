#!/usr/bin/env Rscript --vanilla --default-packages=utils
# Fabio Madeira, 2014

fromCSVtoNetANN <- function(input, output, hidden, iterations,
                               rate, momentum){

 
  # inserting the necessary libraries
  suppressPackageStartupMessages(library(Rcpp))
  suppressPackageStartupMessages(library(RSNNS))
  library(RSNNS)
  
  # input data
  intrain <- read.csv(input, header=FALSE)
  
  # split values and labels: currently for ONE labels
  max <- ncol(intrain)
  train_V <- intrain[,(1:(max-1))]
  train_L <- intrain[,max]
  
  # setting the seed value
  seed <- 2
  set.seed(seed)
  setSnnsRSeedValue(seed)
  
  # ANN training and validation
  model <- mlp(train_V, train_L, size=hidden, maxit=iterations,
               learnFunc="BackpropMomentum",learnFuncParams=c(rate, momentum))
  
  #summary(model)
  exportToSnnsNetFile(model, output)

}

args <- commandArgs(TRUE)
input <- args[1]
output <- args[2]
hidden <- as.integer(args[3])
iterations <- as.integer(args[4])
rate <- as.numeric(args[5])
momentum <- as.numeric(args[6])

fromCSVtoNetANN(input, output, hidden, iterations, rate, momentum)

#input <- "./Experiments/ANN_1_7/ANN_POS_NEG.csv"
#output <- "./Experiments/ANN_1_7/ANN.net"
#hidden <- 20
#iterations <- 5
#rate <- 0.2
#momentum <- 0.05
