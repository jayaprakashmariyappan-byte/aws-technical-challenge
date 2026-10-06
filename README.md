# AWS Technical Challenge — Scalable Web Application on AWS

**Candidate:** Jayaprakash Mariyappa &nbsp;|&nbsp; **Date:** October 2026 &nbsp;|&nbsp; **Account:** 399760685306 &nbsp;|&nbsp; **Region:** us-east-1

---

## Architecture

![Architecture Diagram](architecture-diagram.png)

---

## Solution Summary

| Layer | Service | Detail |
|-------|---------|--------|
| IaC | CloudFormation | 6 nested templates, single deploy command |
| Compute | EC2 + Auto Scaling | t3.small, min 2 / max 6, Amazon Linux 2023 |
| Load Balancer | Application Load Balancer | Internet-facing, multi-AZ, health checks |
| Database | RDS MySQL 8.0.46 | Multi-AZ, encrypted, deletion protection |
| Storage | S3 | Static assets, audit logs, ALB logs |
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
│   ├── app.py              # Flask REST API
│   └── requirements.txt
├── scripts/
│   └── deploy.sh           # One-command deployment
├── screenshots/            # AWS Console evidence
└── README.md
```

---

## Deployment

```bash
bash scripts/deploy.sh prod
```

Deploys all stacks in order: VPC → IAM → S3 → RDS (~15 min Multi-AZ) → Compute

---

## Evidence

### 1. Infrastructure as Code — CloudFormation Stacks

All 6 nested stacks deployed successfully via a single master CloudFormation template.

![CloudFormation Stacks](screenshots/01-cloudformation-stacks.png)
![CloudFormation Resources](screenshots/02-cloudformation-stacks-2.png)

---

### 2. Compute — EC2 Auto Scaling Group

2 instances running across us-east-1a and us-east-1b. Both healthy. Scaling limits: min 2, max 6.

![ASG Instances](screenshots/03-asg-instances.png)
![ASG Instances Detail](screenshots/04-asg-instances-2.png)

---

### 3. Networking — VPC Resource Map

VPC `prod-vpc` with 4 subnets (2 public, 2 private) across 2 AZs, Internet Gateway, NAT Gateway, and route tables.

![VPC Resource Map](screenshots/05-vpc-resource-map.png)
![VPC Resource Map Detail](screenshots/06-vpc-resource-map-2.png)

---

### 4. Additional Evidence

![Screenshot](screenshots/image007.png)
![Screenshot](screenshots/image008.png)
![Screenshot](screenshots/image009.png)
![Screenshot](screenshots/image010.png)
![Screenshot](screenshots/image011.png)
![Screenshot](screenshots/image012.png)
![Screenshot](screenshots/image013.png)
![Screenshot](screenshots/image014.png)
![Screenshot](screenshots/image015.png)
![Screenshot](screenshots/image016.png)
![Screenshot](screenshots/image017.png)
![Screenshot](screenshots/image018.png)
![Screenshot](screenshots/image019.png)
![Screenshot](screenshots/image020.png)
![Screenshot](screenshots/image021.png)
![Screenshot](screenshots/image022.png)

---

## Requirements Compliance

| Requirement | Status |
|-------------|--------|
| IaC — CloudFormation | ✅ 6 templates, single deploy command |
| Compute + Auto Scaling | ✅ ASG min:2 max:6, CPU + request tracking |
| VPC — public + private subnets | ✅ 2+2 subnets across 2 AZs |
| Internet Gateway + NAT Gateway | ✅ Both configured |
| Security Groups + NACLs | ✅ Least-privilege, layered |
| Elastic Load Balancer | ✅ ALB, multi-AZ, /health check |
| S3 static assets | ✅ Encrypted, versioned, lifecycle rules |
| RDS database | ✅ MySQL Multi-AZ, encrypted |
| IAM least privilege | ✅ 4 scoped roles, no wildcards |
| WAF + Shield DDoS | ✅ 7 WAF rules + Shield Standard |
| CloudWatch monitoring + alarms | ✅ Dashboard + 8 alarms + SNS |
| CloudTrail + Logs | ✅ Multi-region, 4 log groups |
| Backup strategy | ✅ AWS Backup daily+weekly + RDS 7-day |

---

*AWS Technical Challenge — Jayaprakash Mariyappa — October 2026*
