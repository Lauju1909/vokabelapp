import wx
import sys
import os
import json
import crypto_helper

# Parent-Ordner in sys.path einfügen, um main.py zu importieren
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import main as vokabel_main

class LehrerFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title="Lehrer - Vokabeltest Manager", size=(600, 500))
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        lbl_title = wx.StaticText(panel, label="Lehrer: Vokabeltests verwalten")
        font = lbl_title.GetFont()
        font.PointSize += 5
        font = font.Bold()
        lbl_title.SetFont(font)
        sizer.Add(lbl_title, 0, wx.ALL | wx.ALIGN_CENTER, 15)
        
        btn_import = wx.Button(panel, label="Importieren")
        btn_import.Bind(wx.EVT_BUTTON, self.on_create_test)
        sizer.Add(btn_import, 0, wx.ALL | wx.EXPAND, 10)
        
        btn_results = wx.Button(panel, label="2. Schüler-Ergebnisse importieren und ansehen")
        btn_results.Bind(wx.EVT_BUTTON, self.on_view_results)
        sizer.Add(btn_results, 0, wx.ALL | wx.EXPAND, 10)
        
        self.log = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
        font_log = self.log.GetFont()
        font_log.PointSize += 1
        self.log.SetFont(font_log)
        sizer.Add(self.log, 1, wx.ALL | wx.EXPAND, 10)
        
        panel.SetSizer(sizer)
        self.Centre()
        
    def on_create_test(self, event):
        wildcard = "Unterstützte Formate (*.docx;*.xlsx;*.pdf;*.csv;*.txt)|*.docx;*.xlsx;*.pdf;*.csv;*.txt|Alle Dateien (*.*)|*.*"
        with wx.FileDialog(self, "Datei auswählen", wildcard=wildcard, style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            pfad = fileDialog.GetPath()
            
            try:
                neue_vokabeln = vokabel_main.datei_importieren_universal(pfad)
                if neue_vokabeln:
                    with open("vokabeltest.json", "w", encoding="utf-8") as f:
                        json.dump(neue_vokabeln, f, ensure_ascii=False, indent=4)
                    self.log.AppendText(f"Test mit {len(neue_vokabeln)} Vokabeln erstellt: vokabeltest.json\n")
                    wx.MessageBox(f"Erfolgreich! 'vokabeltest.json' mit {len(neue_vokabeln)} Vokabeln generiert.", "Erfolg", wx.OK | wx.ICON_INFORMATION)
                else:
                    wx.MessageBox("Es konnten keine Vokabeln gefunden werden.", "Fehler", wx.OK | wx.ICON_ERROR)
            except Exception as e:
                wx.MessageBox(f"Fehler beim Import: {e}", "Fehler", wx.OK | wx.ICON_ERROR)

    def on_view_results(self, event):
        with wx.FileDialog(self, "Schüler-Ergebnis auswählen", wildcard="JSON Dateien (*.json)|*.json", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            pfad = fileDialog.GetPath()
            
            ergebnisse = crypto_helper.decrypt_results(pfad)
            if ergebnisse:
                name = ergebnisse.get('schueler_name', 'Unbekannt')
                punkte = ergebnisse.get('punkte', 0)
                gesamt = ergebnisse.get('gesamt', 0)
                fehler_anzahl = gesamt - punkte
                alle_antworten = ergebnisse.get('alle_antworten', ergebnisse.get('falsch_beantwortet', [])) # Fallback für alte Tests
                
                prozent = 0
                if gesamt > 0:
                    prozent = round((punkte / gesamt) * 100)
                
                self.log.AppendText(f"\n{'='*50}\n")
                self.log.AppendText(f" ERGEBNIS FÜR: {name.upper()}\n")
                self.log.AppendText(f"{'='*50}\n")
                self.log.AppendText(f"Punkte: {punkte} von {gesamt} ({prozent}%)\n")
                self.log.AppendText(f"Fehler: {fehler_anzahl}\n")
                self.log.AppendText(f"{'-'*50}\n")
                
                if alle_antworten:
                    for i, item in enumerate(alle_antworten, 1):
                        gefragt = item.get('gefragt', '?')
                        richtig = item.get('richtig', '?')
                        schueler = item.get('schueler', '?')
                        
                        bewertung = item.get('bewertung', '')
                        if not bewertung:
                            # Kompatibilität zu alten Dateien
                            bewertung = "Falsch" if schueler.lower() != richtig.lower() else "Richtig"
                            
                        self.log.AppendText(f"Frage {i}: {gefragt}\n")
                        self.log.AppendText(f"  -> Schüler: {schueler} ({bewertung})\n")
                        if bewertung == "Falsch":
                            self.log.AppendText(f"  -> Erwartet: {richtig}\n")
                        self.log.AppendText("\n")
                else:
                    self.log.AppendText("Keine detaillierten Antworten gefunden.\n")
                self.log.AppendText(f"{'='*50}\n")
            else:
                wx.MessageBox("Konnte die Datei nicht entschlüsseln. Ist es wirklich eine Schüler-Ergebnisdatei?", "Fehler", wx.OK | wx.ICON_ERROR)

if __name__ == '__main__':
    app = wx.App(False)
    # Lade Screenreader Support
    if vokabel_main._tolk:
        vokabel_main._tolk_geladen = vokabel_main._tolk.Tolk_IsLoaded()
        if not vokabel_main._tolk_geladen:
            try:
                vokabel_main._tolk.Tolk_Load()
            except Exception:
                pass
    frame = LehrerFrame()
    frame.Show()
    app.MainLoop()
