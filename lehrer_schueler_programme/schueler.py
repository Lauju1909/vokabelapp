import wx
import json
import os
import sys
import crypto_helper
import random
import time
import threading

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import main as vokabel_main

def text_zu_zahl(text):
    text = text.lower().strip()
    mapping = {
        "null": "0", "zero": "0", "eins": "1", "one": "1", "zwei": "2", "two": "2",
        "drei": "3", "three": "3", "vier": "4", "four": "4", "fünf": "5", "five": "5",
        "sechs": "6", "six": "6", "sieben": "7", "seven": "7", "acht": "8", "eight": "8",
        "neun": "9", "nine": "9", "zehn": "10", "ten": "10", "elf": "11", "eleven": "11",
        "zwölf": "12", "twelve": "12", "dreizehn": "13", "thirteen": "13",
        "vierzehn": "14", "fourteen": "14", "fünfzehn": "15", "fifteen": "15",
        "sechzehn": "16", "sixteen": "16", "siebzehn": "17", "seventeen": "17",
        "achtzehn": "18", "eighteen": "18", "neunzehn": "19", "nineteen": "19",
        "zwanzig": "20", "twenty": "20", "dreißig": "30", "thirty": "30",
        "vierzig": "40", "forty": "40", "fünfzig": "50", "fifty": "50",
        "sechzig": "60", "sixty": "60", "siebzig": "70", "seventy": "70",
        "achtzig": "80", "eighty": "80", "neunzig": "90", "ninety": "90",
        "hundert": "100", "einhundert": "100", "hundred": "100", "one hundred": "100"
    }
    return mapping.get(text, None)

def antwort_ist_richtig(eingabe, zielwort):
    e = eingabe.strip().lower()
    z = zielwort.strip().lower()
    if e == z:
        return True
    if e.isdigit():
        ziel_als_zahl = text_zu_zahl(z)
        if ziel_als_zahl == e:
            return True
    return False

class SchuelerFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title="Schüler - Vokabeltest", size=(500, 400))
        self.panel = wx.Panel(self)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.schueler_name = ""
        self.vokabeln = []
        self.aktuelle_frage_index = 0
        self.punkte = 0
        self.alle_antworten = []
        self.warte_auf_naechste = False
        self.antwort_hat_fokus = False
        
        self.ask_name_and_start()
        
    def ask_name_and_start(self):
        dlg = wx.TextEntryDialog(self, "Bitte gib deinen Namen ein:", "Schülername")
        if dlg.ShowModal() == wx.ID_OK:
            self.schueler_name = dlg.GetValue().strip()
            dlg.Destroy()
            
            if not self.schueler_name:
                wx.MessageBox("Name darf nicht leer sein!", "Fehler", wx.OK | wx.ICON_ERROR)
                sys.exit()
                
            self.load_test()
        else:
            dlg.Destroy()
            sys.exit()

    def load_test(self):
        if not os.path.exists("vokabeltest.json"):
            wx.MessageBox("Keine 'vokabeltest.json' gefunden! Bitte lege die Datei in denselben Ordner.", "Fehler", wx.OK | wx.ICON_ERROR)
            sys.exit()
            
        with open("vokabeltest.json", "r", encoding="utf-8") as f:
            self.vokabeln = json.load(f)
            
        if not self.vokabeln:
            wx.MessageBox("Der Test ist leer!", "Fehler", wx.OK | wx.ICON_ERROR)
            sys.exit()
            
        random.shuffle(self.vokabeln)
        
        self.setup_ui()
        self.zeige_naechste_frage()

    def setup_ui(self):
        self.lbl_frage = wx.StaticText(self.panel, label="Frage kommt hier...", style=wx.ALIGN_CENTER_HORIZONTAL)
        font = self.lbl_frage.GetFont()
        font.PointSize += 4
        self.lbl_frage.SetFont(font)
        self.sizer.Add(self.lbl_frage, 0, wx.ALL | wx.EXPAND, 15)
        
        self.txt_antwort = wx.TextCtrl(self.panel, style=wx.TE_PROCESS_ENTER)
        self.txt_antwort.Bind(wx.EVT_TEXT_ENTER, self.on_antwort)
        self.txt_antwort.Bind(wx.EVT_SET_FOCUS, self.on_antwort_focus_set)
        self.txt_antwort.Bind(wx.EVT_KILL_FOCUS, self.on_antwort_focus_kill)
        self.sizer.Add(self.txt_antwort, 0, wx.ALL | wx.EXPAND, 15)
        
        self.lbl_feedback = wx.StaticText(self.panel, label="")
        font_feedback = self.lbl_feedback.GetFont()
        font_feedback.PointSize += 2
        font_feedback = font_feedback.Bold()
        self.lbl_feedback.SetFont(font_feedback)
        self.sizer.Add(self.lbl_feedback, 0, wx.ALL | wx.ALIGN_CENTER, 15)
        
        btn_ok = wx.Button(self.panel, label="Antworten (Enter)")
        btn_ok.Bind(wx.EVT_BUTTON, self.on_antwort)
        self.sizer.Add(btn_ok, 0, wx.ALL | wx.ALIGN_CENTER, 10)
        
        self.panel.SetSizer(self.sizer)
        self.Centre()
        
    def on_antwort_focus_set(self, event):
        self.antwort_hat_fokus = True
        event.Skip()

    def on_antwort_focus_kill(self, event):
        self.antwort_hat_fokus = False
        event.Skip()
        
    def zeige_naechste_frage(self):
        if self.aktuelle_frage_index >= len(self.vokabeln):
            self.test_beenden()
            return
            
        self.warte_auf_naechste = False
        aktuelle_vok = self.vokabeln[self.aktuelle_frage_index]
        
        fremd = aktuelle_vok.get('en', aktuelle_vok.get('es', aktuelle_vok.get('fr', list(aktuelle_vok.values())[0])))
        deu = aktuelle_vok.get('de', list(aktuelle_vok.values())[-1])
        
        # Gemischt abfragen
        if random.randint(0, 1) == 0:
            sprache = vokabel_main.erkenne_sprache(fremd)
            frage_text = f"Wie heißt '{deu}' auf {sprache}?"
            self.aktuelle_loesung = fremd
        else:
            frage_text = f"Wie heißt '{fremd}' auf Deutsch?"
            self.aktuelle_loesung = deu
            
        self.aktuelle_frage_wort = frage_text
        self.lbl_frage.SetLabel(frage_text)
        self.lbl_frage.Wrap(self.GetSize().width - 30)
        
        self.lbl_feedback.SetLabel("")
        self.txt_antwort.SetEditable(True)
        self.txt_antwort.SetValue("")
        self.txt_antwort.SetFocus()
        self.txt_antwort.SetName(frage_text)
        self.panel.Layout()
        
        if vokabel_main._tolk_geladen:
            vokabel_main.sprechen(frage_text)
            vokabel_main.brailen(frage_text)
            
        def frage_halten():
            time.sleep(1.0)
            while not getattr(self, '_hat_antwort_eingegeben', False) and not self.warte_auf_naechste:
                if self.antwort_hat_fokus and vokabel_main._tolk_geladen:
                    wx.CallAfter(vokabel_main.brailen, frage_text)
                time.sleep(0.5)
                
        self._hat_antwort_eingegeben = False
        threading.Thread(target=frage_halten, daemon=True).start()

    def on_antwort(self, event):
        if self.warte_auf_naechste:
            return
            
        antwort = self.txt_antwort.GetValue().strip()
        if not antwort:
            if vokabel_main._tolk_geladen:
                vokabel_main.sprechen("Bitte erst eine Antwort eingeben.")
            return
            
        self._hat_antwort_eingegeben = True
        self.warte_auf_naechste = True
        self.txt_antwort.SetEditable(False)
        
        ist_richtig = antwort_ist_richtig(antwort, self.aktuelle_loesung)
        
        self.alle_antworten.append({
            "gefragt": self.aktuelle_frage_wort,
            "richtig": self.aktuelle_loesung,
            "schueler": antwort,
            "bewertung": "Richtig" if ist_richtig else "Falsch"
        })
        
        if ist_richtig:
            self.punkte += 1
            msg = "Richtig!"
            self.lbl_feedback.SetLabel(msg)
            self.lbl_feedback.SetForegroundColour(wx.Colour(11, 95, 36)) # Erfolg-Farbe
            
            if vokabel_main._tolk_geladen:
                vokabel_main.sprechen(msg)
                vokabel_main.brailen(msg)
                
            def thread_richtig():
                time.sleep(1.5)
                self.aktuelle_frage_index += 1
                wx.CallAfter(self.zeige_naechste_frage)
            threading.Thread(target=thread_richtig, daemon=True).start()
        else:
            msg = f"Falsch! Richtig wäre: {self.aktuelle_loesung}"
            self.lbl_feedback.SetLabel(msg)
            self.lbl_feedback.SetForegroundColour(wx.Colour(139, 0, 0)) # Fehler-Farbe
            
            if vokabel_main._tolk_geladen:
                vokabel_main.sprechen(msg)
                vokabel_main.brailen(msg)
                
            def thread_falsch():
                time.sleep(3.0)
                self.aktuelle_frage_index += 1
                wx.CallAfter(self.zeige_naechste_frage)
            threading.Thread(target=thread_falsch, daemon=True).start()

    def test_beenden(self):
        ergebnisse = {
            "schueler_name": self.schueler_name,
            "punkte": self.punkte,
            "gesamt": len(self.vokabeln),
            "alle_antworten": self.alle_antworten
        }
        
        dateiname = f"vokabeltest_{self.schueler_name}.json"
        crypto_helper.encrypt_results(ergebnisse, dateiname)
        
        prozent = 0
        if len(self.vokabeln) > 0:
            prozent = round((self.punkte / len(self.vokabeln)) * 100)
        
        msg = f"Test beendet!\nDu hast {self.punkte} von {len(self.vokabeln)} Punkten ({prozent}%).\nDie Ergebnisse wurden in '{dateiname}' gespeichert und können nun dem Lehrer gegeben werden."
        if vokabel_main._tolk_geladen:
            vokabel_main.sprechen(msg)
        wx.MessageBox(msg, "Fertig", wx.OK | wx.ICON_INFORMATION)
        sys.exit()

if __name__ == '__main__':
    app = wx.App(False)
    if vokabel_main._tolk:
        vokabel_main._tolk_geladen = vokabel_main._tolk.Tolk_IsLoaded()
        if not vokabel_main._tolk_geladen:
            try:
                vokabel_main._tolk.Tolk_Load()
            except Exception:
                pass
    frame = SchuelerFrame()
    frame.Show()
    app.MainLoop()
