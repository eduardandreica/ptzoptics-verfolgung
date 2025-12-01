# PTZOptics Face Tracking via HTTP

Dieses Projekt enthält ein Python-Skript, mit dem **PTZOptics-Kameras** über HTTP-Commands gesteuert werden können.  
Das Skript verfolgt automatisch Gesichter und passt die Kameraposition entsprechend an.

## Features
- Steuerung von PTZOptics-Kameras über HTTP-Requests
- Automatische Gesichtserkennung und -verfolgung
- Anpassung von Pan, Tilt und Zoom basierend auf der Position des Gesichts
- Modularer Aufbau (einfach erweiterbar für andere Tracking-Logiken)

## Dateien
- `http_commands.py` → enthält die Funktionen zur Kommunikation mit der Kamera über HTTP
- `koerperverfolgung.py` → Hauptskript für Gesichtserkennung und Tracking
- `requirements.txt` → listet die benötigten Python-Pakete

## Installation
1. Repository klonen:
   ```bash
   git clone https://github.com/eduardandreica/ptzoptics-face-tracking.git
   cd ptzoptics-face-tracking
