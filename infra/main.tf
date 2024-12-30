# Deploy a Cloud Run service
resource "google_cloud_run_service" "medical_entity_extraction_service" {
    name     = var.service_name
    location = var.region

    template {
        spec {
            containers {
                image = var.image_name
                
                resources {
                    limits = {
                        memory = var.memory_limit
                        cpu    = var.cpu_limit
                    }
                }

                # Add startup probe
                startup_probe {
                    http_get {
                        path = "/health"
                    }
                    initial_delay_seconds = 10
                    timeout_seconds = 3
                    period_seconds = 5
                    failure_threshold = 3
                }

                # Add environment variables
                dynamic "env" {
                    for_each = var.env_vars
                    content {
                        name  = env.key
                        value = env.value
                    }
                }

                # Add port configuration
                ports {
                    container_port = 8080
                }
            }

            # Add container configuration
            container_concurrency = 80
            timeout_seconds = 300
        }

        metadata {
            annotations = {
                "autoscaling.knative.dev/maxScale" = "10"
                "autoscaling.knative.dev/minScale" = "0"
            }
        }
    }

    traffic {
        percent         = 100
        latest_revision = true
    }
}

# Allow unauthenticated access
resource "google_cloud_run_service_iam_member" "noauth" {
    location = google_cloud_run_service.medical_entity_extraction_service.location
    project  = var.project_id
    service  = google_cloud_run_service.medical_entity_extraction_service.name
    role     = "roles/run.invoker"
    member   = "allUsers"
}
