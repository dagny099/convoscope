#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${PROJECT_ID:-gen-lang-client-0374286648}"
REGION="${REGION:-us-central1}"
AR_LOCATION="${AR_LOCATION:-us}"
SERVICE="${SERVICE:-convoscope}"
REPO_NAME="${REPO_NAME:-convoscope}"
IMAGE="${IMAGE:-${AR_LOCATION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${SERVICE}:latest}"
RUNTIME_SA_NAME="${RUNTIME_SA_NAME:-convoscope-runtime}"
RUNTIME_SA_EMAIL="${RUNTIME_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

echo "Deploying $SERVICE to project $PROJECT_ID ($REGION)"

# Context
gcloud config set project "$PROJECT_ID"
gcloud config set compute/region "$REGION"

# Enable services
gcloud services enable run.googleapis.com cloudbuild.googleapis.com secretmanager.googleapis.com artifactregistry.googleapis.com

# Artifact Registry repo (idempotent)
if ! gcloud artifacts repositories describe "$REPO_NAME" --location="$AR_LOCATION" >/dev/null 2>&1; then
  gcloud artifacts repositories create "$REPO_NAME" \
    --repository-format=docker \
    --location="$AR_LOCATION" \
    --description="Docker images for ${SERVICE}"
fi

# Service accounts
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')
CLOUDBUILD_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"
COMPUTE_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

for SA in "$CLOUDBUILD_SA"; do
  gcloud projects add-iam-policy-binding "$PROJECT_ID" --member="serviceAccount:${SA}" --role="roles/artifactregistry.writer" || true
  gcloud projects add-iam-policy-binding "$PROJECT_ID" --member="serviceAccount:${SA}" --role="roles/storage.admin" || true
  gcloud projects add-iam-policy-binding "$PROJECT_ID" --member="serviceAccount:${SA}" --role="roles/logging.logWriter" || true
done

for SA in "$COMPUTE_SA"; do
  gcloud projects add-iam-policy-binding "$PROJECT_ID" --member="serviceAccount:${SA}" --role="roles/artifactregistry.writer" || true
  gcloud projects add-iam-policy-binding "$PROJECT_ID" --member="serviceAccount:${SA}" --role="roles/logging.logWriter" || true
done

if ! gcloud iam service-accounts describe "$RUNTIME_SA_EMAIL" >/dev/null 2>&1; then
  gcloud iam service-accounts create "$RUNTIME_SA_NAME" --display-name "Convoscope Cloud Run runtime"
fi

gcloud projects add-iam-policy-binding "$PROJECT_ID" --member="serviceAccount:${RUNTIME_SA_EMAIL}" --role="roles/secretmanager.secretAccessor" || true
gcloud projects add-iam-policy-binding "$PROJECT_ID" --member="serviceAccount:${RUNTIME_SA_EMAIL}" --role="roles/artifactregistry.reader" || true

# Build image
gcloud builds submit --tag "$IMAGE"

# Deploy
gcloud run deploy "$SERVICE" \
  --image "$IMAGE" \
  --region "$REGION" \
  --allow-unauthenticated \
  --no-use-http2 \
  --update-annotations run.googleapis.com/invoker-iam-disabled=true \
  --service-account "$RUNTIME_SA_EMAIL" \
  --cpu 1 --memory 512Mi --concurrency 10 \
  --min-instances 0 --max-instances 1 \
  --set-env-vars DEFAULT_LLM_PROVIDER=openai,DEFAULT_TEMPERATURE=0.7,MAX_CONVERSATION_HISTORY=100 \
  --set-secrets OPENAI_API_KEY=OPENAI_API_KEY:latest,ANTHROPIC_API_KEY=ANTHROPIC_API_KEY:latest,GEMINI_API_KEY=GEMINI_API_KEY:latest


URL=$(gcloud run services describe "$SERVICE" --region "$REGION" --format='value(status.url)')
echo "✅ Service deployed at: $URL"
