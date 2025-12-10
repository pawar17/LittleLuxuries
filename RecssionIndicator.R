## SEM of Recession Indicators
# packages
library(lavaan)
library(dplyr)
# load data
df <- read.csv("~/filepath/All Variables - US Data - Sheet1.csv")
head(df)
# make sure df is numeric
sapply(df, class)
# it is not, transform to numeric
df_clean <- as.data.frame(lapply(df, function(x) {
x <- gsub(",", "", x) # remove commas
as.numeric(as.character(x)) # convert to numeric
}))
## indie sleaze
indiesleaze <- 'indiesleaze =~ + indiesleaze_skinnyjeans + indiesleaze_cheetahprint +
indiesleaze_furcoat + indiesleaze_leatherskirt + indiesleaze_discopants'
# fix scale
# standardize your observed variables (mean = 0, sd = 1)
df_clean <- df_clean |>
mutate(across(starts_with("indiesleaze"), ~ scale(.) |> as.numeric()))
# sem fit
fit <- sem(indiesleaze, data = df_clean)
summary(fit, standardized = TRUE, fit.measures = TRUE)
#' notes on results
#' model works but fur coat has low shared variance, so we test again w/o it
indiesleaze <- 'indiesleaze =~ + indiesleaze_skinnyjeans + indiesleaze_cheetahprint +
indiesleaze_leatherskirt + indiesleaze_discopants'
# sem fit
fit <- sem(indiesleaze, data = df_clean)
summary(fit, standardized = TRUE, fit.measures = TRUE)
# add in latent variable
latent_scores <- lavPredict(fit)
df_clean$indiesleaze <- latent_scores
# regression
model2 <- lm(cci ~ indiesleaze, data = df_clean)
summary(model2)
## lipstick index
lipstickindex <- 'lipstickindex =~ + lipstickindex_lipstick + lipstickindex_lip_stick +
lipstickindex_lipgloss + lipstickindex_lipliner + lipstickindex_liptint'
# fix scale
# standardize your observed variables (mean = 0, sd = 1)
df_clean <- df_clean |>
mutate(across(starts_with("lipstickindex"), ~ scale(.) |> as.numeric()))
# sem fit
fit <- sem(lipstickindex, data = df_clean)
summary(fit, standardized = TRUE, fit.measures = TRUE)
#' notes on fit results
#' liptint is causing a problem
#' in SEM, when a standardized factor loading (Std.all) is too high
#' it signals a potential problem with overfitting or a misbehaving indicator
#' so we remove and retry without liptint
lipstickindex <- 'lipstickindex =~ + lipstickindex_lipstick + lipstickindex_lip_stick +
lipstickindex_lipgloss + lipstickindex_lipliner'
# sem fit
fit <- sem(lipstickindex, data = df_clean)
summary(fit, standardized = TRUE, fit.measures = TRUE)
# lipgloss now overfits, so we drop it
lipstickindex <- 'lipstickindex =~ + lipstickindex_lipstick + lipstickindex_lip_stick +
lipstickindex_lipliner'
# sem fit
fit <- sem(lipstickindex, data = df_clean)
summary(fit, standardized = TRUE, fit.measures = TRUE)
# better so we move to creating a latent variable
latent_scores <- lavPredict(fit)
df_clean$lipstickindex <- latent_scores
# regression
model2 <- lm(cci ~ lipstickindex, data = df_clean)
summary(model2)
# significant model again
# move on to maxi skirts
maxiskirt <- 'maxiskirt =~ + maxiskirt_maxiskirt + maxiskirt_longskirt + maxiskirt_bohoskirt +
maxiskirt_maxidress + maxiskirt_longdress'
# fix scale
# standardize your observed variables (mean = 0, sd = 1)
df_clean <- df_clean |>
mutate(across(starts_with("maxiskirt"), ~ scale(.) |> as.numeric()))
# sem fit
fit <- sem(maxiskirt, data = df_clean)
summary(fit, standardized = TRUE, fit.measures = TRUE)
# all factor loadings are good, so move directly to the regression
# add in latent variable
latent_scores <- lavPredict(fit)
df_clean$maxiskirt <- latent_scores
# regression
model2 <- lm(cci ~ maxiskirt, data = df_clean)
summary(model2)
# also significant, altho explains less of the variance than indie sleaze or lipstick
# next recession indicator -- big bag
bigbag <- 'bigbag =~ + bigbag_hobobag + bigbag_oversizedbag + bigbag_totebag +
bigbag_neverfull + bigbag_balenciagacitybag'
# fix scale
# standardize your observed variables (mean = 0, sd = 1)
df_clean <- df_clean |>
mutate(across(starts_with("bigbag"), ~ scale(.) |> as.numeric()))
# sem fit
fit <- sem(bigbag, data = df_clean)
summary(fit, standardized = TRUE, fit.measures = TRUE)
# oversized bag overfits, so we drop this
# remake model
bigbag <- 'bigbag =~ + bigbag_hobobag + bigbag_totebag + bigbag_neverfull +
bigbag_balenciagacitybag'
# sem fit
fit <- sem(bigbag, data = df_clean)
summary(fit, standardized = TRUE, fit.measures = TRUE)
# better - so move to latent var and regression
latent_scores <- lavPredict(fit)
df_clean$bigbag <- latent_scores
# regression
model2 <- lm(cci ~ bigbag, data = df_clean)
summary(model2)
# next recession indicator -- highheelindex_highheels
highheelindex <- 'highheelindex =~ + highheelindex_highheels + highheelindex_stilletoheel +
highheelindex_platforms + highheelindex_platformheels + highheelindex_pumps'
# standardize your observed variables (mean = 0, sd = 1)
df_clean <- df_clean |>
mutate(across(starts_with("highheelindex"), ~ scale(.) |> as.numeric()))
# sem fit
fit <- sem(highheelindex, data = df_clean)
summary(fit, standardized = TRUE, fit.measures = TRUE)
# platform terms causing heyword case / negative variance
highheelindex <- 'highheelindex =~ + highheelindex_highheels + highheelindex_stilletoheel +
highheelindex_pumps'
fit <- sem(highheelindex, data = df_clean)
summary(fit, standardized = TRUE, fit.measures = TRUE)
# still bad can't do latent variables, so we just do a regression with one variable
model2 <- lm(cci ~ highheelindex_highheels, data = df_clean)
summary(model2)
# high heel index is not significant
# next recession indicator -- peplums
peplums <- 'peplums =~ + peplums_peplum + peplums_peplumtops + peplums_peplumdress +
peplums_rufflewaist + peplums_peplumblazer'
# standardize your observed variables (mean = 0, sd = 1)
df_clean <- df_clean |>
mutate(across(starts_with("peplums"), ~ scale(.) |> as.numeric()))
# sem fit
fit <- sem(peplums, data = df_clean)
summary(fit, standardized = TRUE, fit.measures = TRUE)
# try again but remove ruffle and solo peplum searches
peplums <- 'peplums =~ + peplums_peplumtops + peplums_peplumdress +
peplums_peplumblazer'
# sem fit
fit <- sem(peplums, data = df_clean)
summary(fit, standardized = TRUE, fit.measures = TRUE)
# fine so create latent
latent_scores <- lavPredict(fit)
df_clean$peplum <- latent_scores
model2 <- lm(cci ~ peplum, data = df_clean)
summary(model2)
# next indicator -- blazers
blazers <- 'blazers =~ + blazers_blazer + blazers_womensblazer + blazers_oversizedblazer +
blazers_boyfriendblazer + blazers_croppedblazer'
# standardize your observed variables (mean = 0, sd = 1)
df_clean <- df_clean |>
mutate(across(starts_with("blazers"), ~ scale(.) |> as.numeric()))
# sem fit
fit <- sem(blazers, data = df_clean)
summary(fit, standardized = TRUE, fit.measures = TRUE)
# boyfriend blazer bad loading
blazers <- 'blazers =~ + blazers_blazer + blazers_womensblazer + blazers_oversizedblazer +
blazers_croppedblazer'
# sem fit
fit <- sem(blazers, data = df_clean)
summary(fit, standardized = TRUE, fit.measures = TRUE)
# best model yet now
# create latent
latent_scores <- lavPredict(fit)
df_clean$blazers <- latent_scores
model2 <- lm(cci ~ blazers, data = df_clean)
summary(model2)
# final indicator -- mini skirts
mini <- 'mini =~ + mini_miniskirt + mini_minidress + mini_micromini + mini_microshort +
mini_micominiskirt'
# standardize your observed variables (mean = 0, sd = 1)
df_clean <- df_clean |>
mutate(across(starts_with("mini"), ~ scale(.) |> as.numeric()))
# sem fit
fit <- sem(mini, data = df_clean)
summary(fit, standardized = TRUE, fit.measures = TRUE)
# micro mini has to go
mini <- 'mini =~ + mini_miniskirt + mini_minidress + mini_microshort + mini_micominiskirt'
# sem fit
fit <- sem(mini, data = df_clean)
summary(fit, standardized = TRUE, fit.measures = TRUE)
# fine now
# create latent
latent_scores <- lavPredict(fit)
df_clean$mini <- latent_scores
model2 <- lm(cci ~ mini, data = df_clean)
summary(model2)
# 2 x plots for strongest vars
# Fit the model
model_blazers <- lm(cci ~ blazers, data = df_clean)
# Base R plot
plot(df_clean$blazers, df_clean$cci,
xlab = "Blazer Trend Score",
ylab = "Consumer Confidence",
pch = 10, col = rgb(0.2, 0.2, 0.2, 0.5))
# Add regression line
abline(model_blazers, col = "black", lwd = 2)
# Add R² and p-value
r2 <- summary(model_blazers)$r.squared
pval <- summary(model_blazers)$coefficients[2, 4]
legend("topright",
bty = "n")
# Fit the model
model_mini <- lm(cci ~ mini, data = df_clean)
# Base R plot
plot(df_clean$mini, df_clean$cci,
xlab = "Mini Skirt Trend Score",
ylab = "Consumer Confidence",
pch = 10, col = rgb(0.2, 0.2, 0.2, 0.5))
# Add regression line
abline(model_blazers, col = "black", lwd = 2)
# Add R² and p-value
r2 <- summary(model_blazers)$r.squared
pval <- summary(model_blazers)$coefficients[2, 4]
legend("topright",
bty = "n")