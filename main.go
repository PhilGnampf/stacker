package main

import (
    "encoding/json"
    "io/ioutil"
    "log"
    "net/http"
    "os"
)

type Highscore struct {
    Password  string `json:"password,omitempty"`
    Highscore int    `json:"highscore"`
}

func getHighscores(w http.ResponseWriter, r *http.Request) {
    // Set CORS headers
    w.Header().Set("Access-Control-Allow-Origin", "*")
    w.Header().Set("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    w.Header().Set("Access-Control-Allow-Headers", "Content-Type")
    
    file, err := os.Open("/app/highscore.json")
    if err != nil {
        http.Error(w, "Could not open highscore.json", http.StatusInternalServerError)
        return
    }
    defer file.Close()

    byteValue, err := ioutil.ReadAll(file)
    if err != nil {
        http.Error(w, "Could not read highscore.json", http.StatusInternalServerError)
        return
    }

    var highscores map[string]Highscore
    if err := json.Unmarshal(byteValue, &highscores); err != nil {
        http.Error(w, "Could not parse highscore.json", http.StatusInternalServerError)
        return
    }

    // Remove passwords from the response
    for username := range highscores {
        highscores[username] = Highscore{
            Highscore: highscores[username].Highscore,
        }
    }

    w.Header().Set("Content-Type", "application/json")
    if err := json.NewEncoder(w).Encode(highscores); err != nil {
        http.Error(w, "Could not encode highscores to JSON", http.StatusInternalServerError)
    }
}

func main() {
    http.HandleFunc("/highscores", getHighscores)
    log.Println("Server starting on port 9090...")
    if err := http.ListenAndServe(":9090", nil); err != nil {
        log.Fatalf("Could not start server: %s\n", err)
    }
}
