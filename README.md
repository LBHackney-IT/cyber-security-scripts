# cyber-security-scripts
A selection of scripts the Cyber Security team uses to automate things.

This repository is open-source and publicly available, so we won't add anything secret here.

## Probely scripts

The [`probely`](probely/) directory holds a number of useful scripts to automate admin tasks on our vulnerability scanner.

## Secrets detection with ggshield

We use GitGuardian and `ggshield` to scan for secrets. Ensure you configure local pre-commit hooks when you clone the repository if you don't already have global pre-commit hooks configured:

1. [Install ggshield](https://docs.gitguardian.com/ggshield-docs/getting-started)
2. Add the [pre-commit](https://docs.gitguardian.com/ggshield-docs/integrations/git-hooks/pre-commit) and [pre-push](https://docs.gitguardian.com/ggshield-docs/integrations/git-hooks/pre-push) hooks. We recommend the global hooks as this provides protection across all your repositories.
