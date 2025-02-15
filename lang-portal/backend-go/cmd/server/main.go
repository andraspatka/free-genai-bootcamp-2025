package main

import (
	"log"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"

	"github.com/andraspatka/free-genai-bootcamp-2025/backend_go/internal/handlers"
	"github.com/andraspatka/free-genai-bootcamp-2025/backend_go/internal/models"
	"github.com/andraspatka/free-genai-bootcamp-2025/backend_go/internal/service"
)

func main() {
	// Open database connection
	db, err := models.GetDBConnection()
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	defer db.Close()

	// Initialize services
	dashboardService := service.NewDashboardService(db)
	wordsService := service.NewWordsService(db)
	studyActivityService := service.NewStudyActivityService(db)

	// Initialize handlers
	dashboardHandlers := handlers.NewDashboardHandlers(dashboardService)
	wordsHandlers := handlers.NewWordsHandlers(wordsService)
	studyActivityHandlers := handlers.NewStudyActivityHandlers(studyActivityService)

	// Setup Gin router
	router := gin.Default()

	// Dashboard routes
	router.GET("/api/dashboard/last-study-session", dashboardHandlers.GetLastStudySession)
	router.GET("/api/dashboard/study-progress", dashboardHandlers.GetStudyProgress)
	router.GET("/api/dashboard/quick-stats", dashboardHandlers.GetQuickStats)

	// Words routes
	router.GET("/api/words", wordsHandlers.GetWords)
	router.GET("/api/words/:id", wordsHandlers.GetWordByID)

	// Study Activity routes
	router.GET("/api/study-activities/:id", studyActivityHandlers.GetStudyActivity)
	router.GET("/api/study-activities/:id/study-sessions", studyActivityHandlers.GetStudySessions)
	router.POST("/api/study-activities", studyActivityHandlers.CreateStudyActivity)
	router.POST("/api/study-activities/:study_session_id/words/:word_id/review", studyActivityHandlers.RecordWordReview)

	// Start server
	log.Println("Starting server on :8080")
	if err := router.Run(":8080"); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}
