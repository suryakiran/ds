tasks_csv = read_csv("tasks.csv")
nec = c("TaskName", "Task To Run", "Start In", "Run As User", "Schedule Type", "Repeat: Every")

tasks_csv %>% select(all_of(nec)) %>% View()

glimpse(tasks_csv)
