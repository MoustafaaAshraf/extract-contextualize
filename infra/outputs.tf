output "service_url" {
    value       = google_cloud_run_service.medical_entity_extraction_service.status[0].url
    description = "The URL of the deployed service"
}
