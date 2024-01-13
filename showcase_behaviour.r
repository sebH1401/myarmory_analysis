nPlayer <- 10
default_score <- rep(300,10)

data <- data.frame(score=default_score)
hist(data$score)

#adjust values to your liking
event_scores <-data.frame(toxicity=-100, trainer=+75, helpful=+50)

toxic_players <-c(1,2,5,6,7)

data$score[toxic_players] <- data$score[toxic_players]+event_scores$toxicity

trainer_players <- c(1,5,10)

data$score[trainer_players] <- data$score[trainer_players]+event_scores$trainer

helpful_players <- c(1,2,4,3,6,8,9)

data$score[helpful_players] <- data$score[helpful_players]+event_scores$helpful

hist(data$score)

# tranform it to the scale
hist(data$score/100)