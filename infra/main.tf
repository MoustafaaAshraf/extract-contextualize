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

            # Dynamic environment variables
            dynamic "env" {
            for_each = var.env_vars
            content {
                name  = env.key
                value = env.value
            }
            }
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
