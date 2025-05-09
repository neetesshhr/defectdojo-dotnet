terraform {
  cloud {
    organization = "budgetbuys"
    workspaces {
      name = "ollama_predictor"
    }
  }
  required_version = ">=0.12"

  required_providers {
    azapi = {
      source  = "azure/azapi"
      version = "~>1.5"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~>3.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~>3.0"
    }
  }
}

provider "azurerm" {
  subscription_id = var.subscriptionID
  client_id = var.clientID
  client_secret = var.clientSecret
  tenant_id = var.tenantID

  features {
    
  }
}

provider "azapi" {
  subscription_id = var.subscriptionID
  client_id       = var.clientID
  client_secret   = var.clientSecret
  tenant_id       = var.tenantID
}