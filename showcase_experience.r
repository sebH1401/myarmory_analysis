#main question: how experienced are the players?


#basic experience based on achievements, give points for that
nPlayer <- 10
achievements <- c(100, 250 ,150)

data <- data.frame(baseExperience=rep(0,10))

dataPlayerAchievements <- data.frame(ach1 = rbinom(10,1,0.7), ach2 = rbinom(10,1,0.5), ach3 = rbinom(10,1,0.2))

achievements * dataPlayerAchievements