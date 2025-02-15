package models

import "time"

type StudyActivity struct {
    ID            int       `json:"id"`
    Name          string    `json:"name"`
    ThumbnailURL  string    `json:"thumbnail_url"`
    Description   string    `json:"description"`
    StudySessionID int       `json:"study_session_id"`
}

func (sa *StudyActivity) TableName() string {
    return "study_activities"
}
