# vars.tf 
variable "resource_group_location" {
  type        = string
  default     = "westus2"
  description = "Location of the resource group."
}

variable "resource_group_name_prefix" {
  type        = string
  default     = "rg"
  description = "Prefix of the resource group name that's combined with a random ID so name is unique in your Azure subscription."
}

variable "username" {
  type        = string
  description = "The username for the local account that will be created on the new VM."
  default     = "scanner"
}

variable "subscriptionID" {
  type = string
}

variable "clientID" {
  type = string
}

variable "clientSecret" {
  type = string
}

variable "tenantID" {
  type = string
}

variable "vmname" {
  type = string
  description = "Vm name"
  default = "scanner1"
}

variable "ssh_public_key" {
  type        = string
  description = "Your SSH public key"
}


variable "AZzone" {
  type = number
  default = 1
  description = "Your zone id"
}

variable "wireguard_private_key" {
  description = "WireGuard private key"
  type        = string
  sensitive   = true
}

variable "wireguard_peer_public_key" {
  description = "WireGuard peer public key"
  type        = string
  sensitive   = true
}

variable "wireguard_host_endpoint" {
  description = "Wireguard host enpoint ip and port"
  type = string
}