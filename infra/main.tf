# Deploy a Cloud Run service
resource "google_cloud_run_service" "default" {
    name     = var.service_name
    location = var.region

    template {
        spec {
        containers {
            image = var.image_name
            
            # Example resource config
            resources {
            limits = {
                memory = "512Mi"
                cpu    = "1"
            }
            }

            # Optional environment variables
            env {
            name  = "ENVIRONMENT"
            value = "production"
            }
        }
        }
    }

    traffic {
        percent         = 100
        latest_revision = true
    }

    # Make it publicly accessible
    autogenerate_revision_name = true
}

# Allow unauthenticated access
resource "google_cloud_run_service_iam_member" "noauth" {
    location        = google_cloud_run_service.default.location
    project         = var.project_id
    service         = google_cloud_run_service.default.name
    role            = "roles/run.invoker"
    member          = "allUsers"
}
