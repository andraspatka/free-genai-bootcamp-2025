package models

import "time"

type StudySession struct {
    ID              int       `json:"id"`
    GroupID         int       `json:"group_id"`
    CreatedAt       time.Time `json:"created_at"`
    StartTime       time.Time `json:"start_time"`
    EndTime         time.Time `json:"end_time"`
    StudyActivityID int       `json:"study_activity_id"`
    GroupName       string    `json:"group_name"`
    ActivityName    string    `json:"activity_name"`
}

func (ss *StudySession) TableName() string {
    return "study_sessions"
}
