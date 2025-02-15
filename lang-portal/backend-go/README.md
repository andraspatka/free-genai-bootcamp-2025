## DOESN't WORK !
I give up, might come back to it later...


# Local server setup

```
export PATH=$(go env GOPATH)/bin:$PATH
```

```
# Initialize a new Go module
go mod init <module-name>

# Add a dependency
go get <package-path>

# Remove an unused dependency
go mod tidy

# Verify module dependencies
go mod verify
```

```
# Build the project
go build

# Run the project
go run main.go

# Build for a specific operating system and architecture
GOOS=darwin GOARCH=amd64 go build

# Install the package
go install
```