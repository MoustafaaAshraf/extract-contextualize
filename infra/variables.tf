variable "project_id" {
    type        = string
    description = "GCP project ID"
}

variable "region" {
    type        = string
    description = "GCP region"
    default     = "us-central1"
}

variable "service_name" {
    type        = string
    description = "Name of the Cloud Run service"
    default     = "my-ner-service"
}

variable "image_name" {
    type        = string
    description = "Full Docker image path (gcr.io/PROJECT_ID/IMAGE:TAG)"
}
