# AWS Technical Challenge — Scalable Web Application

**Candidate:** Jayaprakash Mariyappa &nbsp;|&nbsp; **Date:** October 2026 &nbsp;|&nbsp; **Region:** us-east-1

---

## Architecture

![Architecture Diagram](architecture-diagram.png)

---

## Solution Summary

A production-grade scalable web application built entirely on AWS using CloudFormation IaC.

| Layer | Service | Detail |
|-------|---------|--------|
| IaC | CloudFormation | 6 nested templates, single deploy command |
| Compute | EC2 + Auto Scaling | t3.small, min 2 / max 6, Amazon Linux 2023 |
| Load Balancer | Application Load Balancer | Internet-facing, multi-AZ, health checks |
| Database | RDS MySQL 8.0.46 | Multi-AZ, encrypted, deletion protection |
| Storage | S3 | 3 buckets — static assets, audit logs, ALB logs |
| Security | WAF v2 + Shield Standard | 7 WAF rules incl. Layer 7 DDoS protection |
| Monitoring | CloudWatch | Dashboard, 8 alarms, 4 log groups |
| Audit | CloudTrail | Multi-region, log file validation |
| Backup | AWS Backup | Daily (30-day) + weekly (90-day) plans |

---

## Repository Structure

```
├── cloudformation/
│   ├── 01-vpc.yaml         # VPC, subnets, IGW, NAT GW, NACLs, SGs, Flow Logs
│   ├── 02-iam.yaml         # IAM roles — EC2, RDS, Backup, CloudTrail
│   ├── 03-rds.yaml         # RDS MySQL Multi-AZ, alarms, SSM params
│   ├── 04-s3.yaml          # S3 buckets (static, audit, ALB logs)
│   ├── 05-compute.yaml     # ALB, ASG, WAF, CloudTrail, CW Dashboard
│   └── 06-master.yaml      # Master stack — orchestrates all nested stacks
├── app/
│   ├── app.py              # Flask REST API (/, /health, /db-check)
│   └── requirements.txt
├── scripts/
│   └── deploy.sh           # One-command deployment
├── architecture-diagram.png
├── architecture-diagram.drawio
├── Evidence-Document.html  # Full evidence with screenshots
└── README.md
```

---

## Deployment

```bash
bash scripts/deploy.sh prod
```

Deploys all stacks in order: VPC → IAM → S3 → RDS (~15 min Multi-AZ) → Compute

---

## Network Layout

```
Internet
    │
[AWS WAF v2 — 7 rules]
    │
[ALB — Public Subnets: 10.0.1.0/24, 10.0.2.0/24]
    │
[ASG EC2 — Private Subnets: 10.0.3.0/24, 10.0.4.0/24]
    │
[RDS MySQL Multi-AZ — Private Subnets]
```

| Subnet | CIDR | AZ | Resources |
|--------|------|----|-----------|
| Public 1 | 10.0.1.0/24 | us-east-1a | ALB, NAT Gateway |
| Public 2 | 10.0.2.0/24 | us-east-1b | ALB |
| Private 1 | 10.0.3.0/24 | us-east-1a | EC2, RDS Primary |
| Private 2 | 10.0.4.0/24 | us-east-1b | EC2, RDS Standby |

---

## Security

| Control | Implementation |
|---------|---------------|
| WAF | OWASP Top 10, SQLi, Bad Inputs, Rate Limit, DDoS, Anonymous IP, IP Reputation |
| Shield | Standard — automatic infrastructure DDoS protection |
| IAM | 4 least-privilege roles, no wildcard permissions |
| Network | EC2 + RDS in private subnets, no direct internet exposure |
| Secrets | DB credentials in SSM Parameter Store, never in code |
| Encryption | All S3 buckets AES-256, RDS encrypted at rest, HTTPS-only bucket policies |
| Access | SSM Session Manager — no SSH open to internet |

---

## Monitoring

| Type | Detail |
|------|--------|
| Dashboard | `prod-app-dashboard` — ALB, ASG, EC2, WAF metrics |
| Alarms (8) | EC2 CPU, ALB latency p99, ALB 5xx, WAF blocks, RDS CPU, RDS storage, RDS connections, RDS latency |
| Log Groups | `/aws/app/prod/application`, `/aws/app/prod/system`, `/aws/cloudtrail/prod`, `/aws/vpc/flowlogs/prod` |

---

## Requirements Compliance

| Requirement | Status |
|-------------|--------|
| Infrastructure as Code | ✅ CloudFormation — 6 templates |
| Compute + Auto Scaling | ✅ EC2 ASG min:2 max:6, target tracking |
| VPC — public + private subnets | ✅ 2+2 subnets, 2 AZs |
| Internet Gateway + NAT Gateway | ✅ Both configured |
| Security Groups + NACLs | ✅ Least-privilege, layered |
| Elastic Load Balancer | ✅ ALB, multi-AZ, /health check |
| S3 static assets | ✅ Encrypted, versioned, lifecycle |
| RDS database | ✅ MySQL Multi-AZ, encrypted |
| IAM least privilege | ✅ 4 scoped roles |
| WAF + Shield DDoS | ✅ 7 WAF rules + Shield Standard |
| CloudWatch monitoring + alarms | ✅ Dashboard + 8 alarms + SNS |
| CloudTrail + Logs | ✅ Multi-region, 4 log groups |
| Backup strategy | ✅ AWS Backup daily+weekly + RDS 7-day |

---

## Evidence

Full implementation evidence with AWS Console screenshots: **[Evidence-Document.html](Evidence-Document.html)**

---

*AWS Technical Challenge — Jayaprakash Mariyappa — October 2026*
