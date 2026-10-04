# Bewerbungs-Tracker

Eine kleine Fullstack-Webanwendung zum Verwalten eigener Bewerbungen, mit Benutzerkonten, Statusverwaltung und Statistik.

*A small full-stack web app (Flask, SQLite, vanilla JavaScript) to track job applications.*

![Screenshot](docs/screenshot.png)

## Funktionen

- Registrierung und Login mit gehashten Passwörtern
- Bewerbungen anlegen, anzeigen, Status ändern und löschen
- Filter nach Status und Statistik per SQL `GROUP BY`
- Jeder Nutzer sieht nur seine eigenen Daten

## Technologien

**Backend:** Python, Flask, REST-API mit JSON
**Datenbank:** SQLite mit handgeschriebenem SQL, zwei Tabellen mit Fremdschlüssel
**Frontend:** HTML, CSS, JavaScript ohne Framework (`fetch`)

## Sicherheit

- Gesalzene scrypt-Hashes statt Klartext-Passwörtern
- Parametrisierte SQL-Abfragen gegen SQL-Injection
- Jede Abfrage ist auf den eingeloggten Nutzer beschränkt
- Ausgabe über `textContent` gegen XSS

## Lokal starten

```bash
git clone https://github.com/ElbekkarMohamed/bewerbungs-tracker.git
cd bewerbungs-tracker
python -m venv venv
.\venv\Scripts\Activate.ps1      # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Dann http://127.0.0.1:5000 öffnen. Die Datenbank wird beim ersten Start automatisch angelegt.
