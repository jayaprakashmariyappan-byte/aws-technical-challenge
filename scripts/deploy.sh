#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# deploy.sh — Upload CFT templates to S3 then deploy/update the master stack.
# Usage:  ./scripts/deploy.sh [dev|staging|prod]
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

ENV=${1:-prod}
REGION=${AWS_DEFAULT_REGION:-us-east-1}
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
TEMPLATES_BUCKET="${ENV}-cfn-templates-${ACCOUNT_ID}"
TEMPLATES_PREFIX="scalable-app"
STACK_NAME="${ENV}-scalable-app"

echo "==> Deploying environment: $ENV  |  region: $REGION  |  account: $ACCOUNT_ID"

# ── 1. Create templates bucket if it doesn't exist ─────────────────────────
if ! aws s3 ls "s3://${TEMPLATES_BUCKET}" 2>/dev/null; then
  echo "==> Creating CFN templates bucket: ${TEMPLATES_BUCKET}"
  aws s3 mb "s3://${TEMPLATES_BUCKET}" --region "${REGION}"
  aws s3api put-bucket-versioning \
    --bucket "${TEMPLATES_BUCKET}" \
    --versioning-configuration Status=Enabled
  aws s3api put-bucket-encryption \
    --bucket "${TEMPLATES_BUCKET}" \
    --server-side-encryption-configuration \
    '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'
  aws s3api put-public-access-block \
    --bucket "${TEMPLATES_BUCKET}" \
    --public-access-block-configuration \
    "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
fi

# ── 2. Upload all CFT files ────────────────────────────────────────────────
echo "==> Uploading CloudFormation templates..."
aws s3 sync ./cloudformation/ \
  "s3://${TEMPLATES_BUCKET}/${TEMPLATES_PREFIX}/" \
  --exclude "*" --include "*.yaml" \
  --sse AES256

TEMPLATES_URL="https://s3.amazonaws.com/${TEMPLATES_BUCKET}/${TEMPLATES_PREFIX}"

# ── 3. Prompt for sensitive parameters ────────────────────────────────────
read -rsp "Enter RDS master password (min 8 chars): " DB_PASS
echo

# ── 4. Deploy / update master stack ───────────────────────────────────────
echo "==> Deploying master stack: ${STACK_NAME}"
aws cloudformation deploy \
  --stack-name "${STACK_NAME}" \
  --template-file "./cloudformation/06-master.yaml" \
  --capabilities CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND \
  --region "${REGION}" \
  --disable-rollback \
  --parameter-overrides \
    EnvironmentName="${ENV}" \
    TemplatesBucketURL="${TEMPLATES_URL}" \
    DBMasterPassword="${DB_PASS}" \
    AlertEmail="${ALERT_EMAIL:-ops-team@example.com}" \
    MultiAZ="${MULTI_AZ:-true}" \
  --no-fail-on-empty-changeset

echo ""
echo "==> Stack outputs:"
aws cloudformation describe-stacks \
  --stack-name "${STACK_NAME}" \
  --region "${REGION}" \
  --query 'Stacks[0].Outputs[*].{Key:OutputKey,Value:OutputValue}' \
  --output table

# ── 5. Store RDS endpoint in SSM for app servers ───────────────────────────
RDS_ENDPOINT=$(aws cloudformation describe-stacks \
  --stack-name "${STACK_NAME}" \
  --region "${REGION}" \
  --query "Stacks[0].Outputs[?OutputKey=='RDSEndpoint'].OutputValue" \
  --output text)

# ── 5. SSM parameters are now managed by CloudFormation (03-rds.yaml, 04-s3.yaml) ──

echo ""
echo "✅  Deployment complete!"
echo "   Application URL: http://$(aws cloudformation describe-stacks \
  --stack-name "${STACK_NAME}" --region "${REGION}" \
  --query "Stacks[0].Outputs[?OutputKey=='ApplicationURL'].OutputValue" \
  --output text)"
