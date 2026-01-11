# cybersecurity_game_full.py
# Single-file Pygame cybersecurity game: 10 enhanced levels, auto-progress, overall win/lose.
# Requires: pygame  (pip install pygame)

import pygame
import sys
import random
import time
import re

# =========================
# Setup
# =========================
pygame.init()
WIDTH, HEIGHT = 1000, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cybersecurity Awareness – Full Game (Enhanced, Auto Progress)")
CLOCK = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (210, 210, 210)
LIGHT_GRAY = (235, 235, 235)
BLUE = (36, 100, 255)
GREEN = (0, 170, 0)
YELLOW = (235, 180, 0)
RED = (220, 0, 0)
ORANGE = (255, 120, 0)
PURPLE = (140, 70, 180)

# Fonts
FONT = pygame.font.SysFont(None, 26)
FONT_SM = pygame.font.SysFont(None, 22)
FONT_LG = pygame.font.SysFont(None, 32)
FONT_XL = pygame.font.SysFont(None, 44)

# =========================
# UI Helpers
# =========================
class Button:
    def __init__(self, rect, text, callback=None, font=FONT, fill=GRAY, text_color=BLACK):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.fill = fill
        self.text_color = text_color
        self.font = font
        self.hover = False

    def draw(self, surf):
        color = LIGHT_GRAY if self.hover else self.fill
        pygame.draw.rect(surf, color, self.rect, border_radius=6)
        pygame.draw.rect(surf, BLACK, self.rect, 2, border_radius=6)
        txt = self.font.render(self.text, True, self.text_color)
        surf.blit(txt, (self.rect.centerx - txt.get_width() // 2,
                        self.rect.centery - txt.get_height() // 2))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

    def update_hover(self, pos):
        self.hover = self.rect.collidepoint(pos)

class Toggle:
    def __init__(self, x, y, w, h, label, initial=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label
        self.value = initial

    def draw(self, surf):
        pygame.draw.rect(surf, LIGHT_GRAY, self.rect, border_radius=12)
        pygame.draw.rect(surf, BLACK, self.rect, 2, border_radius=12)
        knob_w = self.rect.height - 6
        knob_x = self.rect.x + 3 if not self.value else self.rect.right - knob_w - 3
        pygame.draw.rect(surf, GREEN if self.value else GRAY,
                         (knob_x, self.rect.y + 3, knob_w, knob_w), border_radius=8)
        lab = FONT.render(f"{self.label}: {'ON' if self.value else 'OFF'}", True, BLACK)
        surf.blit(lab, (self.rect.right + 10, self.rect.y + (self.rect.height - lab.get_height()) // 2))

    def toggle(self, pos):
        if self.rect.collidepoint(pos):
            self.value = not self.value
            return True
        return False

class InputBox:
    def __init__(self, rect, placeholder="", password=False, maxlen=50, font=FONT):
        self.rect = pygame.Rect(rect)
        self.text = ""
        self.placeholder = placeholder
        self.password = password
        self.maxlen = maxlen
        self.font = font
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                return "enter"
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                if len(self.text) < self.maxlen and event.unicode.isprintable():
                    self.text += event.unicode
        return None

    def value(self):
        return self.text

    def clear(self):
        self.text = ""

    def draw(self, surf):
        pygame.draw.rect(surf, BLUE if self.active else GRAY, self.rect, 2, border_radius=6)
        display_text = ("*" * len(self.text)) if self.password else self.text
        if not display_text and not self.active:
            display_text = self.placeholder
            color = (120,120,120)
        else:
            color = BLACK
        txt = self.font.render(display_text, True, color)
        surf.blit(txt, (self.rect.x + 8, self.rect.y + (self.rect.height - txt.get_height()) // 2))

def draw_text_multiline(surf, text, x, y, font, color=BLACK, max_width=920, line_spacing=6):
    words = text.split(' ')
    lines = []
    cur = ""
    for w in words:
        t = cur + w + " "
        if font.size(t)[0] > max_width:
            lines.append(cur)
            cur = w + " "
        else:
            cur = t
    if cur:
        lines.append(cur)
    yy = y
    for line in lines:
        surf.blit(font.render(line, True, color), (x, yy))
        yy += font.get_height() + line_spacing
    return yy

def wait_for_key_or_click():
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN or ev.type == pygame.MOUSEBUTTONDOWN:
                return
        CLOCK.tick(60)

def show_feedback(title, lines, success=True, back_to_menu=True):
    screen.fill(WHITE)
    screen.blit(FONT_XL.render(title, True, GREEN if success else RED), (60, 60))
    y = 140
    for line in lines:
        y = draw_text_multiline(screen, "• " + line, 60, y, FONT_LG if success else FONT, BLACK) + 4
    if back_to_menu:
        screen.blit(FONT.render("Press any key to continue.", True, (60,60,60)), (60, HEIGHT-60))
    else:
        screen.blit(FONT.render("Press any key to continue.", True, (60,60,60)), (60, HEIGHT-60))
    pygame.display.flip()
    wait_for_key_or_click()

# =========================
# Navigation & Auto-Progress
# =========================
def main_menu():
    title = FONT_XL.render("Cybersecurity Awareness – Enhanced Edition", True, BLUE)
    subtitle = FONT.render("Click where to start; the game will auto-progress through all 10 levels.", True, BLACK)

    buttons = []
    for i in range(10):
        col = (i % 2)
        row = (i // 2)
        index = i + 1
        btn = Button((120 + col*420, 180 + row*55, 360, 45), f"Play from Level {index}", lambda n=index: run_levels_sequence(n))
        buttons.append(btn)

    while True:
        screen.fill(WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 40))
        screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, 90))

        mouse = pygame.mouse.get_pos()
        for b in buttons:
            b.update_hover(mouse)
            b.draw(screen)

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                for b in buttons:
                    if b.is_clicked(ev.pos):
                        b.callback()

        pygame.display.flip()
        CLOCK.tick(60)

def final_summary_screen(passed, total, start_level):
    ratio = passed / total
    if passed == total:
        title = "Flawless Victory!"
        color = GREEN
        tips = ["Perfect run. Your instincts are on point."]
    elif ratio >= 0.8:
        title = "You Win!"
        color = GREEN
        tips = ["Strong performance. Keep practicing to perfect your responses."]
    else:
        title = "Try Again"
        color = ORANGE
        tips = ["Review the feedback from each level.", "Small changes can greatly reduce risk."]
    screen.fill(WHITE)
    screen.blit(FONT_XL.render(title, True, color), (60, 60))
    draw_text_multiline(screen, f"You completed levels {start_level}–10.", 60, 130, FONT_LG, BLACK)
    draw_text_multiline(screen, f"Score: {passed} / {total} levels passed", 60, 170, FONT_LG, BLACK)
    y = 220
    for t in tips:
        y = draw_text_multiline(screen, "• " + t, 60, y, FONT, BLACK) + 4
    screen.blit(FONT.render("Press any key to return to the menu.", True, (60,60,60)), (60, HEIGHT-60))
    pygame.display.flip()
    wait_for_key_or_click()

# Dispatcher to play a sequence of levels automatically and tally results
def run_levels_sequence(start_level):
    level_funcs = {
        1: level_1_phishing,
        2: level_2_roboscam,
        3: level_3_passwords,
        4: level_4_malware,
        5: level_5_social_engineering,
        6: level_6_public_wifi,
        7: level_7_firewall_rules,
        8: level_8_data_privacy,
        9: level_9_2fa,
        10: level_10_ransomware
    }
    passed = 0
    total = 0
    for lvl in range(start_level, 11):
        func = level_funcs.get(lvl)
        if func:
            total += 1
            result = func()
            if result:
                passed += 1
    final_summary_screen(passed, total, start_level)

# =========================
# Level implementations (enhanced)
# Each level returns True (pass) or False (fail)
# =========================

# Level 1 – Phishing (3 sublevels)
def level_1_phishing():
    scenarios = [
        {
            "title": "Bank Email Alert",
            "email": {
                "from": "security@secure-bank-login.com",
                "to": "you@example.com",
                "subject": "URGENT: Suspicious Activity – Verify Now",
                "body": ("Dear Customer,\n\nWe detected suspicious activity. Verify your account immediately to avoid suspension.\n"
                         "Click here: https://secure-bank-login.com/update\n\nSincerely,\nSecurity Team"),
                "redflags": [
                    "Sender domain doesn’t match real bank domain",
                    "Urgent tone to pressure immediate action",
                    "Suspicious link domain",
                ],
            },
            "question": "What’s the safest action?",
            "options": [
                "Click the link and sign in to lock the account quickly.",
                "Open a new browser and visit your bank’s official site manually to check.",
                "Reply to the email asking if it’s legitimate.",
                "Forward the email to friends and ask for advice."
            ],
            "correct": 1,
        },
        {
            "title": "Delivery SMS",
            "sms": "Your package could not be delivered. Reschedule now: http://pack-deliver-status.info/track?id=392817",
            "flags": [
                "Unfamiliar/suspicious link domain",
                "Unexpected package / urgent request",
                "No tracking number tied to your known order",
                "Sender number looks spoofed/odd length",
            ],
            "question": "What are the warning signs? (Select all that apply)",
            "options": [
                "The URL domain is odd and not official.",
                "It’s urgent and unexpected.",
                "No real tracking info or details.",
                "The number looks spoofed.",
            ],
            "correct_set": {0,1,2,3},
        },
        {
            "title": "Internal IT Password Reset",
            "email": {
                "from": "it-support123@gmail.com",
                "to": "you@company.com",
                "subject": "[Action Required] Password Expired – Reset Now",
                "body": ("Dear Employee,\n\nYour password has expired. Reset here: http://company-reset-pass.link\n"
                         "Failure to comply will disable your account.\n\nThanks,\nIT Helpdesk"),
                "redflags": [
                    "Non-company sender address",
                    "Reset link not on official domain",
                    "Threatening language",
                ],
            },
            "question": "How should you verify this request?",
            "options": [
                "Check sender domain and link domain carefully.",
                "Contact IT via official channels (intranet/known phone).",
                "Click the link but be careful.",
                "Ignore all IT emails forever."
            ],
            "correct_set": {0,1},
        },
    ]

    step = 0
    selected_flags = set()
    state = "flags"  # for scenario 1: select red flags first

    def draw_email_box(box, y0=140):
        x0 = 40
        pygame.draw.rect(screen, LIGHT_GRAY, (x0, y0, WIDTH-80, 250), border_radius=8)
        pygame.draw.rect(screen, BLACK, (x0, y0, WIDTH-80, 250), 2, border_radius=8)
        y = y0 + 10
        y = draw_text_multiline(screen, f"From: {box['from']}", x0+10, y, FONT, BLACK)
        y = draw_text_multiline(screen, f"To:   {box['to']}", x0+10, y, FONT, BLACK)
        y = draw_text_multiline(screen, f"Subject: {box['subject']}", x0+10, y, FONT_LG, BLUE)
        y += 10
        y = draw_text_multiline(screen, box["body"], x0+10, y, FONT, BLACK)

    while True:
        screen.fill(WHITE)
        sc = scenarios[step]
        title = FONT_XL.render(f"Level 1 – Phishing: {sc['title']}", True, BLUE)
        screen.blit(title, (40, 40))

        buttons = []

        if step == 0:
            # Email with red flags first
            if state == "flags":
                draw_email_box(sc["email"])
                y = 410
                screen.blit(FONT.render("Select ALL red flags you notice, then press ENTER:", True, BLACK), (40, y))
                y += 10
                for i, f in enumerate(sc["email"]["redflags"]):
                    rect = pygame.Rect(60, y + i*40, WIDTH-120, 36)
                    color = (160, 235, 160) if i in selected_flags else GRAY
                    pygame.draw.rect(screen, color, rect, border_radius=6)
                    pygame.draw.rect(screen, BLACK, rect, 2, border_radius=6)
                    screen.blit(FONT.render(f"{i+1}. {f}", True, BLACK),
                                (rect.x + 10, rect.y + 7))
                    buttons.append(("flag", i, rect))
            elif state == "action":
                draw_email_box(sc["email"])
                y = 410
                screen.blit(FONT.render(sc["question"], True, BLACK), (40, y))
                for i, opt in enumerate(sc["options"]):
                    rect = pygame.Rect(60, y + 40 + i*45, WIDTH-120, 36)
                    pygame.draw.rect(screen, GRAY, rect, border_radius=6)
                    pygame.draw.rect(screen, BLACK, rect, 2, border_radius=6)
                    screen.blit(FONT.render(opt, True, BLACK),
                                (rect.x + 10, rect.y + 7))
                    buttons.append(("choice", i, rect))
        elif step == 1:
            sms_box_y = 140
            pygame.draw.rect(screen, LIGHT_GRAY, (40, sms_box_y, WIDTH-80, 120), border_radius=8)
            pygame.draw.rect(screen, BLACK, (40, sms_box_y, WIDTH-80, 120), 2, border_radius=8)
            draw_text_multiline(screen, "SMS:", 60, sms_box_y+10, FONT_LG, BLUE)
            draw_text_multiline(screen, sc["sms"], 60, sms_box_y+50, FONT, BLACK)

            y = 290
            screen.blit(FONT.render(sc["question"], True, BLACK), (40, y))
            for i, opt in enumerate(sc["options"]):
                rect = pygame.Rect(60, y + 40 + i*45, WIDTH-120, 36)
                color = (160, 235, 160) if i in selected_flags else GRAY
                pygame.draw.rect(screen, color, rect, border_radius=6)
                pygame.draw.rect(screen, BLACK, rect, 2, border_radius=6)
                screen.blit(FONT.render(opt, True, BLACK),
                            (rect.x + 10, rect.y + 7))
                buttons.append(("flag", i, rect))
            screen.blit(FONT_SM.render("Press ENTER to submit your selections.", True, BLACK), (40, HEIGHT-50))
        else:
            draw_email_box(sc["email"])
            y = 410
            screen.blit(FONT.render(sc["question"], True, BLACK), (40, y))
            for i, opt in enumerate(sc["options"]):
                rect = pygame.Rect(60, y + 40 + i*45, WIDTH-120, 36)
                color = (160, 235, 160) if i in selected_flags else GRAY
                pygame.draw.rect(screen, color, rect, border_radius=6)
                pygame.draw.rect(screen, BLACK, rect, 2, border_radius=6)
                screen.blit(FONT.render(opt, True, BLACK),
                            (rect.x + 10, rect.y + 7))
                buttons.append(("flag", i, rect))
            screen.blit(FONT_SM.render("Press ENTER to submit your selections.", True, BLACK), (40, HEIGHT-50))

        pygame.display.flip()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                pos = ev.pos
                for kind, idx, rect in buttons:
                    if rect.collidepoint(pos):
                        if kind == "flag":
                            if idx in selected_flags:
                                selected_flags.remove(idx)
                            else:
                                selected_flags.add(idx)
                        elif kind == "choice":
                            final_choice = idx
                            if final_choice == sc["correct"]:
                                show_feedback("Correct!", ["Open a new tab and go to the official site yourself."], True, back_to_menu=False)
                                step += 1
                                selected_flags.clear()
                                state = "flags"
                                if step >= len(scenarios):
                                    show_feedback("Level 1 Completed!", ["You identified red flags and chose safe actions."], True)
                                    return True
                            else:
                                show_feedback("Not quite.", ["Never click suspicious links or reply. Verify independently."], False, back_to_menu=False)
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_RETURN:
                    if step == 0 and state == "flags":
                        if selected_flags == {0,1,2}:
                            state = "action"
                        else:
                            show_feedback("Missing flags", ["Select all red flags you spot in the email."], False, back_to_menu=False)
                    elif step == 1:
                        if selected_flags == scenarios[1]["correct_set"]:
                            show_feedback("Good eye!", ["Those are classic smishing signs."], True, back_to_menu=False)
                            step += 1
                            selected_flags.clear()
                        else:
                            show_feedback("Not all correct.", ["Review URL, urgency, details, and sender number."], False, back_to_menu=False)
                    elif step == 2:
                        if selected_flags == scenarios[2]["correct_set"]:
                            show_feedback("Exactly.", ["Verify using official IT channels; never use unknown links."], True, back_to_menu=False)
                            show_feedback("Level 1 Completed!", ["Great job dealing with phishing via email, SMS, and internal spoofing."], True)
                            return True
                        else:
                            show_feedback("Close, but not quite.", ["Pick the official verification steps only."], False, back_to_menu=False)
        CLOCK.tick(60)

# Level 2 – Robo-Scamming (detective MCQ)
def level_2_roboscam():
    stage = 0
    score = 0
    stages = [
        {
            "caller": "IRS Agent (alleged)",
            "line": "This is the IRS. You owe back taxes. If you don’t pay immediately, police will arrest you today.",
            "options": [
                ("Ask for written notice mailed to your address on file.", True),
                ("Ask where to buy gift cards to pay now.", False),
                ("Provide your SSN to confirm identity.", False),
                ("Hang up instantly without reporting.", False),
            ],
            "hint": "Government agencies don’t demand immediate payment or threaten arrest over the phone."
        },
        {
            "caller": "IRS Agent",
            "line": "We can settle this if you buy $2,000 in gift cards and read me the codes.",
            "options": [
                ("Explain that government never asks for gift cards; request agent badge and callback number.", True),
                ("Agree to buy the cards to avoid arrest.", False),
                ("Offer credit card number over the phone instead.", False),
                ("Ask to pay via crypto; it’s faster.", False),
            ],
            "hint": "Gift cards/crypto requests are classic red flags."
        },
        {
            "caller": "IRS Agent",
            "line": "I don’t have time for that. Just give me your bank login details and we’ll fix it.",
            "options": [
                ("Refuse, end call, and report to official IRS and your IT/security.", True),
                ("Give online banking credentials to resolve quickly.", False),
                ("Send a picture of your debit card front/back.", False),
                ("Ask for their personal number to text them later.", False),
            ],
            "hint": "Never share credentials. Verify via official published channels."
        },
    ]

    def draw_stage(s):
        screen.fill(WHITE)
        title = FONT_XL.render("Level 2 – Robo-Scamming Detective", True, BLUE)
        screen.blit(title, (40, 40))
        y = draw_text_multiline(screen, f"Caller: {stages[s]['caller']}", 40, 120, FONT_LG, BLACK)
        y = draw_text_multiline(screen, stages[s]["line"], 40, y + 10, FONT, BLACK)
        draw_text_multiline(screen, "Choose the safest response:", 40, y + 16, FONT, BLACK)
        buttons = []
        oy = y + 52
        for i, (opt, _) in enumerate(stages[s]["options"]):
            rect = pygame.Rect(60, oy + i*48, WIDTH-120, 40)
            pygame.draw.rect(screen, GRAY, rect, border_radius=6)
            pygame.draw.rect(screen, BLACK, rect, 2, border_radius=6)
            screen.blit(FONT.render(opt, True, BLACK), (rect.x+10, rect.y+8))
            buttons.append((rect, i))
        screen.blit(FONT_SM.render("Tip: " + stages[s]["hint"], True, (80,80,80)), (60, HEIGHT-50))
        pygame.display.flip()
        return buttons

    while stage < len(stages):
        buttons = draw_stage(stage)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                for rect, i in buttons:
                    if rect.collidepoint(ev.pos):
                        chosen, good = stages[stage]["options"][i]
                        if good:
                            score += 1
                            show_feedback("Good move.", ["That’s the safe, verifiable step."], True, back_to_menu=False)
                        else:
                            show_feedback("Risky choice.", ["This is what scammers want—avoid providing info or payments."], False, back_to_menu=False)
                        stage += 1
        CLOCK.tick(60)

    lines = [f"Score: {score} / {len(stages)}", "Report suspicious calls to official channels.", "Never pay via gift cards or share credentials."]
    success = (score == len(stages))
    show_feedback("Call Ended – Summary", lines, success=success)
    return success

# Level 3 – Password Security (create a strong password)
def level_3_passwords():
    rules = [
        "≥ 12 characters",
        "≥ 1 uppercase letter",
        "≥ 1 lowercase letter",
        "≥ 1 digit",
        "≥ 1 special (!@#$%)",
        "No common words or sequences (password, 123456, qwerty, abc123)",
    ]
    input_box = InputBox((80, 360, 840, 48), placeholder="Type a strong password and press ENTER", password=False, maxlen=50, font=FONT_LG)

    def check_password(pw):
        msgs = []
        if len(pw) < 12: msgs.append("Must be at least 12 characters.")
        if not re.search(r'[A-Z]', pw): msgs.append("Add at least one uppercase letter.")
        if not re.search(r'[a-z]', pw): msgs.append("Add at least one lowercase letter.")
        if not re.search(r'[0-9]', pw): msgs.append("Add at least one digit.")
        if not re.search(r'[!@#$%]', pw): msgs.append("Add at least one special (!@#$%).")
        for c in ["password", "123456", "qwerty", "abc123"]:
            if c in pw.lower():
                msgs.append("Avoid common words/sequences.")
                break
        return msgs

    while True:
        screen.fill(WHITE)
        screen.blit(FONT_XL.render("Level 3 – Create a Strong Password", True, BLUE), (60, 40))
        y = draw_text_multiline(screen, "Follow these rules:", 60, 110, FONT_LG, BLACK)
        for r in rules:
            y = draw_text_multiline(screen, "• " + r, 80, y+4, FONT, BLACK)

        input_box.draw(screen)
        draw_text_multiline(screen, "Press ENTER to evaluate strength.", 80, 520, FONT, BLACK)

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            result = input_box.handle_event(ev)
            if result == "enter":
                pw = input_box.value()
                msgs = check_password(pw)
                if msgs:
                    show_feedback("Password Needs Work", msgs, success=False, back_to_menu=False)
                else:
                    show_feedback("Great Password!", ["You met all strength criteria."], success=True)
                    return True

        # live strength meter
        pw = input_box.value()
        msgs = check_password(pw)
        score = 5 - len([m for m in msgs if m])
        score = max(0, score)
        x, y_m, w, h = 80, 430, 840, 20
        pygame.draw.rect(screen, GRAY, (x,y_m,w,h), border_radius=6)
        fill_w = int((score/5.0) * w)
        color = RED if score <= 2 else ORANGE if score == 3 else GREEN
        pygame.draw.rect(screen, color, (x,y_m,fill_w,h), border_radius=6)

        pygame.display.flip()
        CLOCK.tick(60)

# Level 4 – Malware (choose safe downloads)
def level_4_malware():
    scenarios = [
        {
            "title": "Find a Safe PDF Editor",
            "desc": ("You searched for a PDF editor. Choose the safest download."),
            "links": [
                ("pdf-editor-pro-ultimate-2025.exe", "Ad – Unknown site – HTTPS", False),
                ("Adobe Acrobat (adobe.com)", "Official vendor – HTTPS – Known reputation", True),
                ("PDFEditPlusSetup.msi", "Third-party mirror – no reputation info", False),
                ("AcrobatCrackFree.zip", "Pirated – likely malware", False),
            ],
            "multi_ok": False
        },
        {
            "title": "Forum Game Download",
            "desc": ("A forum post links a 'free game'. Comments mention pop-ups."),
            "links": [
                ("GameInstallerFree.exe", "Direct EXE from unknown file host", False),
                ("Official store page", "Trusted store, signed installer", True),
                ("GameInstallerFree.scr", "Screensaver format used as malware", False),
                ("Read community reviews first", "Research legitimacy before download", True),
            ],
            "multi_ok": True,
            "correct_set": {1,3}
        },
        {
            "title": "Email Attachment",
            "desc": ("Unknown sender attached 'TaxRefund.docm'. AV flags it."),
            "links": [
                ("Open attachment anyway", "Risky", False),
                ("Delete the file", "Safe first step", True),
                ("Forward to security team", "Good reporting", True),
                ("Run in sandbox then open", "Safer than opening, but still risky here", False),
            ],
            "multi_ok": True,
            "correct_set": {1,2}
        }
    ]
    idx = 0
    selected = set()
    total_ok = 0

    while idx < len(scenarios):
        sc = scenarios[idx]
        screen.fill(WHITE)
        screen.blit(FONT_XL.render("Level 4 – Malware & Safe Downloads", True, BLUE), (40, 40))
        y = draw_text_multiline(screen, sc["title"], 40, 110, FONT_LG, BLACK)
        y = draw_text_multiline(screen, sc["desc"], 40, y+8, FONT, BLACK)

        btns = []
        base_y = y + 30
        for i, (name, note, _) in enumerate(sc["links"]):
            rect = pygame.Rect(60, base_y + i*60, WIDTH-120, 48)
            color = (160,235,160) if i in selected else GRAY
            pygame.draw.rect(screen, color, rect, border_radius=6)
            pygame.draw.rect(screen, BLACK, rect, 2, border_radius=6)
            screen.blit(FONT.render(name, True, BLACK), (rect.x+10, rect.y+6))
            screen.blit(FONT_SM.render(note, True, (50,50,50)), (rect.x+10, rect.y+26))
            btns.append((rect, i))
        hint = "Select ALL safe choices, then press ENTER." if sc.get("multi_ok") else "Select the ONE safest option, then press ENTER."
        screen.blit(FONT_SM.render(hint, True, BLACK), (60, HEIGHT-50))
        pygame.display.flip()

        correct_now = False
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                for rect, i in btns:
                    if rect.collidepoint(ev.pos):
                        if sc.get("multi_ok"):
                            if i in selected: selected.remove(i)
                            else: selected.add(i)
                        else:
                            selected = {i}
            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_RETURN:
                if sc.get("multi_ok"):
                    if selected == sc["correct_set"]:
                        correct_now = True
                        total_ok += 1
                        show_feedback("Correct!", ["Those were the safe steps."], True, back_to_menu=False)
                        selected.clear(); idx += 1
                    else:
                        show_feedback("Not quite.", ["Pick only the trusted sources and research steps."], False, back_to_menu=False)
                else:
                    correct_index = next(i for i,(n,nn,safe) in enumerate(sc["links"]) if safe)
                    if selected == {correct_index}:
                        correct_now = True
                        total_ok += 1
                        show_feedback("Correct!", ["Official vendor pages are the safest choice."], True, back_to_menu=False)
                        selected.clear(); idx += 1
                    else:
                        show_feedback("Risky choice.", ["Ads/unknown mirrors/pirated files often carry malware."], False, back_to_menu=False)
        CLOCK.tick(60)

    success = (total_ok == len(scenarios))
    show_feedback("Level 4 Completed!", ["You chose safe downloads and avoided malware.", f"Score: {total_ok}/{len(scenarios)}"], success)
    return success

# Level 5 – Social Engineering / Cyberbullying
def level_5_social_engineering():
    chat = [
        ("Unknown", "Hey! We have a bunch of mutual friends. Mind if I ask you something?"),
        ("You",    ["Sure, what's up?", "Sorry, I don't talk to strangers. (Block & Report)"]),
        ("Unknown", "I'm organizing a meetup for classmates. Which school do you go to and what's your number?"),
        ("You",    ["I don't share personal info. (Block & Report)", "It's Lincoln High, my number is 555-12XX"]),
        ("Unknown", "Come on, don't be shy. Also what city do you live in?"),
        ("You",    ["Report user for harassment and block.", "It's Springfield. Also my address is 12 Maple..."]),
    ]
    turn = 0
    safe_count = 0

    while turn < len(chat):
        screen.fill(WHITE)
        screen.blit(FONT_XL.render("Level 5 – Social Engineering / Cyberbullying", True, BLUE), (40, 40))
        y = 120
        for i in range(turn + 1):
            speaker, content = chat[i]
            if speaker == "Unknown":
                y = draw_text_multiline(screen, f"{speaker}: {content}", 60, y, FONT, BLACK, max_width=800) + 8
            else:
                screen.blit(FONT.render("Your reply:", True, BLACK), (60, y)); y += 8
                opts = content
                btns = []
                for k, opt in enumerate(opts):
                    rect = pygame.Rect(80, y+10 + k*48, WIDTH-160, 40)
                    pygame.draw.rect(screen, GRAY, rect, border_radius=6)
                    pygame.draw.rect(screen, BLACK, rect, 2, border_radius=6)
                    screen.blit(FONT.render(opt, True, BLACK), (rect.x+10, rect.y+8))
                    btns.append((rect, k))
                pygame.display.flip()
                choice = None
                choosing = True
                while choosing:
                    for ev in pygame.event.get():
                        if ev.type == pygame.QUIT:
                            pygame.quit(); sys.exit()
                        elif ev.type == pygame.MOUSEBUTTONDOWN:
                            for rect, k in btns:
                                if rect.collidepoint(ev.pos):
                                    choice = k; choosing = False
                    CLOCK.tick(60)
                if choice == 0:
                    safe_count += 1
                    if "Block" in opts[0]:
                        show_feedback("Blocked & Reported", ["You shut down the social engineering attempt."], True)
                        return True
                else:
                    show_feedback("Risky reply", ["Never share personal info with strangers."], False, back_to_menu=False)
            pygame.display.flip()
        turn += 1
        CLOCK.tick(60)

    success = (safe_count >= 2)
    if success:
        show_feedback("Level 5 Completed!", ["Nice! You avoided oversharing and handled harassment."], True)
    else:
        show_feedback("Level 5 Completed (but risky).", ["Be quicker to block/report and avoid personal details."], False)
    return success

# Level 6 – Public Wi-Fi
def level_6_public_wifi():
    vpn_toggle = Toggle(60, 160, 60, 28, "VPN", initial=False)
    https_toggle = Toggle(60, 210, 60, 28, "Force HTTPS", initial=True)
    actions = [
        ("Log into your bank", False),
        ("Read a news site", True),
        ("Send sensitive work email", False),
        ("Use messaging app (no end-to-end encryption)", False),
        ("Use company VPN before checking internal docs", True),
    ]
    selected = set()

    while True:
        screen.fill(WHITE)
        screen.blit(FONT_XL.render("Level 6 – Public Wi-Fi Safety", True, BLUE), (40, 40))
        draw_text_multiline(screen,"You’re on café Wi-Fi. Toggle protections and choose safe actions.",40, 100, FONT, BLACK)
        vpn_toggle.draw(screen); https_toggle.draw(screen)
        y = 270
        btns = []
        for i, (label, _) in enumerate(actions):
            rect = pygame.Rect(60, y + i*52, WIDTH-120, 44)
            color = (160,235,160) if i in selected else GRAY
            pygame.draw.rect(screen, color, rect, border_radius=6)
            pygame.draw.rect(screen, BLACK, rect, 2, border_radius=6)
            screen.blit(FONT.render(label, True, BLACK), (rect.x+10, rect.y+10))
            btns.append((rect, i))
        screen.blit(FONT_SM.render("Click actions to select. Press ENTER to submit.", True, BLACK), (60, HEIGHT-50))
        pygame.display.flip()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                if vpn_toggle.toggle(ev.pos): pass
                elif https_toggle.toggle(ev.pos): pass
                else:
                    for rect, i in btns:
                        if rect.collidepoint(ev.pos):
                            if i in selected: selected.remove(i)
                            else: selected.add(i)
            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_RETURN:
                ok = True
                for i in selected:
                    label, _ = actions[i]
                    if "bank" in label.lower() or "work email" in label.lower() or "internal" in label.lower():
                        if not vpn_toggle.value or not https_toggle.value:
                            ok = False
                if any("messaging" in actions[i][0].lower() for i in selected):
                    ok = False
                if ok and selected:
                    show_feedback("Smart choices!", ["You used protections and avoided sensitive tasks without VPN."], True)
                    return True
                else:
                    show_feedback("Some choices were risky.", ["Enable VPN and avoid sensitive tasks on public Wi-Fi."], False)
                    return False
        CLOCK.tick(60)

# Level 7 – Firewall Rules
def level_7_firewall_rules():
    traffic = [
        ("Inbound RDP from Internet", "Block"),
        ("Inbound HTTP to server", "Allow"),
        ("Outbound DNS from user", "Allow"),
        ("Inbound SMB from Internet", "Block"),
        ("Outbound HTTP/HTTPS from user", "Allow"),
        ("Inbound SSH from Internet", "Block"),
    ]
    choices = ["Allow", "Block"]
    selection = [None]*len(traffic)

    while True:
        screen.fill(WHITE)
        screen.blit(FONT_XL.render("Level 7 – Firewall Configuration", True, BLUE), (40, 40))
        draw_text_multiline(screen, "Set rules to keep users safe while allowing normal web activity.", 40, 100, FONT, BLACK)
        btns = []
        y = 150
        for i, (desc, correct) in enumerate(traffic):
            screen.blit(FONT.render(f"{i+1}. {desc}", True, BLACK), (60, y+i*58))
            for j, c in enumerate(choices):
                rect = pygame.Rect(520 + j*160, y-8 + i*58, 140, 40)
                color = (160,235,160) if selection[i] == c else GRAY
                pygame.draw.rect(screen, color, rect, border_radius=6)
                pygame.draw.rect(screen, BLACK, rect, 2, border_radius=6)
                screen.blit(FONT.render(c, True, BLACK), (rect.x+10, rect.y+8))
                btns.append((rect, i, c))
        screen.blit(FONT_SM.render("Click to choose for each rule. Press ENTER to evaluate.", True, BLACK), (60, HEIGHT-50))
        pygame.display.flip()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                for rect, i, c in btns:
                    if rect.collidepoint(ev.pos):
                        selection[i] = c
            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_RETURN:
                if None in selection:
                    show_feedback("Complete all rules first.", ["Every entry needs Allow or Block."], False, back_to_menu=False)
                else:
                    correct_all = True
                    for i, (_, corr) in enumerate(traffic):
                        if selection[i] != corr:
                            correct_all = False
                            break
                    if correct_all:
                        show_feedback("Firewall configured correctly!", ["You blocked risky inbound services and allowed needed traffic."], True)
                        return True
                    else:
                        show_feedback("Some rules are unsafe.", ["Revise inbound services from Internet (RDP/SSH/SMB should be blocked)."], False, back_to_menu=False)
        CLOCK.tick(60)

# Level 8 – Data Privacy (permissions)
def level_8_data_privacy():
    # Master list of unique daily scenarios
    scenarios = [
        {
            "app": "PhotoShare",
            "desc": "Requests access to your camera, location, and contacts to 'enhance your experience'.",
            "safe": {"Camera"},
            "question": "Which permissions are REASONABLE for this app?"
        },
        {
            "app": "WeatherNow",
            "desc": "Wants access to your exact location, microphone, and storage.",
            "safe": {"Location"},
            "question": "Which permissions make sense for a weather app?"
        },
        {
            "app": "FlashlightPro",
            "desc": "Requests access to your camera, contacts, and location.",
            "safe": set(),
            "question": "Should a flashlight app need any permissions?"
        },
        {
            "app": "MapFinder",
            "desc": "Requests access to your location, storage, and Bluetooth.",
            "safe": {"Location"},
            "question": "Which permissions are appropriate for a map/navigation app?"
        },
        {
            "app": "MusicStream",
            "desc": "Requests access to your microphone, storage, and location.",
            "safe": {"Microphone", "Storage"},
            "question": "Which permissions are reasonable for a music streaming app?"
        },
        {
            "app": "NoteSaver",
            "desc": "Wants access to storage and contacts.",
            "safe": {"Storage"},
            "question": "Which permissions are necessary for a note-taking app?"
        },
        {
            "app": "GameWorld",
            "desc": "Requests camera, microphone, and location for in-game AR features.",
            "safe": {"Camera", "Location"},
            "question": "Which permissions are reasonable for an AR-based game?"
        },
    ]

    # Choose 5 random, unique scenarios for the "5 days"
    daily_tasks = random.sample(scenarios, 5)

    for day, sc in enumerate(daily_tasks, start=1):
        selected = set()
        done = False
        while not done:
            screen.fill(WHITE)
            title = FONT_XL.render(f"Level 8 – Data Privacy: Day {day}/5", True, BLUE)
            screen.blit(title, (40, 40))

            y = draw_text_multiline(screen, f"App: {sc['app']}", 40, 120, FONT_LG)
            y = draw_text_multiline(screen, sc["desc"], 40, y + 10, FONT)
            y = draw_text_multiline(screen, sc["question"], 40, y + 20, FONT)

            options = ["Camera", "Location", "Contacts", "Microphone", "Storage", "Bluetooth"]
            buttons = []
            base_y = y + 40

            for i, opt in enumerate(options):
                rect = pygame.Rect(60, base_y + i * 50, WIDTH - 120, 40)
                color = (160, 235, 160) if opt in selected else GRAY
                pygame.draw.rect(screen, color, rect, border_radius=6)
                pygame.draw.rect(screen, BLACK, rect, 2, border_radius=6)
                screen.blit(FONT.render(opt, True, BLACK), (rect.x + 10, rect.y + 8))
                buttons.append((rect, opt))

            screen.blit(FONT_SM.render("Select reasonable permissions, then press ENTER.", True, BLACK), (60, HEIGHT - 50))
            pygame.display.flip()

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif ev.type == pygame.MOUSEBUTTONDOWN:
                    for rect, opt in buttons:
                        if rect.collidepoint(ev.pos):
                            if opt in selected:
                                selected.remove(opt)
                            else:
                                selected.add(opt)
                elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_RETURN:
                    if selected == sc["safe"]:
                        show_feedback("Good choice!", ["You granted only necessary permissions."], True, back_to_menu=False)
                    else:
                        show_feedback("Not quite.", ["Grant only permissions essential for the app to work."], False, back_to_menu=False)
                    done = True

            CLOCK.tick(60)

    # After 5 days
    show_feedback("Level 8 Completed!", ["You practiced safe data privacy management for 5 days."], True)
    return True

# Level 9 – Two-Factor Authentication (apply it for real)
def level_9_2fa():
    user_box = InputBox((280, 220, 440, 42), placeholder="Username")
    pass_box = InputBox((280, 280, 440, 42), placeholder="Password", password=True)
    message = ""
    stage = 1
    code = None
    code_box = InputBox((360, 350, 280, 42), placeholder="Enter 2FA code", password=False, maxlen=6, font=FONT_LG)
    start_time = None
    time_limit = 30

    while True:
        screen.fill(WHITE)
        screen.blit(FONT_XL.render("Level 9 – Two-Factor Authentication", True, BLUE), (40, 40))

        if stage == 1:
            draw_text_multiline(screen, "Enter username and password, then press ENTER.", 40, 120, FONT, BLACK)
            user_box.draw(screen)
            pass_box.draw(screen)
        else:
            draw_text_multiline(screen, "A 6-digit code is generated in your authenticator app.", 40, 120, FONT, BLACK)
            screen.blit(FONT.render(f"(Simulated code shown here for demo): {code}", True, (100,100,100)), (40, 160))
            elapsed = time.time() - start_time
            left = max(0, int(time_limit - elapsed))
            screen.blit(FONT_LG.render(f"Time left: {left}s", True, RED if left <= 5 else BLACK), (800-160, 120))
            code_box.draw(screen)
            if left == 0:
                show_feedback("Time expired!", ["2FA failed. Try again and enter the code promptly."], False)
                return False

        if message:
            screen.blit(FONT.render(message, True, RED), (280, 430))

        pygame.display.flip()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if stage == 1:
                user_box.handle_event(ev)
                pass_box.handle_event(ev)
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_RETURN:
                    if user_box.value() and pass_box.value():
                        stage = 2
                        message = ""
                        code = str(random.randint(100000, 999999)).zfill(6)
                        start_time = time.time()
                    else:
                        message = "Please enter both fields."
            else:
                res = code_box.handle_event(ev)
                if res == "enter":
                    if code_box.value() == code:
                        show_feedback("2FA Success", ["Logged in with strong protection."], True)
                        return True
                    else:
                        message = "Incorrect code. Try again."
                        code_box.clear()
        CLOCK.tick(60)

# Level 10 – Ransomware (navigate choices)
def level_10_ransomware():
    start = time.time()
    limit = 45  # seconds
    selected = set()
    actions = [
        ("Disconnect from network immediately", True),
        ("Pay the ransom to get files back", False),
        ("Notify IT/security team", True),
        ("Try random decryptor downloaded from unknown site", False),
        ("Restore from clean backups", True),
        ("Ignore it and keep working", False),
    ]
    while True:
        screen.fill(WHITE)
        screen.blit(FONT_XL.render("Level 10 – Ransomware Incident", True, BLUE), (40, 40))

        elapsed = time.time() - start
        left = max(0, int(limit - elapsed))
        pygame.draw.rect(screen, (30,30,30), (60, 110, WIDTH-120, 120), border_radius=8)
        screen.blit(FONT_LG.render("Your files are encrypted. Send 0.5 BTC to address XYZ in 45 minutes.", True, ORANGE), (80, 140))
        screen.blit(FONT_LG.render("Timer:", True, ORANGE), (80, 180))
        screen.blit(FONT_XL.render(f"{left}s", True, RED if left <= 5 else YELLOW), (160, 174))

        y = 260
        btns = []
        for i, (label, _) in enumerate(actions):
            rect = pygame.Rect(60, y + i*54, WIDTH-120, 44)
            color = (160,235,160) if i in selected else GRAY
            pygame.draw.rect(screen, color, rect, border_radius=6)
            pygame.draw.rect(screen, BLACK, rect, 2, border_radius=6)
            screen.blit(FONT.render(label, True, BLACK), (rect.x+10, rect.y+10))
            btns.append((rect, i))
        screen.blit(FONT_SM.render("Select ALL correct steps, then press ENTER.", True, BLACK), (60, HEIGHT-50))
        pygame.display.flip()

        if left == 0:
            show_feedback("Clock ran out.", ["Don’t panic—contain first, report, and restore from clean backups."], False)
            return False

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                for rect, i in btns:
                    if rect.collidepoint(ev.pos):
                        if i in selected: selected.remove(i)
                        else: selected.add(i)
            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_RETURN:
                correct_set = {0,2,4}
                if selected == correct_set:
                    show_feedback("Exactly right.", ["Don’t pay—contain, report, and restore from backups."], True)
                    return True
                else:
                    show_feedback("Some choices were unsafe.", ["Avoid paying, avoid random tools. Contain, report, restore."], False)
                    return False
        CLOCK.tick(60)

# =========================
# Run
# =========================
if __name__ == "__main__":
    main_menu()
