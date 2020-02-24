library(dplyr)
library(ggplot2)

twilio <- read.csv("twilio.csv")


twilio <- twilio %>% 
    mutate(Body.Type = 
                      case_when (
                            str_detect(Body, " CES ") ~ "CES", 
                            str_detect(Body, "RACE/Router Restarted") ~ "RaceRestart",
                            str_detect(Body, "^EigenAlert\\(UAT\\):") ~ "UatAlerts",
                            str_detect(Body, "^EigenAlert\\(PRISM2\\):") ~ "Prism2Alerts",
                            str_detect(Body, "^EigenAlert\\(PRISM\\):") ~ "PrismAlerts"
                        ))
twilio_invalid <- twilio %>%
    filter(is.na(Body.Type)) %>% View()

