# Terraform Base Infrastructure

## Prerequisites

- docker-compose
- docker
- AWS CLI credentials set in .env

## Commands

Build:

```
make build
```

Run shell:
```
make shell
```

## Terraform auto formatting

Install terraform locally:
`brew install terraform`

Set path to terraform in terraform extension settings. Get the path like `which terraform`.

```json
"terraform.languageServer.terraform.path": "/opt/homebrew/bin/terraform"
```
```