# MySQL RDS Instance

## Resources

* `aws_db_instance.mysql` - the MySQL RDS database
* `aws_security_group.db_sg` - security group for the database
* `aws_db_subnet_group.rds_subnet_group` - subnet group for the RDS

## Variables

* `enabled` - whether to create the database (default true)
* `db_name` - name of the database
* `db_username` - mysql database username
* `db_password` - mysql database password
* `db_instance_class` - instance class for rds instance (default db.t3.micro)
* `db_allocation_storage` - allocated storage (GiB) for database (default 20)
* `vpc_security_group_ids` - ids for security groups in vpc
* `db_subnet_ids` - list of subnet ids to put the database
* `db_publicly_accessible` - if the database is publicly accessible (default false)
* `vpc_id` - vpc for database security group
* `tags` - tags for the rds instance

## Outputs

* `db_endpoint` - the endpoint for the rds instance (host:port)
