package handlers

import (
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
	"your_project/internal/service"
)

type WordsHandler struct {
	wordsService *service.WordsService
}

func NewWordsHandler(wordsService *service.WordsService) *WordsHandler {
	return &WordsHandler{wordsService: wordsService}
}

func (h *WordsHandler) GetWords(c *gin.Context) {
	page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
	itemsPerPage, _ := strconv.Atoi(c.DefaultQuery("items_per_page", "100"))

	paginatedWords, err := h.wordsService.GetWords(page, itemsPerPage)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, paginatedWords)
}

func (h *WordsHandler) GetWordByID(c *gin.Context) {
	id, err := strconv.ParseInt(c.Param("id"), 10, 64)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid word ID"})
		return
	}

	word, err := h.wordsService.GetWordByID(id)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, word)
}
