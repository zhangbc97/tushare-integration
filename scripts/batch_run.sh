#! /bin/bash

# 使用kubectl批量触发所有任务

for job in $(kubectl get cronjobs -o name); do
  kubectl create job --from=$job $(echo $job | cut -d'/' -f2)
done