variable "root_pass" {
  type = string
  sensitive = true
}
variable "ssh_key" {
  type = string
  sensitive = true
}
resource "linode_instance" "sonarqube" {
    label = "sonarqube"
    image = "linode/ubuntu22.04"
    region = "ap-south"
    type = "g6-nanode-1"
    authorized_keys = [var.ssh_key]
    root_pass = var.root_pass

    group = "sonarqube"
    tags = [ "sonarqube" ]
    swap_size = 1024
}


resource "linode_firewall" "sonarqube-firewall" {
  label = "sonarqube-firewall"

  inbound {
    label    = "allow-ssh"
    action   = "ACCEPT"
    protocol = "TCP"
    ports    = "22"
    ipv4     = ["0.0.0.0/0"]
    ipv6     = ["::/0"]
  }

  inbound {
    label    = "allow-sonarqube"
    action   = "ACCEPT"
    protocol = "TCP"
    ports    = "9000"
    ipv4     = ["0.0.0.0/0"]
    ipv6     = ["::/0"]
  }

  inbound_policy = "DROP"

  outbound_policy = "ACCEPT"

  linodes = [
    linode_instance.sonarqube.id,
  ]

}

output "sonarqube-ip" {
  value = join(",",linode_instance.sonarqube.ipv4)
}
