# KI_INFO - Vokabeltrainer Projekt

## 1. Was ist dieses Projekt?
Dieses Projekt ist ein Vokabeltrainer, geschrieben in Python (mit wxPython für die grafische Oberfläche). Es legt großen Wert auf Barrierefreiheit (Unterstützung von Screenreadern über `Tolk.dll`) und Sicherheit/Cheat-Schutz für den schulischen Einsatz. Es gibt neben dem regulären Trainingsprogramm auch spezielle Module für Lehrer (zum Erstellen von Tests) und Schüler (zum Absolvieren der Tests mit verschlüsselter Ergebnis-Speicherung).

## 2. Was macht jede Datei in diesem Ordner?
* **main.py**: Die Hauptanwendung. Beinhaltet die Trainings-GUI, Vokabelverwaltung, Import-Logik und Screenreader-Anbindung.
* **Start_Vokabeltrainer.bat**: Windows Batch-Datei zum schnellen Starten der Anwendung.
* **Tolk.dll & nvdaControllerClient64.dll**: Bibliotheken zur Kommunikation mit Screenreadern (für Barrierefreiheit).
* **einstellungen.json**: Verschlüsselte Konfigurationsdatei.
* **patch.py / update.py / update2.py**: Skripte zum Modifizieren von `main.py` (fügen per String-Replace neue UI-Buttons oder Backup-Aufräumlogik hinzu).
* **Vokabeltrainer.spec / main.spec**: PyInstaller-Konfigurationsdateien, um Python-Code in ausführbare `.exe` zu kompilieren.
* **test_*.py** (z.B. `test_vokabel.py`, `test_crypto.py`): Test-Suite für verschiedene Funktionen des Programms.
* **test.*, test_*.txt/json**: Verschiedene Beispieldateien (PDF, CSV, Excel, TXT), die vermutlich in Tests für den Import-Prozess genutzt werden.
* **lehrer_schueler_programme/**: Unterordner für den Schulprüfungs-Modus.
  * **lehrer.py**: GUI für Lehrkräfte, importiert Vokabeln und erstellt Test-Dateien; entschlüsselt und liest Schüler-Ergebnisse aus.
  * **schueler.py**: GUI für Schüler, um die Tests (`vokabeltest.json`) zu bearbeiten und die Ergebnisse verschlüsselt zu speichern.
  * **crypto_helper.py**: Stellt Verschlüsselungsfunktionen für die Schüler-Testergebnisse bereit.
  * **vokabeltest.json**: Eine generierte Testdatei (Vokabeln für eine Prüfung).

## 3. Welche Funktionen gibt es (Grobüberblick)?
* **Vokabel-Training**: Abfrage von Vokabeln aus verschiedenen Sprachen. Das Fragesystem unterscheidet u.A. nach Kategorien ("Vokabel" vs. "Fachwort").
* **Vokabel-Management**: Import von Vokabeln aus verschiedenen Dateiformaten (PDF, XLSX, DOCX, CSV, TXT) sowie Bearbeitung und Löschung.
* **Barrierefreiheit**: Vollständige Audio-Ausgabe der Texte sowie Braille-Unterstützung durch Anbindung an Windows Screenreader (via Tolk).
* **Sicherheit & Anti-Cheat**: Konfigurationseinstellungen werden mit XOR + zlib (Key: "SuperGeheimerKey_42_VokabelTrainer_Schule") ver- und entschlüsselt. Backups und Einstellungsdateien werden versteckt und schreibgeschützt (`ctypes.windll.kernel32`).
* **Prüfungssystem**: Lehrer können Tests erstellen, Schüler diese absolvieren. Die Ergebnisse werden manipulationssicher (verschlüsselt) gespeichert.

## 4. Spezifische Infos für weitere KI-Agenten
* **Sicherheit / Dateiattribute**: Beachte, dass `main.py` intensiv die Windows-API (`ctypes.windll.kernel32.SetFileAttributesW`) nutzt, um Settings (wie `einstellungen.json`) zu verstecken und schreibzuschützen. Dies könnte bei unachtsamen Datei-Operationen zu Permission Errors führen.
* **GUI-Framework**: Das Projekt nutzt `wxPython`. Neue grafische Elemente müssen thread-safe (z.B. via `wx.CallAfter` aus Background-Tasks) in den MainLoop eingebunden werden.
* **Verschlüsselung**: Falls du Einstellungsdateien anpassen musst, nutze die internen Methoden `chiffriere()` und `dechiffriere()` aus `main.py`.
* **String-Replacements**: Die Dateien `patch.py` und `update.py` manipulieren `main.py` mittels simplen Suchen & Ersetzen von Strings. Solche Patches gehen kaputt, wenn der Quellcode in `main.py` anders formatiert oder verändert wurde. Dies ist fehleranfällig.
* **Systemabhängigkeit**: Die Screenreader-Funktion (`Tolk.dll`) ist fest auf Windows-Systeme ausgelegt.
