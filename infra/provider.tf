terraform {
    required_version = ">= 1.2.0"
    required_providers {
        google = {
        source  = "hashicorp/google"
        version = "~> 4.0"
        }
    }
}

# Configure the Google Cloud provider
provider "google" {
    project = var.project_id
    region  = var.region
}
