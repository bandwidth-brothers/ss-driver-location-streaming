
#output "spark_task_role_arn" {
#  value = module.spark_service.spark_task_role_arn
#}

output "cluster_arn" {
  value = module.ecs.ecs_cluster_arn
}
