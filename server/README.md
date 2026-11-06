# Aschenpfad – eigener Server (Docker)

Ein kleiner Server ohne Abhängigkeiten. Er liefert das Spiel aus und vermittelt die Mehrspieler-Daten über WebSocket. Damit funktioniert der Mehrspieler in jedem LAN/VLAN, ohne WebRTC, ohne fremde Dienste.

## Starten

Im Repo-Ordner (dort, wo das `Dockerfile` liegt):

```bash
docker compose up -d --build
```

oder ohne Compose:

```bash
docker build -t aschenpfad .
docker run -d --name aschenpfad -p 8080:8080 --restart unless-stopped aschenpfad
```

Ohne Docker geht es auch direkt mit Node.js (ab Version 18):

```bash
# im Repo-Ordner:
GAME_FILE=./index.html node server/server.js
```

## Spielen

1. Auf dem Server-Rechner die IP herausfinden (z. B. `ipconfig` unter Windows, `ip a` unter Linux), z. B. `192.168.1.20`.
2. Beide Spieler öffnen im Browser **http://192.168.1.20:8080**
3. Host: *Mehrspieler → Spiel hosten* → Raum-Code wird angezeigt.
4. Mitspieler: *Mehrspieler → Beitreten* → Code eingeben.

Die Windows-Firewall muss Port 8080 auf dem Server-Rechner erlauben (beim ersten Start fragt Windows meist nach).

## Aktualisieren

Nach einem `git pull` den Container neu bauen: `docker compose up -d --build`.

Status prüfen: `http://<server>:8080/status`
