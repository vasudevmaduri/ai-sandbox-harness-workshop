---
name: terraform-iac
description: Production Infrastructure-as-Code workflow for modular Terraform configurations with pinned versions, zero hardcoded secrets, least-privilege IAM, and plan-only autonomous safety.
---

# Terraform IaC Skill

Use this skill when creating or modifying Terraform modules (`.tf`). Consult [references/checklist.md](./references/checklist.md) for security and module structure standards.

## 1. Structural & Security Invariants
- **Strict Version Pinning**: Always declare `required_version` and pessimistic provider constraints (`~>`) in `versions.tf`.
- **Standard Module Layout**: Separate `versions.tf`, `variables.tf` (with `description`, `type`, and `validation` blocks), `main.tf`, and `outputs.tf`.
- **Zero Hardcoded Secrets**: Never place API keys, passwords, or private keys in `.tf` or `.tfvars`. Mark secret inputs `sensitive = true` and source runtime secrets from Secret Manager / KMS.
- **Least Privilege & Encryption**: Never grant wildcard `*` IAM actions/resources without justification; enforce encryption at rest and block public bucket access by default.

## 2. Autonomous Safety Boundary
- Allowed commands: `terraform fmt -check -recursive`, `terraform validate`, `terraform plan`.
- **Hard-Blocked (`PreToolUse`)**: `terraform apply -auto-approve`, `terraform destroy -auto-approve`, or raw state edits.
