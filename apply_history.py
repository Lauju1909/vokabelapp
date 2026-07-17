import re

with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add HistorieDialog before VokabelFrame
historie_dialog_code = """
class HistorieDialog(wx.Dialog):
    def __init__(self, parent, richtig, falsch, vertipper, historie):
        super().__init__(parent, title="Lern-Historie & Übersicht", size=(650, 450))
        self.SetBackgroundColour(HINTERGRUND)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        lbl_stat = wx.StaticText(self, label=f"Übersicht:\\nRichtig: {richtig}  |  Falsch: {falsch}  |  Vertipper: {vertipper}")
        lbl_stat.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        lbl_stat.SetForegroundColour(VORDERGRUND)
        sizer.Add(lbl_stat, 0, wx.ALL | wx.ALIGN_CENTER, 15)
        
        self.liste = wx.ListCtrl(self, style=wx.LC_REPORT | wx.BORDER_SUNKEN)
        self.liste.InsertColumn(0, "Frage", width=220)
        self.liste.InsertColumn(1, "Deine Eingabe", width=140)
        self.liste.InsertColumn(2, "Korrekte Antwort", width=140)
        self.liste.InsertColumn(3, "Status", width=100)
        
        for i, eintrag in enumerate(historie):
            self.liste.InsertItem(i, eintrag["frage"])
            self.liste.SetItem(i, 1, eintrag["eingabe"])
            self.liste.SetItem(i, 2, eintrag["korrekt"])
            self.liste.SetItem(i, 3, eintrag["status"])
            
            # Farbliche Markierung je nach Status
            if eintrag["status"] == "Richtig":
                self.liste.SetItemBackgroundColour(i, wx.Colour(220, 255, 220))
            elif eintrag["status"] == "Tippfehler":
                self.liste.SetItemBackgroundColour(i, wx.Colour(255, 255, 220))
            else:
                self.liste.SetItemBackgroundColour(i, wx.Colour(255, 220, 220))
                
        sizer.Add(self.liste, 1, wx.ALL | wx.EXPAND, 10)
        
        btn_ok = wx.Button(self, wx.ID_OK, "Schließen")
        btn_ok.SetBackgroundColour(BUTTON_HINTERGRUND)
        btn_ok.SetForegroundColour(BUTTON_VORDERGRUND)
        sizer.Add(btn_ok, 0, wx.ALL | wx.ALIGN_CENTER, 10)
        
        self.SetSizer(sizer)

"""
content = content.replace("class VokabelFrame(wx.Frame):", historie_dialog_code + "class VokabelFrame(wx.Frame):")

# 2. Add variables to VokabelFrame.__init__
old_init = "self.lern_timer.Start(60000) # 1 Minute"
new_init = """self.lern_timer.Start(60000) # 1 Minute
        
        self.session_richtig = 0
        self.session_falsch = 0
        self.session_vertipper = 0
        self.session_historie = []"""
content = content.replace(old_init, new_init)

# 3. Modify on_antwort_enter
# We need to insert the status evaluation logic exactly after match_val = check_equal(...)
old_match = "match_val = check_equal(eingabe, self.korrekte_antwort)"
new_match = """match_val = check_equal(eingabe, self.korrekte_antwort)
        
        if match_val == 1:
            self.session_richtig += 1
            status_text = "Richtig"
        elif match_val == 2:
            self.session_vertipper += 1
            status_text = "Tippfehler"
        else:
            self.session_falsch += 1
            status_text = "Falsch"
            
        self.session_historie.append({
            "frage": self.aktuelle_frage,
            "eingabe": eingabe,
            "korrekt": self.korrekte_antwort,
            "status": status_text
        })"""
content = content.replace(old_match, new_match)

# 4. Modify on_lern_timer
old_timer = 'wx.MessageBox(f"Lernzeit abgelaufen! Du hast {LERN_DAUER_MIN} Minuten gelernt.\\nGute Arbeit!", "Zeit abgelaufen", wx.OK | wx.ICON_INFORMATION)'
new_timer = '''res = wx.MessageBox(f"Lernzeit abgelaufen! Du hast {LERN_DAUER_MIN} Minuten gelernt.\\n\\nMöchtest du dir deine Lern-Historie ansehen?", "Zeit abgelaufen", wx.YES_NO | wx.ICON_INFORMATION)
            if res == wx.YES:
                self.on_historie(None)'''
content = content.replace(old_timer, new_timer)

# 5. Add Menu item and on_historie method
old_menu_end = 'menubar.Append(menu_vokabeln, "Vokabeln")'
new_menu_end = '''menubar.Append(menu_vokabeln, "Vokabeln")
        
        menu_aktionen = wx.Menu()
        item_historie = menu_aktionen.Append(wx.ID_ANY, "Lern-Historie anzeigen...")
        menubar.Append(menu_aktionen, "Aktionen")
        
        self.Bind(wx.EVT_MENU, self.on_historie, item_historie)'''
content = content.replace(old_menu_end, new_menu_end)

new_on_historie = '''    def on_historie(self, event):
        dlg = HistorieDialog(self, self.session_richtig, self.session_falsch, self.session_vertipper, self.session_historie)
        dlg.ShowModal()
        dlg.Destroy()
        
    def _menue_aufbauen'''
content = content.replace("    def _menue_aufbauen", new_on_historie)


with open("main.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Historie logic applied.")
