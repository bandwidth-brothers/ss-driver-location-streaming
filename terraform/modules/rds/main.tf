
resource "aws_db_instance" "mysql" {
  count                  = var.enabled ? 1 : 0
  engine                 = "mysql"
  engine_version         = "8.0"
  skip_final_snapshot    = true
  publicly_accessible    = var.db_publicly_accessible
  allocated_storage      = var.db_allocation_storage
  instance_class         = var.db_instance_class
  name                   = var.db_name
  username               = var.db_username
  password               = var.db_password
  vpc_security_group_ids = concat(var.vpc_security_group_ids, [aws_security_group.db_sg.id])
  db_subnet_group_name   = aws_db_subnet_group.rds_subnet_group.name
  tags                   = var.tags
}

resource "aws_db_subnet_group" "rds_subnet_group" {
  name       = "scrumptious-rds-subnet-group"
  subnet_ids = var.db_subnet_ids

  tags = {
    Name = "RDS Subnet Group"
  }
}

resource "aws_security_group" "db_sg" {
  name        = "scrumptious-db-sg"
  description = "Access for MySQL"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 3306
    protocol    = "tcp"
    to_port     = 3306
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port = 0
    protocol  = "-1"
    to_port   = 0
  }
}
