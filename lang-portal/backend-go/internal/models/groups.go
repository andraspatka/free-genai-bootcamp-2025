package models

type Group struct {
    ID   int    `json:"id"`
    Name string `json:"name"`
}

func (g *Group) TableName() string {
    return "groups"
}
