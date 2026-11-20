# Terraform IaC Reference Checklist

## Security & Hygiene Gates
- [ ] `required_version` and provider constraints pinned in `versions.tf`
- [ ] Zero hardcoded credentials, tokens, or default passwords
- [ ] All sensitive variables and outputs marked `sensitive = true`
- [ ] Remote state backend configured with locking (no local `terraform.tfstate` committed)
- [ ] `terraform fmt -check` and `terraform validate` pass cleanly
