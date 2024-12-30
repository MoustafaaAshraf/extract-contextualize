#!make
-include .env
export

POETRY := poetry

help: ## Display this help
	@grep -h -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

pre-commit: ## Run pre-commit
	@ ${POETRY} run pre-commit run --all-files

test: ## Run tests
	@ ${POETRY} run pytest

commit: ## commit using Commitizen
	@ ${POETRY} run cz c

run: ## Run the app
	@ ${POETRY} run uvicorn src.app:app --reload

build-image: ## Build the image
	@ docker build -t ${GCP_LOCATION}-docker.pkg.dev/${GCP_PROJECT_ID}/${GCP_REPOSITORY_NAME}/api:latest .

setup-gcp: ## Setup GCP resources needed before Terraform
	@ echo "Enabling required GCP APIs..."
	@ gcloud services enable run.googleapis.com
	@ gcloud services enable artifactregistry.googleapis.com
	@ gcloud services enable containerregistry.googleapis.com
	@ gcloud services enable aiplatform.googleapis.com

	@ echo "Creating Artifact Registry repository..."
	@ gcloud artifacts repositories create ${GCP_REPOSITORY_NAME} \
		--repository-format=docker \
		--location=${GCP_LOCATION} \
		--description="Docker repository for medical entity extraction" \
		|| true

	@ echo "Creating Terraform state bucket..."
	@ gcloud storage buckets create gs://${GCP_PROJECT_ID}-terraform-state \
		--location=${GCP_LOCATION} \
		--uniform-bucket-level-access \
		|| true

	@ echo "Creating service account for GitHub Actions..."
	@ gcloud iam service-accounts create github-actions \
		--description="Service account for GitHub Actions" \
		--display-name="GitHub Actions" \
		|| true

	@ echo "Granting necessary permissions..."
	@ gcloud projects add-iam-policy-binding ${GCP_PROJECT_ID} \
		--member="serviceAccount:github-actions@${GCP_PROJECT_ID}.iam.gserviceaccount.com" \
		--role="roles/run.admin"
	@ gcloud projects add-iam-policy-binding ${GCP_PROJECT_ID} \
		--member="serviceAccount:github-actions@${GCP_PROJECT_ID}.iam.gserviceaccount.com" \
		--role="roles/storage.admin"
	@ gcloud projects add-iam-policy-binding ${GCP_PROJECT_ID} \
		--member="serviceAccount:github-actions@${GCP_PROJECT_ID}.iam.gserviceaccount.com" \
		--role="roles/iam.serviceAccountUser"
	@ gcloud projects add-iam-policy-binding ${GCP_PROJECT_ID} \
		--member="serviceAccount:github-actions@${GCP_PROJECT_ID}.iam.gserviceaccount.com" \
		--role="roles/artifactregistry.admin"

	@ echo "Setup completed successfully!"

push-image: ## Push the image
	@ docker push ${GCP_LOCATION}-docker.pkg.dev/${GCP_PROJECT_ID}/${GCP_REPOSITORY_NAME}/api:latest

terraform-init: ## Initialize Terraform
	@ terraform init

terraform-plan: ## Plan Terraform
	@ terraform plan \
		-var="project_id=${GCP_PROJECT_ID}" \
		-var="image_name=us-central1-docker.pkg.dev/${GCP_PROJECT_ID}/${GCP_REPOSITORY_NAME}/api:latest" \
		-var='env_vars={"GCP_PROJECT_ID":"${GCP_PROJECT_ID}","GCP_MODEL_NAME":"${GCP_MODEL_NAME}","GCP_LOCATION":"${GCP_LOCATION}"}'

terraform-apply: ## Apply Terraform
	@ terraform apply \
		-var="project_id=${GCP_PROJECT_ID}" \
		-var="image_name=us-central1-docker.pkg.dev/${GCP_PROJECT_ID}/${GCP_REPOSITORY_NAME}/api:latest" \
		-var='env_vars={"GCP_PROJECT_ID":"${GCP_PROJECT_ID}","GCP_LOCATION":"${GCP_LOCATION}"}'

test-health: ## Test health endpoint
	@ curl -f $(shell terraform output -raw service_url)/health
