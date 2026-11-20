---
name: deployment-pipeline
description: Safe CI/CD, containerization, and deployment workflow enforcing non-destructive dry runs, pinned images, health checks, and rollback readiness.
---

# Deployment Pipeline Skill

Use this skill when creating or modifying Dockerfiles, CI/CD workflows, or deployment manifests:

1. **Reproducible Builds**: Pin base image versions and dependency lockfiles; avoid `:latest` tags in production configs.
2. **Least Privilege**: Run containers as non-root users, never bake `.env` or credentials into images, and separate build vs runtime stages.
3. **Safe Rollout & Dry-Run First**: Validate manifests (`docker build --check`, `terraform plan`, `kubectl --dry-run=client`) before any live deployment; never bypass manual approval gates.
4. **Rollback Plan**: Document or automate the exact rollback command and health-check probe for every deployment unit.
