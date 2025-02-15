package models

import "time"

type WordReviewItem struct {
    ID             int       `json:"id"`
    WordID         int       `json:"word_id"`
    StudySessionID int       `json:"study_session_id"`
    Correct        bool      `json:"correct"`
    CreatedAt      time.Time `json:"created_at"`
}

func (wri *WordReviewItem) TableName() string {
    return "word_review_items"
}
