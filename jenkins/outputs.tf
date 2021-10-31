
output "ec2_public_dns" {
  value = aws_instance.jenkins.public_dns
}

output "ec2_public_ip" {
  value = aws_instance.jenkins.public_ip
}
