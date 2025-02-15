package handlers

import (
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
	"your_project/internal/service"
)

type StudyActivitiesHandler struct {
	studyActivitiesService *service.StudyActivityService
}

func NewStudyActivitiesHandler(studyActivitiesService *service.StudyActivityService) *StudyActivitiesHandler {
	return &StudyActivitiesHandler{studyActivitiesService: studyActivitiesService}
}

func (h *StudyActivitiesHandler) GetStudyActivity(c *gin.Context) {
	id, err := strconv.ParseInt(c.Param("id"), 10, 64)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid study activity ID"})
		return
	}

	activity, err := h.studyActivitiesService.GetStudyActivity(id)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, activity)
}

func (h *StudyActivitiesHandler) GetStudySessions(c *gin.Context) {
	id, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid study activity ID"})
		return
	}

	page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
	itemsPerPage, _ := strconv.Atoi(c.DefaultQuery("items_per_page", "100"))

	sessions, err := h.studyActivitiesService.GetStudySessions(id, page, itemsPerPage)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, sessions)
}

func (h *StudyActivitiesHandler) CreateStudyActivity(c *gin.Context) {
	var requestBody struct {
		GroupID           int64 `json:"group_id"`
		StudyActivityID   int64 `json:"study_activity_id"`
	}

	if err := c.BindJSON(&requestBody); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	studySessionID, err := h.studyActivitiesService.CreateStudyActivity(requestBody.GroupID, requestBody.StudyActivityID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusCreated, gin.H{
		"id": studySessionID,
	})
}
