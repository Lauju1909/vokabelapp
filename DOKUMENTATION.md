# System-Dokumentation: Vokabel-App

Diese Dokumentation erklärt die zwei wichtigsten Sicherheits- und Automatisierungssysteme der Vokabel-App, der Lehrer-App und der Schüler-App.

---

## 1. Das Auto-Update-System

Das Update-System sorgt dafür, dass alle Apps (Vokabeltrainer, Lehrer, Schüler) sich vollautomatisch aktualisieren, ohne dass Administratorrechte (wie z.B. auf Schul-Laptops) benötigt werden.

### Ablauf eines Updates:
1. **Prüfung:** Direkt beim Start der App öffnet sich ein kleiner, unsichtbarer Hintergrundprozess. Dieser verbindet sich mit der offiziellen GitHub-API und prüft den neusten *Release* (Veröffentlichung) unter `Lauju1909/vokabelapp`.
2. **Versions-Vergleich:** Er liest die Version des GitHub-Releases aus (z.B. `1.0.1`) und vergleicht sie mit der fest einprogrammierten Version in der `.exe` (z.B. `APP_VERSION = "1.0.0"`).
3. **Download:** Ist die GitHub-Version neuer, sucht der Updater nach der passenden `.exe`-Datei im Release (er sucht exakt nach dem Namen der App, die gerade läuft, z.B. `lehrer.exe`). Diese wird in einen temporären Ordner deines Computers heruntergeladen.
4. **Der System-Trick (Keine Admin-Rechte!):** 
   Da man unter Windows laufende Programme nicht einfach löschen darf, nutzt die App einen Trick: Sie benennt sich *während sie läuft* kurzerhand selbst um! Aus `vokabeltrainer.exe` wird z.B. `vokabeltrainer.exe.old`. Das erlaubt Windows ohne Passwortabfrage.
5. **Austausch & Neustart:** Die gerade heruntergeladene, neue Datei wird an den Ursprungsort verschoben und heißt nun wieder `vokabeltrainer.exe`. Die App startet die neue Version und beendet sich sofort selbst.
6. **Aufräumen:** Wenn die App beim nächsten Mal startet, erkennt sie die zurückgelassene `.old`-Datei und löscht diese lautlos.

### Sicherheit (Der Token-Schutz):
Der Code für den Updater steht gut lesbar in den Python-Dateien. Um jedoch zu verhindern, dass Hacker oder findige Schüler sensible GitHub-Tokens auslesen können, wurde das Feld für den Token mit ZLIB (Komprimierung) und Base64 (umgedreht) verschlüsselt. So bleibt der Token als völlig unlesbarer Datensalat versteckt.

---

## 2. Das versteckte Backup-System (Anti-Cheat)

Da Vokabeln und Lernfortschritte in einer leicht lesbaren `vokabeln.json` oder `historie.json` gespeichert werden, könnten Schüler theoretisch die Dateien im Texteditor öffnen und sich selbst gute Noten oder weniger Fehler eintragen. Das versteckte Backup-System verhindert das.

### Ablauf des Schutzes:
1. **Das Original:** Die normalen Dateien (wie `vokabeln.json`) liegen offen im Ordner.
2. **Das Geheim-Backup:** Sobald du Vokabeln lernst oder Einstellungen speicherst, erstellt die App im Hintergrund automatisch eine exakte Kopie der Datei (z.B. `vokabeln.json.bak` oder speichert sie tief versteckt im Windows `%TEMP%` Ordner).
3. **Tarnung:** Dieses Backup erhält von Windows den Modus `Versteckt` (Hidden) und `Schreibgeschützt` (Read-Only). Ein normaler Schüler sieht diese Datei nicht einmal, wenn er den Ordner öffnet.
4. **Die Überprüfung:** Jedes Mal, wenn die App startet oder Daten lädt, vergleicht sie heimlich das Original (`vokabeln.json`) mit dem versteckten Backup. 
5. **Manipulation erkannt:** Wenn ein Schüler die sichtbare `vokabeln.json` manipuliert, bemerkt die App sofort, dass der Inhalt nicht mehr mit dem versteckten Backup übereinstimmt.
6. **Die Strafe:** Die App schlägt Alarm ("Manipulation erkannt!") und überschreibt die gefälschte Schüler-Datei rücksichtslos wieder mit den echten, versteckten Backup-Daten. Der Täuschungsversuch wird damit sofort rückgängig gemacht!
