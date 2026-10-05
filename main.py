import threading
import webbrowser
from pathlib import Path

from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window

from upstox_auth import authorization_url, exchange_code
from futures import get_nifty_futures_key
from upstox_adapter import UpstoxFeed, UpstoxError
from nifty_option_engine import DecisionEngine

Window.clearcolor = (0.04, 0.05, 0.08, 1)

class NiftyAIApp(App):
    title = "NIFTY AI Scanner"

    def build(self):
        self.token = ""
        self.futures_key = ""
        self.running = False
        self.current_decision = None

        root = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))

        title = Label(
            text="NIFTY AI SCANNER",
            font_size=dp(22), bold=True,
            size_hint_y=None, height=dp(42)
        )
        root.add_widget(title)

        self.status = Label(
            text="Upstox connect karke scanner start karein",
            size_hint_y=None, height=dp(38)
        )
        root.add_widget(self.status)

        self.form = GridLayout(cols=1, spacing=dp(7), size_hint_y=None)
        self.form.bind(minimum_height=self.form.setter("height"))

        self.client_id = TextInput(
            hint_text="Upstox API Key / Client ID",
            multiline=False, password=False, size_hint_y=None, height=dp(45)
        )
        self.client_secret = TextInput(
            hint_text="Upstox API Secret",
            multiline=False, password=True, size_hint_y=None, height=dp(45)
        )
        self.redirect_uri = TextInput(
            hint_text="Registered Redirect URI",
            multiline=False, size_hint_y=None, height=dp(45)
        )
        self.auth_code = TextInput(
            hint_text="Login ke baad Redirect URL / code yahan paste karein",
            multiline=False, size_hint_y=None, height=dp(45)
        )

        for w in (self.client_id, self.client_secret, self.redirect_uri, self.auth_code):
            self.form.add_widget(w)

        b1 = Button(text="1. Open Upstox Login", size_hint_y=None, height=dp(48))
        b1.bind(on_release=self.open_login)
        self.form.add_widget(b1)

        b2 = Button(text="2. Get Access Token", size_hint_y=None, height=dp(48))
        b2.bind(on_release=self.get_token)
        self.form.add_widget(b2)

        self.scan_btn = Button(
            text="START NIFTY SCANNER",
            size_hint_y=None, height=dp(52)
        )
        self.scan_btn.bind(on_release=self.start_scanner)
        self.form.add_widget(self.scan_btn)

        scroll = ScrollView()
        scroll.add_widget(self.form)
        root.add_widget(scroll)

        self.dashboard = GridLayout(
            cols=2, spacing=dp(6), padding=dp(5),
            size_hint_y=None
        )
        self.dashboard.bind(minimum_height=self.dashboard.setter("height"))

        dash_scroll = ScrollView(size_hint_y=1)
        dash_scroll.add_widget(self.dashboard)
        root.add_widget(dash_scroll)

        self.refresh_dashboard([])
        return root

    def set_status(self, msg):
        self.status.text = msg

    def open_login(self, *_):
        cid = self.client_id.text.strip()
        redir = self.redirect_uri.text.strip()
        if not cid or not redir:
            self.set_status("API Key aur Redirect URI bhariye.")
            return
        url = authorization_url(cid, redir)
        webbrowser.open(url)
        self.set_status("Upstox login browser mein khul gaya. Login ke baad redirect URL copy karein.")

    def get_token(self, *_):
        def work():
            try:
                data = exchange_code(
                    self.auth_code.text.strip(),
                    self.client_id.text.strip(),
                    self.client_secret.text.strip(),
                    self.redirect_uri.text.strip(),
                )
                self.token = data["access_token"]
                Clock.schedule_once(lambda dt: self.set_status("✓ Upstox connected"), 0)
            except Exception as e:
                Clock.schedule_once(lambda dt: self.set_status(f"Token error: {e}"), 0)
        threading.Thread(target=work, daemon=True).start()

    def start_scanner(self, *_):
        if not self.token:
            self.set_status("Pehle Upstox login karke token lein.")
            return
        if self.running:
            return
        self.running = True
        self.set_status("Scanner starting...")
        threading.Thread(target=self.scan_once, daemon=True).start()

    def scan_once(self):
        try:
            if not self.futures_key:
                self.futures_key = get_nifty_futures_key()

            feed = UpstoxFeed(
                self.token,
                futures_key=self.futures_key,
                timeframe_min=5,
                intraday_oi=True,
            )
            expiry = feed.nearest_expiry()
            snapshot = feed.snapshot(expiry)
            decision = DecisionEngine().run(snapshot, max_risk=2000)

            vals = [
                ("STATUS", decision.status),
                ("TREND", decision.trend.trend),
                ("SPOT", f"{decision.spot:,.2f}"),
                ("AI SCORE", f"{decision.score}/10"),
                ("SUPPORT", f"{decision.levels.support:,.0f}"),
                ("RESISTANCE", f"{decision.levels.resistance:,.0f}"),
                ("ENTRY", f"₹{decision.risk.entry_premium:.1f}" if decision.risk.ok else "WAIT"),
                ("SL", f"₹{decision.risk.premium_sl:.1f}" if decision.risk.ok else "—"),
                ("TARGETS", " / ".join(f"₹{x:.0f}" for x in decision.risk.targets) if decision.risk.ok else "—"),
                ("REASON", decision.reason),
            ]
            Clock.schedule_once(lambda dt, v=vals: self.refresh_dashboard(v), 0)
            Clock.schedule_once(lambda dt: self.set_status(f"LIVE • Expiry {expiry} • 5 min"), 0)

        except Exception as e:
            Clock.schedule_once(lambda dt: self.set_status(f"Scanner error: {e}"), 0)
        finally:
            self.running = False

    def refresh_dashboard(self, values):
        self.dashboard.clear_widgets()
        if not values:
            self.dashboard.add_widget(Label(
                text="Dashboard yahan live signal dikhayega.",
                size_hint_y=None, height=dp(45)
            ))
            self.dashboard.add_widget(Label(text=""))
            return
        for k, v in values:
            self.dashboard.add_widget(Label(
                text=str(k), bold=True,
                size_hint_y=None, height=dp(42)
            ))
            self.dashboard.add_widget(Label(
                text=str(v),
                size_hint_y=None, height=dp(42)
            ))

if __name__ == "__main__":
    NiftyAIApp().run()
