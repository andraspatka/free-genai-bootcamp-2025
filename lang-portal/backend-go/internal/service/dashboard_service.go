package service

import (
	"database/sql"
	"time"

	"github.com/andraspatka/free-genai-bootcamp-2025/backend_go/internal/models"
)

type DashboardService struct {
	db *sql.DB
}

func NewDashboardService(db *sql.DB) *DashboardService {
	return &DashboardService{db: db}
}

func (s *DashboardService) GetLastStudySession() (*models.StudySession, error) {
	query := `
		SELECT 
			ss.id, 
			ss.group_id, 
			ss.created_at, 
			ss.study_activity_id, 
			g.name
		FROM study_sessions ss
		JOIN groups g ON ss.group_id = g.id
		ORDER BY ss.created_at DESC
		LIMIT 1
	`

	var session models.StudySession
	err := s.db.QueryRow(query).Scan(
		&session.ID, 
		&session.GroupID, 
		&session.CreatedAt, 
		&session.StudyActivityID, 
		&session.GroupName,
	)
	if err != nil {
		return nil, err
	}

	return &session, nil
}

func (s *DashboardService) GetStudyProgress() (*models.StudyProgress, error) {
	var progress models.StudyProgress

	// Total words studied
	query := `
		SELECT COUNT(DISTINCT word_id) 
		FROM word_review_items 
		WHERE correct = 1
	`
	err := s.db.QueryRow(query).Scan(&progress.TotalWordsStudied)
	if err != nil {
		return nil, err
	}

	// Total available words
	query = `SELECT COUNT(*) FROM words`
	err = s.db.QueryRow(query).Scan(&progress.TotalAvailableWords)
	if err != nil {
		return nil, err
	}

	return &progress, nil
}

func (s *DashboardService) GetQuickStats() (*models.DashboardQuickStats, error) {
	var stats models.DashboardQuickStats

	// Success rate
	query := `
		SELECT 
			ROUND(
				(CAST(SUM(CASE WHEN correct = 1 THEN 1 ELSE 0 END) AS FLOAT) / 
				CAST(COUNT(*) AS FLOAT)) * 100, 
				2
			) 
		FROM word_review_items
	`
	err := s.db.QueryRow(query).Scan(&stats.SuccessRate)
	if err != nil {
		return nil, err
	}

	// Total study sessions
	query = `SELECT COUNT(*) FROM study_sessions`
	err = s.db.QueryRow(query).Scan(&stats.TotalStudySessions)
	if err != nil {
		return nil, err
	}

	// Total active groups
	query = `SELECT COUNT(*) FROM groups`
	err = s.db.QueryRow(query).Scan(&stats.TotalActiveGroups)
	if err != nil {
		return nil, err
	}

	// Study streak days (simplified calculation)
	query = `
		SELECT COUNT(DISTINCT DATE(created_at)) 
		FROM study_sessions 
		WHERE created_at >= date('now', '-7 days')
	`
	err = s.db.QueryRow(query).Scan(&stats.StudyStreakDays)
	if err != nil {
		return nil, err
	}

	return &stats, nil
}
