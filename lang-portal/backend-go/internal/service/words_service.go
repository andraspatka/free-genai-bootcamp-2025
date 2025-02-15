package service

import (
	"database/sql"
	"fmt"

	"github.com/andraspatka/free-genai-bootcamp-2025/backend_go/internal/models"
)

type WordsService struct {
	db *sql.DB
}

func NewWordsService(db *sql.DB) *WordsService {
	return &WordsService{db: db}
}

type PaginatedWords struct {
	Items      []models.Word `json:"items"`
	Pagination Pagination    `json:"pagination"`
}

type Pagination struct {
	CurrentPage  int `json:"current_page"`
	TotalPages   int `json:"total_pages"`
	TotalItems   int `json:"total_items"`
	ItemsPerPage int `json:"items_per_page"`
}

func (s *WordsService) GetWords(page, itemsPerPage int) (*PaginatedWords, error) {
	// Calculate total items
	var totalItems int
	err := s.db.QueryRow("SELECT COUNT(*) FROM words").Scan(&totalItems)
	if err != nil {
		return nil, err
	}

	// Calculate pagination
	totalPages := (totalItems + itemsPerPage - 1) / itemsPerPage
	offset := (page - 1) * itemsPerPage

	// Fetch words with their review statistics
	query := `
		SELECT 
			w.id, 
			w.italian, 
			w.english, 
			w.parts,
			COALESCE(SUM(CASE WHEN wri.correct = 1 THEN 1 ELSE 0 END), 0) as correct_count,
			COALESCE(SUM(CASE WHEN wri.correct = 0 THEN 1 ELSE 0 END), 0) as wrong_count
		FROM words w
		LEFT JOIN word_review_items wri ON w.id = wri.word_id
		GROUP BY w.id
		LIMIT ? OFFSET ?
	`

	rows, err := s.db.Query(query, itemsPerPage, offset)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var words []models.Word
	for rows.Next() {
		var word models.Word
		var correctCount, wrongCount int
		if err := rows.Scan(
			&word.ID, 
			&word.Italian, 
			&word.English, 
			&word.Parts,
			&correctCount,
			&wrongCount,
		); err != nil {
			return nil, err
		}
		words = append(words, word)
	}

	return &PaginatedWords{
		Items: words,
		Pagination: Pagination{
			CurrentPage:  page,
			TotalPages:   totalPages,
			TotalItems:   totalItems,
			ItemsPerPage: itemsPerPage,
		},
	}, nil
}

func (s *WordsService) GetWordByID(id int64) (*models.Word, error) {
	query := `
		SELECT id, italian, english, parts 
		FROM words 
		WHERE id = ?
	`

	var word models.Word
	err := s.db.QueryRow(query, id).Scan(
		&word.ID, 
		&word.Italian, 
		&word.English, 
		&word.Parts,
	)
	if err != nil {
		return nil, err
	}

	return &word, nil
}

type StudyActivityService struct {
	db *sql.DB
}

func NewStudyActivityService(db *sql.DB) *StudyActivityService {
	return &StudyActivityService{db: db}
}

type PaginatedStudySessions struct {
	Items      []StudySessionDetail `json:"items"`
	Pagination Pagination           `json:"pagination"`
}

type StudySessionDetail struct {
	ID            int64  `json:"id"`
	ActivityName  string `json:"activity_name"`
	GroupName     string `json:"group_name"`
	StartTime     string `json:"start_time"`
	EndTime       string `json:"end_time"`
	ReviewItems   int    `json:"review_items_count"`
}

func (s *StudyActivityService) GetStudyActivity(id int64) (*models.StudyActivity, error) {
	query := `
		SELECT id, name, thumbnail_url, description 
		FROM study_activities 
		WHERE id = ?
	`

	var activity models.StudyActivity
	err := s.db.QueryRow(query, id).Scan(
		&activity.ID, 
		&activity.Name, 
		&activity.ThumbnailURL, 
		&activity.Description,
	)
	if err != nil {
		return nil, err
	}

	return &activity, nil
}

func (s *StudyActivityService) GetStudySessions(activityID, page, itemsPerPage int) (*PaginatedStudySessions, error) {
	// Calculate total items
	var totalItems int
	err := s.db.QueryRow(
		"SELECT COUNT(*) FROM study_sessions WHERE study_activity_id = ?", 
		activityID,
	).Scan(&totalItems)
	if err != nil {
		return nil, err
	}

	// Calculate pagination
	totalPages := (totalItems + itemsPerPage - 1) / itemsPerPage
	offset := (page - 1) * itemsPerPage

	// Fetch study sessions
	query := `
		SELECT 
			ss.id, 
			sa.name as activity_name, 
			g.name as group_name, 
			ss.created_at,
			(
				SELECT COUNT(*) 
				FROM word_review_items wri 
				WHERE wri.study_session_id = ss.id
			) as review_items_count
		FROM study_sessions ss
		JOIN study_activities sa ON ss.study_activity_id = sa.id
		JOIN groups g ON ss.group_id = g.id
		WHERE ss.study_activity_id = ?
		ORDER BY ss.created_at DESC
		LIMIT ? OFFSET ?
	`

	rows, err := s.db.Query(query, activityID, itemsPerPage, offset)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var sessions []StudySessionDetail
	for rows.Next() {
		var session StudySessionDetail
		var startTime sql.NullString
		if err := rows.Scan(
			&session.ID, 
			&session.ActivityName, 
			&session.GroupName, 
			&startTime,
			&session.ReviewItems,
		); err != nil {
			return nil, err
		}
		session.StartTime = startTime.String
		sessions = append(sessions, session)
	}

	return &PaginatedStudySessions{
		Items: sessions,
		Pagination: Pagination{
			CurrentPage:  page,
			TotalPages:   totalPages,
			TotalItems:   totalItems,
			ItemsPerPage: itemsPerPage,
		},
	}, nil
}

func (s *StudyActivityService) CreateStudyActivity(groupID, studyActivityID int64) (int64, error) {
	query := `
		INSERT INTO study_sessions (group_id, study_activity_id) 
		VALUES (?, ?)
	`

	result, err := s.db.Exec(query, groupID, studyActivityID)
	if err != nil {
		return 0, err
	}

	return result.LastInsertId()
}

func (s *StudyActivityService) RecordWordReview(wordID, studySessionID int64, correct bool) (int64, error) {
	query := `
		INSERT INTO word_review_items (word_id, study_session_id, correct) 
		VALUES (?, ?, ?)
	`

	result, err := s.db.Exec(query, wordID, studySessionID, correct)
	if err != nil {
		return 0, err
	}

	return result.LastInsertId()
}
