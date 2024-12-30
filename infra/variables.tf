variable "project_id" {
    description = "The GCP project ID"
    type        = string
}

variable "region" {
    description = "The region to deploy to"
    type        = string
    default     = "us-central1"
}

variable "service_name" {
    description = "The name of the Cloud Run service"
    type        = string
    default     = "medical-entity-extraction"
}

variable "image_name" {
    description = "The name of the container image"
    type        = string
}

variable "env_vars" {
    description = "Environment variables to set in the container"
    type        = map(string)
    default = {
        GCP_PROJECT_ID = null  
        GCP_MODEL_NAME   = null  
        GCP_LOCATION     = null  
    }
}

variable "memory_limit" {
    description = "Memory limit for the container"
    type        = string
    default     = "2Gi"
}

variable "cpu_limit" {
    description = "CPU limit for the container"
    type        = string
    default     = "1"
}
