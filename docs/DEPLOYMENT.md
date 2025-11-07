# Deployment Guide - Renewable DD Tool

This guide covers production deployment of the Renewable Energy Due Diligence Management Tool.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Infrastructure Setup](#infrastructure-setup)
3. [Google Cloud Setup](#google-cloud-setup)
4. [Database Setup](#database-setup)
5. [Backend Deployment](#backend-deployment)
6. [Frontend Deployment](#frontend-deployment)
7. [Security Configuration](#security-configuration)
8. [Monitoring Setup](#monitoring-setup)
9. [Maintenance](#maintenance)

## Prerequisites

### Required Accounts
- Google Cloud Platform account with billing enabled
- Domain name for the application
- SSL certificate (can use Let's Encrypt)
- Sentry account for error monitoring (optional)

### Required Software
- Docker and Docker Compose
- Kubernetes CLI (kubectl) - if using GKE
- Terraform (optional, for infrastructure as code)

### Minimum Infrastructure Requirements
- **Backend**: 4 vCPU, 16GB RAM, 100GB SSD
- **Database**: PostgreSQL 14+, 8GB RAM, 200GB SSD
- **Redis**: 2GB RAM
- **Vector DB**: Pinecone (cloud) or self-hosted Weaviate

## Infrastructure Setup

### Option 1: Google Cloud Platform (Recommended)

#### 1. Create GCP Project
```bash
gcloud projects create renewable-dd-prod --name="Renewable DD Tool Production"
gcloud config set project renewable-dd-prod
```

#### 2. Enable Required APIs
```bash
gcloud services enable \
  compute.googleapis.com \
  container.googleapis.com \
  sqladmin.googleapis.com \
  cloudkms.googleapis.com \
  drive.googleapis.com \
  storage-api.googleapis.com
```

#### 3. Create GKE Cluster (Kubernetes)
```bash
gcloud container clusters create renewable-dd-cluster \
  --zone us-central1-a \
  --num-nodes 3 \
  --machine-type n2-standard-4 \
  --enable-autoscaling \
  --min-nodes 2 \
  --max-nodes 10 \
  --enable-autorepair \
  --enable-autoupgrade
```

#### 4. Create Cloud SQL Instance
```bash
gcloud sql instances create renewable-dd-db \
  --database-version=POSTGRES_14 \
  --tier=db-custom-4-16384 \
  --region=us-central1 \
  --backup \
  --backup-start-time=03:00 \
  --maintenance-window-day=SUN \
  --maintenance-window-hour=04
```

#### 5. Create Database
```bash
gcloud sql databases create renewable_dd \
  --instance=renewable-dd-db
```

## Google Cloud Setup

### 1. Set Up Cloud KMS for Encryption

```bash
# Create key ring
gcloud kms keyrings create renewable-dd-keyring \
  --location us-central1

# Create crypto key
gcloud kms keys create document-encryption-key \
  --location us-central1 \
  --keyring renewable-dd-keyring \
  --purpose encryption
```

### 2. Create Service Account

```bash
# Create service account
gcloud iam service-accounts create renewable-dd-sa \
  --display-name "Renewable DD Tool Service Account"

# Grant permissions
gcloud projects add-iam-policy-binding renewable-dd-prod \
  --member="serviceAccount:renewable-dd-sa@renewable-dd-prod.iam.gserviceaccount.com" \
  --role="roles/cloudkms.cryptoKeyEncrypterDecrypter"

gcloud projects add-iam-policy-binding renewable-dd-prod \
  --member="serviceAccount:renewable-dd-sa@renewable-dd-prod.iam.gserviceaccount.com" \
  --role="roles/cloudsql.client"

# Generate key
gcloud iam service-accounts keys create ~/renewable-dd-sa-key.json \
  --iam-account=renewable-dd-sa@renewable-dd-prod.iam.gserviceaccount.com
```

### 3. Set Up Google Drive API

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Navigate to "APIs & Services" > "Credentials"
3. Click "Create Credentials" > "OAuth 2.0 Client ID"
4. Choose "Web application"
5. Add authorized redirect URIs:
   - `https://your-domain.com/auth/callback`
   - `http://localhost:3000/auth/callback` (for development)
6. Download credentials JSON

### 4. Enable Google Drive API
```bash
gcloud services enable drive.googleapis.com
```

## Database Setup

### 1. Initialize Database Schema

```bash
# Connect to Cloud SQL
gcloud sql connect renewable-dd-db --user=postgres

# Or use connection string
export DATABASE_URL="postgresql://user:password@host:5432/renewable_dd"
```

### 2. Run Migrations

```bash
cd backend
source venv/bin/activate
alembic upgrade head
```

### 3. Create Application User

```sql
CREATE USER dd_app WITH PASSWORD 'your-secure-password';
GRANT ALL PRIVILEGES ON DATABASE renewable_dd TO dd_app;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO dd_app;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO dd_app;
```

## Backend Deployment

### Option 1: Docker Deployment

#### 1. Create Dockerfile

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 2. Build and Push Image

```bash
# Build image
docker build -t gcr.io/renewable-dd-prod/backend:v1.0.0 backend/

# Push to Google Container Registry
docker push gcr.io/renewable-dd-prod/backend:v1.0.0
```

#### 3. Create Kubernetes Deployment

```yaml
# k8s/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: renewable-dd-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: renewable-dd-backend
  template:
    metadata:
      labels:
        app: renewable-dd-backend
    spec:
      containers:
      - name: backend
        image: gcr.io/renewable-dd-prod/backend:v1.0.0
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: renewable-dd-secrets
              key: database-url
        - name: GOOGLE_APPLICATION_CREDENTIALS
          value: /secrets/sa-key.json
        volumeMounts:
        - name: sa-key
          mountPath: /secrets
          readOnly: true
        resources:
          requests:
            cpu: 1000m
            memory: 2Gi
          limits:
            cpu: 2000m
            memory: 4Gi
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: sa-key
        secret:
          secretName: gcp-sa-key
---
apiVersion: v1
kind: Service
metadata:
  name: renewable-dd-backend-service
spec:
  selector:
    app: renewable-dd-backend
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

#### 4. Deploy to Kubernetes

```bash
# Create secrets
kubectl create secret generic renewable-dd-secrets \
  --from-literal=database-url="$DATABASE_URL" \
  --from-literal=secret-key="$SECRET_KEY" \
  --from-literal=openai-api-key="$OPENAI_API_KEY"

kubectl create secret generic gcp-sa-key \
  --from-file=sa-key.json=~/renewable-dd-sa-key.json

# Deploy application
kubectl apply -f k8s/backend-deployment.yaml
```

## Frontend Deployment

### 1. Create Production Build

```bash
cd frontend

# Create .env.production
cat > .env.production << EOF
NEXT_PUBLIC_API_URL=https://api.your-domain.com
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-client-id
EOF

# Build
npm run build
```

### 2. Deploy to Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

### 3. Or Deploy to Google Cloud Run

```dockerfile
# frontend/Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package*.json ./
RUN npm ci --only=production

EXPOSE 3000
CMD ["npm", "start"]
```

```bash
# Build and deploy
gcloud builds submit --tag gcr.io/renewable-dd-prod/frontend
gcloud run deploy renewable-dd-frontend \
  --image gcr.io/renewable-dd-prod/frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## Security Configuration

### 1. Set Up SSL/TLS

```bash
# Using cert-manager with Let's Encrypt
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create ClusterIssuer
cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

### 2. Configure Firewall Rules

```bash
# Allow only HTTPS traffic
gcloud compute firewall-rules create allow-https \
  --allow tcp:443 \
  --source-ranges 0.0.0.0/0 \
  --target-tags https-server

# Restrict database access
gcloud compute firewall-rules create allow-postgres \
  --allow tcp:5432 \
  --source-ranges 10.0.0.0/8 \
  --target-tags postgres-server
```

### 3. Enable Cloud Armor (DDoS Protection)

```bash
gcloud compute security-policies create renewable-dd-policy \
  --description "Security policy for Renewable DD Tool"

gcloud compute security-policies rules create 1000 \
  --security-policy renewable-dd-policy \
  --expression "origin.region_code == 'CN'" \
  --action "deny-403"
```

## Monitoring Setup

### 1. Set Up Cloud Monitoring

```bash
# Enable monitoring API
gcloud services enable monitoring.googleapis.com

# Create uptime check
gcloud monitoring uptime create https://your-domain.com/health
```

### 2. Configure Sentry

```bash
# In backend .env
SENTRY_DSN=your-sentry-dsn

# In frontend .env.production
NEXT_PUBLIC_SENTRY_DSN=your-sentry-dsn
```

### 3. Set Up Logging

```yaml
# k8s/fluentd-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluentd-config
data:
  fluent.conf: |
    <source>
      @type tail
      path /var/log/containers/*.log
      tag kubernetes.*
      format json
    </source>

    <match **>
      @type google_cloud
    </match>
```

## Maintenance

### Backup Strategy

```bash
# Automated daily backups
gcloud sql backups create \
  --instance renewable-dd-db \
  --async

# Export to Cloud Storage
gcloud sql export sql renewable-dd-db \
  gs://renewable-dd-backups/backup-$(date +%Y%m%d).sql \
  --database=renewable_dd
```

### Update Procedure

```bash
# 1. Build new version
docker build -t gcr.io/renewable-dd-prod/backend:v1.1.0 backend/

# 2. Push image
docker push gcr.io/renewable-dd-prod/backend:v1.1.0

# 3. Update deployment
kubectl set image deployment/renewable-dd-backend \
  backend=gcr.io/renewable-dd-prod/backend:v1.1.0

# 4. Monitor rollout
kubectl rollout status deployment/renewable-dd-backend

# 5. Rollback if needed
kubectl rollout undo deployment/renewable-dd-backend
```

### Scaling

```bash
# Horizontal pod autoscaling
kubectl autoscale deployment renewable-dd-backend \
  --cpu-percent=70 \
  --min=3 \
  --max=10

# Scale database
gcloud sql instances patch renewable-dd-db \
  --tier=db-custom-8-32768
```

## Cost Optimization

1. **Use Preemptible VMs** for non-critical workloads
2. **Enable autoscaling** to scale down during low usage
3. **Use Cloud CDN** for frontend assets
4. **Set up budget alerts**
5. **Review and optimize queries** to reduce database load

## Troubleshooting

### Common Issues

1. **Connection to Cloud SQL fails**
   - Verify Cloud SQL Proxy is running
   - Check firewall rules
   - Verify service account permissions

2. **KMS decryption errors**
   - Ensure service account has `cloudkms.cryptoKeyEncrypterDecrypter` role
   - Verify key exists and is enabled

3. **Out of memory errors**
   - Increase pod memory limits
   - Review memory usage patterns
   - Consider horizontal scaling

### Logs

```bash
# Backend logs
kubectl logs -f deployment/renewable-dd-backend

# Database logs
gcloud sql operations list --instance renewable-dd-db

# Application logs in Cloud Logging
gcloud logging read "resource.type=k8s_container AND resource.labels.cluster_name=renewable-dd-cluster"
```

## Security Checklist

- [ ] SSL/TLS enabled for all endpoints
- [ ] Google Cloud KMS configured for encryption
- [ ] Service accounts follow principle of least privilege
- [ ] Secrets stored in Kubernetes Secrets or Secret Manager
- [ ] Database has strong passwords and restricted access
- [ ] Firewall rules properly configured
- [ ] DDoS protection enabled
- [ ] Audit logging enabled
- [ ] Regular security updates scheduled
- [ ] Penetration testing completed
- [ ] Data backup and recovery tested
- [ ] Incident response plan documented

## Support

For deployment issues, contact your DevOps team or refer to:
- [Google Cloud Documentation](https://cloud.google.com/docs)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- Project repository issues page
