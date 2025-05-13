
# ssh.tf 
resource "random_pet" "ssh_key_name" {
  prefix    = "ssh"
  separator = ""
}

resource "azapi_resource" "ssh_public_key" {
  type      = "Microsoft.Compute/sshPublicKeys@2022-11-01"
  name      = random_pet.ssh_key_name.id
  location  = azurerm_resource_group.rg.location
  parent_id = azurerm_resource_group.rg.id

  response_export_values = ["properties.publicKey"]

  body = jsonencode({
    properties = {
      publicKey = var.ssh_public_key
    }
  })
}