

## IBM Watson Project ###
##Importing dataset
## IBM Watson Project ###

data <-  read.csv("Final_Dataset.csv", header= TRUE)
str(data)

## Checking for null values
sapply(data, function(x) sum(is.na(x)))

# Dropping Variables which have null values 
data_v1 <- subset(data, select=-c(GMAT, IBTScore, UnderGradGPA, studentid, UnderGradMajor, International, Gender, gpa))
gpa <- data$gpa

num_col <- dim(data_v1)[2]

#This code takes the important features, trains the model and predits GPA
getwd()
setwd("C:/Users/abhis/Desktop/IBM Watson/Modeling")
feat_df <-  read.csv("FeaturesImp.csv", header= TRUE)

colnames(feat_df)
dim(feat_df)

eval1 <- unique(subset(feat_df, pvalue < 0.1))
dim(eval1)
eval1



##creating datafram to store Freq of occurred variables and their significance
var_impdf <- data.frame(matrix(nrow= 3, ncol= num_col))
colnames(var_impdf) <- colnames(data_v1)



for(k in colnames(data_v1))
{ var_impdf[1,k] <- sum(!is.na(eval1[,k]))
var_impdf[2,k] <- (table(eval1[,k]< 0.1)["TRUE"])

if(is.na(var_impdf[2,k]))
  var_impdf[3,k]<-NA
else
  var_impdf[3,k]<- var_impdf[2,k]/var_impdf[1,k]
}

var_impdf<-t(var_impdf)
var_impdf
dim(var_impdf)
colnames(var_impdf) <- c("Freq", "SignificantFreq","Percent" )

var_impdf <- data.frame(var_impdf)
head(var_impdf)

##subsetting for more than 50 percent

imp_var <- subset(var_impdf, Percent > 0.5)
imp_var_names<-rownames(imp_var)

imp_var_names<-array(imp_var_names)
imp_var_names
traindf <- cbind (data_v1[,imp_var_names],gpa)
traindf

## Running Models


ctrl <- trainControl(method="LOOCV",
                     classProbs = FALSE,
                     summaryFunction = defaultSummary)





##linear Regression
lmfit <- train(gpa ~ .,
               data = traindf,
               method = "lm",
               trControl = ctrl,
               metric = "RMSE")

summary(lmfit)

##lasso
lassofit <- train (gpa ~ .,
                   data = traindf,
                   method = "lars",
                   trControl = ctrl,
                   tuneLength = 25,
                   metric = "RMSE")

summary(lassofit)

predict(lassofit$finalModel, type='coefficients', s=lassofit$bestTune$fraction, mode='fraction')

# ##decision tree
# 
# ctrl <- trainControl(method="cv", number=5,
#                      classProbs = FALSE,
#                      summaryFunction = defaultSummary)
# traindf
# reg_tree <- train(gpa~.,
#                   data = traindf,
#                   method = "rpart",
#                   trControl = ctrl,
#                   tuneLength = 5,
#                   metric = "RMSE")
# 
# ## checking the results
# reg_tree
# 
# #plotting the CV tree to see optimal number of terminal nodes
# plot(reg_tree)
# 
# plot(cv.trees)
# 
# #plotting the CV tree to see optimal number of terminal nodes
# par(mfrow=c(1,1))
# plot(reg_tree$finalModel)
# text(reg_tree$finalModel)
# library(rattle)
# fancyRpartPlot(reg_tree$finalModel)


##comparing performance of Lasso and Linear Regression
library(resample)

resamps <- resamples(list(LASSO = lassofit,                    
                          Linear_Regression = lmfit
                          ))

resamps

summary(resamps)

### box plot of all three metrics for all the models
bwplot(resamps, layout = c(2, 1))

##scatter plot of ROC for various resamples for all the three models
splom(resamps)
