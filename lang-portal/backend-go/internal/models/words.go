package models

type Word struct {
    ID       int    `json:"id"`
    Italian  string `json:"italian"`
    English  string `json:"english"`
    CorrectCount int `json:"correct_count"`
    WrongCount  int `json:"wrong_count"`
}

func (w *Word) TableName() string {
    return "words"
}
