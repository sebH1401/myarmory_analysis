nPlayer <- 500
bosses <- c('b1', 'b2')

#to be prredicted
meanDPSb1 <- 10000
meanDPSb2 <- 15000
sDPS <- 1000

#predictors
meanMight <- 20
sMight <- 1
meanQuick <- 0.70
sQuick <- 0.1
meanAlac <- 0.70
sAlac <- 0.1

#unrealistic
dpsB1 <- rnorm(nPlayer, meanDPSb1, sDPS)
dpsB2 <- rnorm(nPlayer, meanDPSb2, sDPS)

#maybe you need to adjust these values if they are some kidn of skewed
might <- rnorm(nPlayer, meanMight, sMight)
quick <- rnorm(nPlayer, meanQuick, sQuick)
alac <- rnorm(nPlayer, meanAlac, sAlac)

hist(might)

#problems: linear model, values outside of argrange are difficult to estimate
#is there a linear connection?, are the estimate significant?
b1 <- data.frame(dps=dpsB1, might=might, quick=quick, alac=alac)
modelDPSb1 <- glm(dpsB1 ~ might, data=b1)
#no significance as expected
summary(modelDPSb1)

examplePlayer <- data.frame(might=25.0, quick=0.95, alac=0.99)
dpsEx <- predict.glm(modelDPSb1, newdata = examplePlayer)
cbind(examplePlayer, dpsEx)

#compare expected dps to actual observed dps and give a rating on that, maybe include breakbar damage and mechanic and so on
#adjust personal score (maybe mean) with score


# for boon supporters take boon output, combined with dps for a boon supporter or sth similar
#adjust personal score with that

plot(might, dpsB1)