terraform {
    required_providers {
        google = {
        source  = "hashicorp/google"
        version = "~> 4.0"
        }
    }

    backend "gcs" {
        # These values will be filled by -backend-config in terraform init
    }
} 
