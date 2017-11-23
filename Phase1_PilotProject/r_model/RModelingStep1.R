####-------------- This script finds the features selected by random subset selection ------------####

library(reshape)
library(plyr)
library(caret)
library(data.table)

### Increasing the printing limit of R 
options(max.print=10000)

##Importing dataset
getwd()
setwd("C:/Users/abhis/Desktop/IBM Watson/Modeling")

data <-  read.csv("Final_Dataset.csv", header= TRUE)
str(data)

## Checking for null values
sapply(data, function(x) sum(is.na(x)))

# Dropping Variables which have null values 
data_v1 <- subset(data, select=-c(GMAT, IBTScore, UnderGradGPA, studentid, UnderGradMajor, International, Gender, gpa))
gpa <- data$gpa

## Selecting the features
iterations <- 500 #setting the no of iterations to run random subset selection
num_col <- dim(data_v1)[2]   #no of cols= no of features


#using LOOCV model for model building
ctrl <- trainControl(method="LOOCV",
                     classProbs = FALSE,
                     summaryFunction = defaultSummary)

##creating datafram to store selected variables
model_var <- data.frame(matrix(nrow= iterations, ncol=num_col))
colnames(model_var) <- colnames(data_v1)

##creating dataframe to store statsitics of selected variables
model_stats <- data.frame(matrix(nrow= iterations, ncol=6))
colnames(model_stats) <- c("r.squared", "adj.r.squared","value","numdf", "dendf","pvalue" )

for (i in 1:iterations) {
  ## Creating sampled dataframe
  num_features <- sample.int(dim(data_v1)[1]-2, 1, replace=F) 
  feature_index <- sample.int(num_col, num_features, replace=F) 
  feature_index <- sort(feature_index, decreasing = FALSE)

  #creating dataset and integrating gpa
  temp <- data_v1[,c(feature_index)]
  temp <- cbind(temp,gpa)

  #predictive model
  lmfit <- train(gpa ~ .,
               data = temp,
               method = "lm",
               trControl = ctrl,
               metric = "RMSE")

  results <- summary(lmfit)

  p_values <- results$coefficients[,4]
  x1 <- data.frame(p_values)

  for (j in feature_index){ 
      cname<-colnames(model_var[j])
      model_var[i,cname] <- x1[cname,1]

  }

  #storing statistics for each model row by row
  model_stats[i,"r.squared"] <- results$r.squared
  model_stats[i,"adj.r.squared"] <- results$adj.r.squared
  model_stats[i,"value"] <- results$fstatistic[1]
  model_stats[i,"numdf"] <- results$fstatistic[2]
  model_stats[i,"dendf"] <- results$fstatistic[3]
  model_stats[i,"pvalue"] <- pf(model_stats[i,"value"], model_stats[i,"numdf"], model_stats[i,"dendf"], lower.tail = F)

}


#combining the pvalues of each feature from each iteration with its statistics
eval <- cbind(model_var, model_stats)
eval <- unique(subset(eval, pvalue < 0.1))









