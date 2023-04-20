terraform {
  required_providers {
    linode = {
      source  = "linode/linode"
    }
  }
}

variable "linode_token" {
  type = string
  sensitive = true
}

# Configure the Linode Provider
provider "linode" {
  token = var.linode_token
}
