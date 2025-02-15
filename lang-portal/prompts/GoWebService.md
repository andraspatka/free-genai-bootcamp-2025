# Creating Web Services in Go with Gin Framework

## Why Gin?
- High-performance web framework
- Similar to FastAPI in ease of use
- Minimal overhead
- Robust routing
- Middleware support

## Project Setup

### 1. Initialize Go Module
```bash
# Create a new directory for your project
mkdir go-web-service
cd go-web-service

# Initialize Go module
go mod init mywebservice

# Install Gin
go get -u github.com/gin-gonic/gin
```

### 2. Basic Web Service Structure
```go
package main

import (
    "net/http"
    "github.com/gin-gonic/gin"
)

// Struct for representing data
type Item struct {
    ID    string `json:"id"`
    Name  string `json:"name"`
    Value int    `json:"value"`
}

// In-memory data store (simulating a database)
var items = []Item{
    {ID: "1", Name: "First Item", Value: 100},
    {ID: "2", Name: "Second Item", Value: 200},
}

func main() {
    // Create Gin router
    router := gin.Default()

    // Define routes
    router.GET("/items", getItems)
    router.GET("/items/:id", getItemByID)
    router.POST("/items", createItem)

    // Start server
    router.Run(":8080")
}

// GET all items
func getItems(c *gin.Context) {
    c.JSON(http.StatusOK, items)
}

// GET item by ID
func getItemByID(c *gin.Context) {
    id := c.Param("id")
    
    for _, item := range items {
        if item.ID == id {
            c.JSON(http.StatusOK, item)
            return
        }
    }
    
    c.JSON(http.StatusNotFound, gin.H{"error": "Item not found"})
}

// POST new item
func createItem(c *gin.Context) {
    var newItem Item
    
    // Bind JSON to struct
    if err := c.BindJSON(&newItem); err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
        return
    }
    
    // Add to items (would be database in real app)
    items = append(items, newItem)
    
    c.JSON(http.StatusCreated, newItem)
}
```

## Key Concepts

### Routing
- `router.GET()` defines GET endpoints
- `router.POST()` defines POST endpoints
- Other methods: `PUT()`, `DELETE()`, `PATCH()`

### Request Handling
- `c.Param()` gets URL parameters
- `c.Query()` gets query parameters
- `c.BindJSON()` parses JSON request body

### Response Handling
- `c.JSON()` sends JSON response
- First argument is HTTP status code
- Second argument is response body

### Error Handling
- Return appropriate HTTP status codes
- Use `gin.H{}` for creating error responses

## Middleware and Advanced Features

### CORS Middleware
```go
router.Use(cors.Default())
```

### Logging Middleware
```go
router.Use(gin.Logger())
router.Use(gin.Recovery())
```

### Validation
```go
type CreateItemRequest struct {
    Name  string `json:"name" binding:"required"`
    Value int    `json:"value" binding:"gte=0"`
}
```

## Dependency Management
- Use `go.mod` for managing dependencies
- `go get` to add new packages
- `go mod tidy` to clean up unused packages

## Testing
```go
func TestGetItems(t *testing.T) {
    router := setupRouter()
    w := httptest.NewRecorder()
    req, _ := http.NewRequest("GET", "/items", nil)
    router.ServeHTTP(w, req)
    
    assert.Equal(t, http.StatusOK, w.Code)
}
```

## Deployment Considerations
- Use environment variables for configuration
- Consider using Docker for containerization
- Use `go build` to create standalone binary

## Recommended Packages
- Routing: Gin (`github.com/gin-gonic/gin`)
- ORM: GORM (`gorm.io/gorm`)
- Validation: Go Playground Validator
- Configuration: Viper

## Performance Tips
- Use pointers for large structs
- Minimize allocations
- Use connection pools for databases
- Leverage Go's concurrency

## Learning Resources
- Gin Documentation: https://gin-gonic.com/docs/
- Go Web Programming Book
- Official Go Documentation

## Comparison with FastAPI
- Similar routing concepts
- Gin is compiled, FastAPI is interpreted
- Gin has less magic, more explicit
- Both support middleware
- Go is statically typed, Python is dynamically typed

## Example Project Structure
```
mywebservice/
├── main.go
├── handlers/
│   └── items.go
├── models/
│   └── item.go
├── services/
│   └── item_service.go
└── go.mod
```

## Best Practices
- Keep handlers thin
- Use services for business logic
- Separate concerns
- Use interfaces for flexibility
- Handle errors explicitly