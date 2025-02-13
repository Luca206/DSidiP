Repository zu dem Kurs "DataScience in der industriellen Produktion" im WS2024/2025.

# Projekt-Struktur
| GitHub-Dir | Beschreibung                                  |
|------------|-----------------------------------------------|
| src        | Source-Code                                   |
| Data       | Informationen, wie Doku oder Zeichnungen o.ä. |

# Docker-Container
1. Docker installieren
2. Dockerfile bauen mit ```docker build [PATH] -t=dsidip``` --> PATH = *"GitHub-Repo Pfad"/src*
3. Container ist nun gebaut. ```Schritt 2``` muss nur erneut ausgeführt werden, wenn etwas an dem Dockerfile geändert wird.
4. Container starten mit ```docker compose up```

# Abhängingkeiten installieren
Installieren mit ```pip install -r requirements.txt```