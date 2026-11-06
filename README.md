# Aschenpfad

Ein düsterer 2D-Souls-like im Browser – eine einzige `index.html` (HTML5 Canvas + WebGL-Post-Effekte + WebAudio-Musik), ohne Abhängigkeiten.

**Spielen:** `index.html` im Browser öffnen (am Handy am besten im Vollbild, Controller wird unterstützt).

## Steuerung

| Aktion | Tastatur | Controller (nach Position) |
|---|---|---|
| Laufen | A / D, Pfeiltasten | Stick / Steuerkreuz |
| Springen / Schwimmen | Leertaste, W | untere Taste |
| Rollen | Shift, L | rechte Taste |
| Leichter / schwerer Angriff | J / K, Maus | R / ZR (RB / RT) |
| Blocken / Parieren | C / F | L / ZL (LB / LT) |
| Heiltrank | Q, R | linke Taste |
| Benutzen (Leuchtfeuer, Truhe, Glocke …) | E | obere Taste |
| Waffe wechseln | X | Select / − |
| Menü | Esc | Start / + |

## Mehrspieler (WLAN)

Hauptmenü → *Mehrspieler (WLAN)*. Einer wählt **Spiel hosten** und bekommt einen 6-stelligen Raum-Code, der andere wählt **Beitreten** und gibt ihn ein. Läuft nur im normalen Browser (z. B. über GitHub Pages), nicht in der Claude-App. Koop: gemeinsame Welt des Hosts, Seelen für beide. Duell: am leuchtenden Stein in der Zuflucht.

### Eigener Server (empfohlen im LAN)

`docker compose up -d --build` startet Spiel + Mehrspieler-Server auf Port 8080. Beide öffnen `http://<Server-IP>:8080`. Details: [server/README.md](server/README.md)

## Welten

- **Die Zuflucht** – Hub mit Schmied (Waffen +1…+5) und Händlerin; gereist wird über die Leuchtfeuer
- **Akt I · Der Aschenpfad** – Ruinen, Versunkene Kapelle, Katakomben, Brennende Zitadelle (Gerhart, Morn, Vaelra)
- **Akt II · Der Giftsumpf** – Gift, Sporen, Stege (Grolmok der Moorschlund)
- **Akt II · Der Frostgürtel** – Eis, Kälte, Schneesturm (Isolde, die Gefrorene Königin)
- **Akt III · Die Ertrunkene Stadt Velmor** – Gezeiten, Glocken, Schwimmen, Atem (Tharn, der Ertrunkene König)
- **Akt III · Der Moderwald** – Wurzel-Plattformen, Sporenpilze (Ysra, die Moderhexe & ihr Baumriese)
- **Akt IV · Das Knochenmeer** – Sandwurm, Skelette, die sich wieder zusammensetzen (Der Erste Aschenträger)

Geplant: Himmelsturm (vertikal), Der Abgrund / Die Andere Seite (Finale / NG+).

## Inhalt des Repos

- `index.html` – das komplette Spiel
- `sprite/` – Werkzeuge und Atlas für den Pixel-Art-Helden (aus den Sprite-Sheets des Autors zusammengebaut)
- `waffen/` – Pixel-Art der 13 Waffen (Griff links)
- `sprite/atlas_nosword.png` + `sprite/hand_anchors.json` – Held ohne Waffe und Handpunkte je Pose
- `helden.html` – frühe Entwurfsseite für den Helden

## Versionen

Jede Version ist ein eigener Commit, die Versionsnummer steht am Anfang der Commit-Nachricht. Frühere Stände (v0.1–v0.4) wurden nicht als Datei gesichert und fehlen daher in der Historie.

| Version | Inhalt |
|---|---|
| v0.5 | Akt I komplett, Rüstungen, Hauptmenü mit 3 Speicherplätzen, Post-FX |
| v0.6.3 | Pixel-Art-Held aus den Sprites des Autors |
| v0.6.x | Scrollbare Menüs, sichtbare Stacheln, Seelen gehen beim Tod verloren |
| v0.8 | Hub „Die Zuflucht“, Balance (weniger Ausdauer, stärkere Bosse), Giftsumpf |
| v0.9 | Frostgürtel, Velmor, Moderwald, Knochenmeer, Musik für alle Gebiete |
| v0.9.3 | Controller-Erkennung über alle Slots, Controller-Diagnose, „Zur Zuflucht reisen“ |
| v0.9.6 | Feuer verletzt Gegner und fällt zu Boden, Leuchtfeuer nach Endbossen, Weltentor entfernt, Waffenstufen im Menü, Reisen nach Gebieten gruppiert |
| v0.9.8 | Waffenbilder im Ausrüstungsmenü |
| v0.10 | Held ohne festes Schwert, alle 13 Waffen als Pixel-Art in der Hand und im Menü |
| v0.11 | Mehrspieler im WLAN (WebRTC, Verbindung per Code): Koop durch alle Welten, Duell in der Zuflucht |
| v0.12 | Mehrspieler mit kurzem 6-stelligem Raum-Code (nur der Gast gibt ihn ein) |
| v0.13 | Eigener Mehrspieler-Server als Docker-Container (WebSocket, funktioniert in jedem LAN) |
