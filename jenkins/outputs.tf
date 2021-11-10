
output "jenkins_public_dns" {
  value = "${aws_instance.jenkins.public_dns}:8080"
}

output "jenkins_public_ip" {
  value = "${aws_instance.jenkins.public_ip}:8080"
}
