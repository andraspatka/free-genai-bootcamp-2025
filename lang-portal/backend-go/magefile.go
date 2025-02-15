//go:build mage
// +build mage

package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"path/filepath"
	"sort"
	"strings"

	_ "github.com/mattn/go-sqlite3"
)

// InitDB initializes the SQLite database
func InitDB() error {
	log.Println("Starting InitDB...")

	// Remove existing database if it exists
	if err := os.Remove("words.db"); err != nil && !os.IsNotExist(err) {
		log.Printf("Error removing existing database: %v", err)
		return err
	}

	// Open a new database connection
	db, err := sql.Open("sqlite3", "words.db")
	if err != nil {
		log.Printf("Error opening database connection: %v", err)
		return err
	}
	defer db.Close()

	log.Println("Database connection established")

	// Read the migration SQL
	migrationSQL, err := ioutil.ReadFile("db/migrations/0001_init.sql")
	if err != nil {
		log.Printf("Error reading migration file: %v", err)
		return fmt.Errorf("error reading migration file: %v", err)
	}

	log.Printf("Migration SQL read successfully. Length: %d bytes", len(migrationSQL))

	// Execute the migration SQL
	_, err = db.Exec(string(migrationSQL))
	if err != nil {
		log.Printf("Error executing migration: %v", err)
		return fmt.Errorf("error executing migration: %v", err)
	}

	log.Println("Database initialized successfully")
	return nil
}

// MigrateDB runs all migration SQL files in order
func MigrateDB() error {
	db, err := sql.Open("sqlite3", "words.db")
	if err != nil {
		return err
	}
	defer db.Close()

	// Get all migration files
	migrationFiles, err := filepath.Glob("db/migrations/*.sql")
	if err != nil {
		return err
	}

	// Sort migration files to ensure they run in order
	sort.Strings(migrationFiles)

	for _, migrationFile := range migrationFiles {
		migrationSQL, err := ioutil.ReadFile(migrationFile)
		if err != nil {
			return err
		}

		_, err = db.Exec(string(migrationSQL))
		if err != nil {
			return fmt.Errorf("error executing migration %s: %v", migrationFile, err)
		}
		log.Printf("Applied migration: %s", migrationFile)
	}

	return nil
}

// SeedData populates the database with seed data
func SeedData() error {
	db, err := sql.Open("sqlite3", "words.db")
	if err != nil {
		return err
	}
	defer db.Close()

	// Get all seed files
	seedFiles, err := filepath.Glob("db/seeds/data_*.json")
	if err != nil {
		return err
	}

	for _, seedFile := range seedFiles {
		// Extract group name from filename
		groupName := strings.TrimSuffix(filepath.Base(seedFile), filepath.Ext(seedFile))
		groupName = strings.Replace(groupName, "data_", "", 1)
		groupName = strings.Replace(groupName, "_it", " ", 1)

		// Create group first
		result, err := db.Exec("INSERT INTO groups (name) VALUES (?)", groupName)
		if err != nil {
			return err
		}
		groupID, err := result.LastInsertId()
		if err != nil {
			return err
		}

		// Read seed data
		data, err := ioutil.ReadFile(seedFile)
		if err != nil {
			return err
		}

		var words []struct {
			Italian string `json:"italian"`
			English string `json:"english"`
		}
		if err := json.Unmarshal(data, &words); err != nil {
			return err
		}

		// Insert words and link to group
		for _, word := range words {
			result, err := db.Exec("INSERT INTO words (italian, english) VALUES (?, ?)",
				word.Italian, word.English)
			if err != nil {
				return err
			}
			wordID, err := result.LastInsertId()
			if err != nil {
				return err
			}

			_, err = db.Exec("INSERT INTO words_groups (word_id, group_id) VALUES (?, ?)", wordID, groupID)
			if err != nil {
				return err
			}
		}

		log.Printf("Seeded data for group: %s", groupName)
	}

	data, err := ioutil.ReadFile("db/seeds/study_activities.json")
	if err != nil {
		return err
	}
	var study_activities []struct {
		Name           string `json:"name"`
		Description    string `json:"description"`
		StudySessionID int    `json:"study_session_id"`
	}
	if err := json.Unmarshal(data, &study_activities); err != nil {
		return err
	}

	// Insert study activities
	for _, activity := range study_activities {
		result, err := db.Exec("INSERT INTO study_activities (name, description, study_session_id) VALUES (?, ?, ?)",
			activity.Name, activity.Description, activity.StudySessionID)
		if err != nil {
			return err
		}
		activityID, err := result.LastInsertId()
		if err != nil {
			return err
		}
	}

	return nil
}

// Default target to run when just typing mage
func Default() {
	// Run all tasks in order
	if err := InitDB(); err != nil {
		log.Fatal(err)
	}
	if err := MigrateDB(); err != nil {
		log.Fatal(err)
	}
	if err := SeedData(); err != nil {
		log.Fatal(err)
	}
	fmt.Println("Database initialized, migrated, and seeded successfully!")
}
