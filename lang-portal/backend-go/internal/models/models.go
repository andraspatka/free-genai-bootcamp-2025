package models

import (
	"database/sql"
	"encoding/json"
	"time"
)

type Word struct {
	ID       int64           `json:"id"`
	Italian  string          `json:"italian"`
	English  string          `json:"english"`
	Parts    json.RawMessage `json:"parts"`
}

type Group struct {
	ID   int64  `json:"id"`
	Name string `json:"name"`
}

type StudySession struct {
	ID               int64     `json:"id"`
	GroupID          int64     `json:"group_id"`
	CreatedAt        time.Time `json:"created_at"`
	StudyActivityID  int64     `json:"study_activity_id"`
	GroupName        string    `json:"group_name,omitempty"`
}

type StudyActivity struct {
	ID            int64  `json:"id"`
	Name          string `json:"name"`
	ThumbnailURL  string `json:"thumbnail_url"`
	Description   string `json:"description"`
}

type WordReviewItem struct {
	ID             int64     `json:"id"`
	WordID         int64     `json:"word_id"`
	StudySessionID int64     `json:"study_session_id"`
	Correct        bool      `json:"correct"`
	CreatedAt      time.Time `json:"created_at"`
}

type DashboardQuickStats struct {
	SuccessRate       float64 `json:"success_rate"`
	TotalStudySessions int     `json:"total_study_sessions"`
	TotalActiveGroups int     `json:"total_active_groups"`
	StudyStreakDays   int     `json:"study_streak_days"`
}

type StudyProgress struct {
	TotalWordsStudied   int `json:"total_words_studied"`
	TotalAvailableWords int `json:"total_available_words"`
}

// Database connection helper
func GetDBConnection() (*sql.DB, error) {
	return sql.Open("sqlite3", "words.db")
}
