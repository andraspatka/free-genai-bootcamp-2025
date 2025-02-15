package handlers

import (
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
	"github.com/andraspatka/free-genai-bootcamp-2025/backend_go/internal/service"
)

type DashboardHandlers struct {
	dashboardService *service.DashboardService
}

func NewDashboardHandlers(dashboardService *service.DashboardService) *DashboardHandlers {
	return &DashboardHandlers{dashboardService: dashboardService}
}

func (h *DashboardHandlers) GetLastStudySession(c *gin.Context) {
	session, err := h.dashboardService.GetLastStudySession()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, session)
}

func (h *DashboardHandlers) GetStudyProgress(c *gin.Context) {
	progress, err := h.dashboardService.GetStudyProgress()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, progress)
}

func (h *DashboardHandlers) GetQuickStats(c *gin.Context) {
	stats, err := h.dashboardService.GetQuickStats()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, stats)
}
