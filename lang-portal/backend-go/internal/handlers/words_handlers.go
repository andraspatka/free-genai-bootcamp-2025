package handlers

import (
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
	"github.com/andraspatka/free-genai-bootcamp-2025/backend_go/internal/service"
)

type WordsHandlers struct {
	wordsService *service.WordsService
}

func NewWordsHandlers(wordsService *service.WordsService) *WordsHandlers {
	return &WordsHandlers{wordsService: wordsService}
}

func (h *WordsHandlers) GetWords(c *gin.Context) {
	page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
	itemsPerPage, _ := strconv.Atoi(c.DefaultQuery("items_per_page", "100"))

	words, err := h.wordsService.GetWords(page, itemsPerPage)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, words)
}

func (h *WordsHandlers) GetWordByID(c *gin.Context) {
	wordID, err := strconv.ParseInt(c.Param("id"), 10, 64)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid word ID"})
		return
	}

	word, err := h.wordsService.GetWordByID(wordID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, word)
}

type StudyActivityHandlers struct {
	studyActivityService *service.StudyActivityService
}

func NewStudyActivityHandlers(studyActivityService *service.StudyActivityService) *StudyActivityHandlers {
	return &StudyActivityHandlers{studyActivityService: studyActivityService}
}

func (h *StudyActivityHandlers) GetStudyActivity(c *gin.Context) {
	activityID, err := strconv.ParseInt(c.Param("id"), 10, 64)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid activity ID"})
		return
	}

	activity, err := h.studyActivityService.GetStudyActivity(activityID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, activity)
}

func (h *StudyActivityHandlers) GetStudySessions(c *gin.Context) {
	activityID, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid activity ID"})
		return
	}

	page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
	itemsPerPage, _ := strconv.Atoi(c.DefaultQuery("items_per_page", "100"))

	sessions, err := h.studyActivityService.GetStudySessions(activityID, page, itemsPerPage)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, sessions)
}

func (h *StudyActivityHandlers) CreateStudyActivity(c *gin.Context) {
	var requestBody struct {
		GroupID           int64 `json:"group_id"`
		StudyActivityID   int64 `json:"study_activity_id"`
	}

	if err := c.BindJSON(&requestBody); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	sessionID, err := h.studyActivityService.CreateStudyActivity(
		requestBody.GroupID, 
		requestBody.StudyActivityID,
	)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusCreated, gin.H{
		"id": sessionID,
		"group_id": requestBody.GroupID,
	})
}

func (h *StudyActivityHandlers) RecordWordReview(c *gin.Context) {
	wordID, err := strconv.ParseInt(c.Param("word_id"), 10, 64)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid word ID"})
		return
	}

	studySessionID, err := strconv.ParseInt(c.Param("study_session_id"), 10, 64)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid study session ID"})
		return
	}

	var requestBody struct {
		Correct bool `json:"correct"`
	}

	if err := c.BindJSON(&requestBody); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	reviewItemID, err := h.studyActivityService.RecordWordReview(
		wordID, 
		studySessionID, 
		requestBody.Correct,
	)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusCreated, gin.H{
		"success": true,
		"word_id": wordID,
		"study_session_id": studySessionID,
		"correct": requestBody.Correct,
		"created_at": time.Now().Format(time.RFC3339),
	})
}
