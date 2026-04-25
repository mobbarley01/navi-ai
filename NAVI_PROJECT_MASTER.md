# NAVI PROJECT MASTER FILE

Last updated: 2026-04-24  
Source: long Claude project session + ChatGPT cleanup handoff + Claude Code session

---

## 1. Project Purpose

Navi is a personal AI companion running on a Raspberry Pi 5.

Navi is not a generic assistant. She has a full written personality: sharp, loyal, direct, warm when the moment earns it, honest, and personal to Rafael. She was built by Rafael and she knows it. She calls him Captain only sparingly.

The goal is for Navi to:

- Think using the Claude API
- Speak using Piper TTS with the Cori voice
- Remember conversations and facts permanently using SQLite
- Use live tools: weather, news, Wikipedia, Tavily search
- Control an animated HTML face on the Pi touchscreen via WebSocket
- Accept voice input from a USB microphone ✓ working
- Run as much as possible directly on the Pi without relying on the laptop

This is not a new project. Do not start over. Do not rewrite files unless explicitly asked.

---

## 2. User Skill Level

Rafael is a beginner/noob with coding. He built this project with Claude step by step.

Rules for future Claude or Claude Code:

- Explain every command in plain language.
- Give exact commands to copy-paste, one step at a time.
- Do not assume knowledge of Git, Python, Linux, systemd, APIs, or terminal errors.
- Before risky changes, explain what will happen in simple words.
- Ask before deleting, moving, renaming, or heavily refactoring files.
- Prefer small safe edits over big rewrites.
- Do not paste huge files back unless necessary.
- If something fails, explain the error like talking to someone new to coding.
- Never do two risky things at once.
- Isolate bugs with tests before proposing edits.
- Prove the bug location before changing code.
- Always make a backup before editing important files.
- Use commands Rafael can copy-paste.
- Keep a short living project map as work continues.
- When chat gets long, update this master file so context is not lost.

---

## 3. Hardware

Current hardware:

- Raspberry Pi 5, 8GB RAM
- 10.1 inch 1024x600 IPS LAFVIN touchscreen, plugged directly into the Pi
- Windows laptop used to SSH into the Pi
- USB microphone: Amazon Basics Mini USB Condenser Microphone, cardioid pickup, plug-and-play USB

Microphone status:

- The USB microphone has physically arrived.
- It is not installed, tested, or integrated yet.
- Do not assume speech input works.
- First microphone step should be hardware detection and recording test.
- Do not rewrite the whole brain for microphone support.

---

## 4. Project Folder and Access

Project lives on the Pi at:

/home/pi/navi

Python virtual environment:

/home/pi/navi/venv

Activate virtual environment:

source ~/navi/venv/bin/activate

SSH from Windows laptop:

ssh pi@192.168.1.22

Go to project folder:

cd ~/navi

Run Navi brain manually, current safe method:

cd ~/navi
source venv/bin/activate
python navi.py

Edit brain:

nano ~/navi/navi.py

Edit tools:

nano ~/navi/tools.py

Shutdown Pi:

sudo shutdown now

Reboot Pi:

sudo reboot

---

## 5. Known File Tree

Known important files and folders:

/home/pi/navi/
├── navi.py
├── tools.py
├── navi_face_1.html
├── navi_server_example.py
├── navi_memory.db
├── navi.log
├── .env
├── voice/
│   ├── en_GB-cori-medium.onnx
│   └── en_GB-cori-medium.onnx.json
├── backups_known_good/
│   ├── navi.py.working_2026-04-19
│   ├── navi_server_example.py.working_2026-04-19
│   └── navi_face_1.html.working_2026-04-19
├── navi.py.backup_before_body_section
├── navi.py.backup_before_shutdown_fix
├── navi.py.backup_before_face_wait
└── navi.py.backup_before_speak_refactor

File meanings:

- `navi.py` = main AI brain: Claude API, personality, memory, tools, face control, voice output
- `tools.py` = data tools: weather, news, Wikipedia, Tavily, formatting helpers
- `navi_face_1.html` = HTML canvas face animation, runs in Chromium kiosk
- `navi_server_example.py` = WebSocket bridge server, connects brain and browser face
- `navi_memory.db` = SQLite memory database, local only, do not upload
- `navi.log` = local log file, do not upload
- `.env` = API keys, local only, never print, never upload, never commit
- `voice/en_GB-cori-medium.onnx` = Piper Cori voice model, local only, too large for normal GitHub
- `voice/en_GB-cori-medium.onnx.json` = Piper voice model config, small and safe to track
- `backups_known_good/` = known-good backups from before

Systemd service files created in the old Claude session:

/etc/systemd/system/navi-server.service
~/.config/systemd/user/navi-brain.service

Autostart file created:

~/.config/autostart/navi-face.desktop

Service meanings:

- `navi-server.service` = system service that runs the WebSocket face server on boot
- `navi-brain.service` = user service for brain autostart, currently disabled because of audio bug
- `navi-face.desktop` = starts Chromium kiosk face on desktop login

---

## 6. Current Architecture

Navi should be understood in layers.

### 6.1 Brain Layer

Mostly `navi.py`.

Responsible for:

- Claude API calls
- Full personality prompt
- Conversation loop
- Memory read/write
- Context building
- Tool classification
- Deciding what to say
- Deciding when to trigger face moods/actions
- Calling speech output
- Calling face output

Known model in code:

claude-haiku-4-5

### 6.2 Tools Layer

Mostly `tools.py`.

Responsible for:

- Weather via OpenWeatherMap API
- News via NewsAPI
- Wikipedia lookup
- Tavily web search
- Formatting live data for Navi
- Caching results to avoid repeated API calls

Tools should fetch and format data. Tools should not directly control the face or rewrite personality.

### 6.3 Output / Device Layer

Mostly inside `navi.py` plus face files.

Responsible for:

- Piper TTS
- Audio playback through `aplay`
- WebSocket face commands
- HTML face animation
- Future microphone input

Current important output functions:

speak(text, wait_at_end=False)
face(cmd, wait=False)

### 6.4 Face Bridge Layer

Files:

navi_server_example.py
navi_face_1.html

Known behavior:

- WebSocket server runs on `ws://localhost:8765`
- Browser face connects to the WebSocket server
- Brain also sends commands through WebSocket
- Server broadcasts commands to connected clients
- Face reacts to JSON commands

### 6.5 Future Microphone Layer

Not built yet.

Planned flow:

USB microphone → speech-to-text → same user_input flow → navi.py brain → speak() → face()

Do not rewrite the whole brain for microphone support. Prefer a small separate module later, such as:

speech_to_text.py

---

## 7. Current Data Flow

Current typed-input flow:

Rafael types
→ navi.py brain
→ Claude API
→ optional tools.py calls
→ SQLite memory read/write
→ Navi response text
→ speak()
→ Piper TTS
→ aplay
→ speakers / HDMI audio
→ face()
→ WebSocket server
→ browser
→ navi_face_1.html animation

Future voice-input flow:

Rafael speaks
→ USB microphone
→ speech-to-text
→ same user_input flow as typed input
→ Claude brain
→ Piper speech
→ face animation

---

## 8. Current Working Features

Verified or known working as of 2026-04-24:

- Claude brain in `navi.py`
- Full Navi personality prompt
- Persistent SQLite memory
- Facts table
- Conversation history table
- Weather tool
- News tool
- Wikipedia tool
- Tavily web search
- Smart tool classification
- Context caching
- Piper TTS with Cori voice
- Chunked TTS output to avoid cutoffs/gaps
- `normalise_for_speech()` function exists
- HTML face animation in Chromium kiosk
- WebSocket face server broadcasting to clients
- Brain to server to face pipeline was working end-to-end in testing
- `navi-server.service` starts WebSocket server on boot
- `navi-face.desktop` starts Chromium kiosk face on desktop login
- Embodiment section was added to Navi personality
- Ctrl+C graceful shutdown was fixed
- `quit` command graceful shutdown was fixed
- Audio/face desync was improved
- `speak()` owns face sync internally
- `face()` has `wait=True` option for important shutdown messages
- USB microphone hardware tested and working (Amazon Basics USB, card 2)
- `speech_to_text.py` created and tested — mic → Whisper → clean text
- Continuous voice mode added to `navi.py`
- `voice` command turns voice mode ON — listens every turn automatically
- `keyboard` command turns voice mode OFF — returns to typed input
- Whisper forced to English, fp16=False, temperature=0, no previous context
- Garbage filtering rejects Cyrillic, empty, and repeated-nonsense transcripts
- Navy/Neville/Navvy corrected to Navi in transcripts
- Voice exit phrases handled before Claude sees them: "keyboard", "stop voice mode", "switch to keyboard"

---

## 9. Unfinished, Broken, or Uncertain Features

### 9.1 Brain Autostart Audio Bug

`navi-brain.service` was created but disabled.

Problem:

- Navi brain can start through systemd/tmux
- Navi responds
- Face reacts
- But audio does not play when launched via systemd

Likely cause:

PipeWire / PulseAudio / systemd user session audio environment issue

Known environment detail:

XDG_RUNTIME_DIR=/run/user/1000

But this did not fully solve audio.

Current safe workaround:

cd ~/navi
source venv/bin/activate
python navi.py

Do not re-enable brain autostart casually. It needs a focused debugging session.

### 9.2 USB Microphone

Status:

- Physically received and plugged in
- Hardware detection confirmed via `lsusb` and `arecord -l`
- Recording and playback tested and working
- `speech_to_text.py` created and integrated into `navi.py`
- Continuous voice mode working as of 2026-04-24

### 9.3 Schedule Context Too Frequent

Navi mentions Rafael's shift schedule more often than feels natural.

The `SCHEDULE_AWARENESS` section in `SYSTEM_PROMPT` says to reference it "only when genuinely relevant" but it still surfaces too often.

Future fix: tighten the instruction or reduce the schedule detail in `get_time_context()`.

Not urgent. Polish task.

### 9.4 Text-before-audio Gap

Text may print in terminal several seconds before audio starts because Piper synthesis takes time on the Pi.

Known polish issue, not blocking.

### 9.5 Bracketed Paste in tmux

Pasting into tmux may show markers like:

^[[201~

Cosmetic issue.

Possible future fix:

set -g bracket-paste off

in:

~/.tmux.conf

### 9.6 Animation Slower on Pi

HTML face may be less fluid on the Pi than on a laptop.

Possible causes:

- canvas rendering load
- particle count
- Chromium performance
- Pi CPU/GPU load

Not diagnosed yet.

### 9.7 Navi Flies Off Screen

Animation bug: Navi sometimes drifts off edge and disappears.

Likely movement clamping bug in `navi_face_1.html`.

Not investigated yet.

### 9.8 Deprecated WebSocket API Warning

`navi_server_example.py` may use a deprecated websockets API such as:

WebSocketServerProtocol is deprecated

It works for now. Not urgent unless library update breaks it.

### 9.9 Level 2 Embodiment Not Built

Current state:

- Navi knows she has a body and face
- But she does not yet autonomously choose face events/moods/behaviors through Claude tool use

Future idea:

- Add a `control_face` Claude tool
- Let Navi choose moods/events/behaviors
- Handle `tool_use` / tool stop reasons in `call_claude()`

This is a bigger change. Do not start casually.

### 9.10 `normalise_for_speech()` Needs Testing

Function exists in `navi.py`.

Uncertain if fully tested for:

- years
- currencies
- percentages
- ranges
- decades

---

## 10. Latest Session State — Where We Stopped

This is the most important handoff section.

### 10.1 Changes From Last Claude Session

Do not revert these unless explicitly asked.

#### 1. Personality / Embodiment Update

`navi.py` `SYSTEM_PROMPT` was updated with a `YOUR BODY:` section.

Navi now knows:

- she has a body / visual presence
- she is a glowing winged fairy-inspired creature, inspired by Zelda's Navi
- she lives visually in a deep-space canvas
- there are planets, a moon, galaxies, cosmic events, and a status bar
- the status bar shows mood, moon phase, and time zones

#### 2. Shutdown Fixes

Ctrl+C and `quit` were improved.

Expected behavior:

- graceful farewell
- face tracks speaking correctly
- no crash traceback on Ctrl+C

#### 3. `auto_extract_facts` Ctrl+C Handling

Fact extraction was wrapped so Ctrl+C during background/late logic does not crash.

#### 4. `face()` Function Update

`face()` gained a wait option:

face(cmd, wait=False)

When `wait=True`, it blocks until the WebSocket message is sent.

Used for important shutdown/speaking-stop messages.

#### 5. `speak()` Refactor

Major refactor:

speak(text, wait_at_end=False)

Key changes:

- first audio chunk is synthesized before `speaking_start`
- fixes 3–5 second desync where face showed speaking while silent
- `speaking_start` fires right before first audio plays
- `speaking_stop` fires after all chunks finish
- `speaking_stop` can use `wait=wait_at_end`
- `speak()` owns face sync internally
- call sites no longer need manual face speaking wrappers
- shutdown paths use:

speak(farewell, wait_at_end=True)

### 10.2 Infrastructure Created

#### WebSocket Server Service

Created:

/etc/systemd/system/navi-server.service

Status from old chat:

- enabled
- working
- starts on boot
- restarts on crash

Manage with:

sudo systemctl status navi-server
sudo systemctl restart navi-server
sudo systemctl stop navi-server

#### Face Autostart

Created:

~/.config/autostart/navi-face.desktop

Status from old chat:

- working
- Chromium kiosk starts on desktop login
- face appears after reboot

#### Brain Autostart Service

Created:

~/.config/systemd/user/navi-brain.service

Status:

- created
- problematic
- disabled recommended
- has audio bug

Recommended commands:

systemctl --user stop navi-brain.service
systemctl --user disable navi-brain.service

#### tmux Installed

tmux installed:

/usr/bin/tmux

Version from old chat:

3.5a

#### Linger Enabled

This command was run:

sudo loginctl enable-linger pi

Leave it enabled.

### 10.3 Current Intended Runtime State

Safe current state:

- Face server starts automatically
- Face browser starts automatically
- Brain starts manually

Manual brain launch:

cd ~/navi
source venv/bin/activate
python navi.py

Do not re-enable `navi-brain.service` until audio/systemd issue is debugged.

### 10.4 Known-Good Backups

Known-good backups:

~/navi/backups_known_good/navi.py.working_2026-04-19
~/navi/backups_known_good/navi_server_example.py.working_2026-04-19
~/navi/backups_known_good/navi_face_1.html.working_2026-04-19

Restore main brain if needed:

cp ~/navi/backups_known_good/navi.py.working_2026-04-19 ~/navi/navi.py

---

## 11. Face Animation / WebSocket Bridge

Face HTML:

/home/pi/navi/navi_face_1.html

Face server:

/home/pi/navi/navi_server_example.py

WebSocket address:

ws://localhost:8765

### 11.1 What Navi Looks Like

Known visual description:

- deep black-blue space background
- two planets
- one planet has an orbiting moon
- quasar / galaxy / cosmic background effects
- Navi is a small glowing winged fairy-inspired creature
- wings flap
- body tilts
- biological movement behaviors
- bottom status bar shows:
  - mood dot
  - status text
  - waveform bars
  - moon phase SVG
  - clocks / uptime / time zones

### 11.2 Seven Moods

Known moods:

idle
listening
speaking
thinking
happy
alert
angry

Known display mapping from old chat:

| Mood | Color | Status text |
|---|---|---|
| idle | blue | STANDBY |
| listening | teal | LISTENING |
| speaking | light blue | SPEAKING |
| thinking | purple | COMPUTING |
| happy | gold | ONLINE |
| alert | orange | ALERT |
| angry | red | WARNING |

### 11.3 Face Commands

Known JSON commands:

{"type": "mood", "value": "idle"}
{"type": "speaking_start"}
{"type": "speaking_stop"}
{"type": "speaking_amplitude", "value": 0.7}
{"type": "behavior", "value": "zoomies"}
{"type": "personality", "value": "exploring"}
{"type": "goto", "x": 0.5, "y": 0.4}
{"type": "point_at", "target": "ice_giant"}
{"type": "point_at", "x": 0.5, "y": 0.3}
{"type": "event", "value": "shooting_star"}
{"type": "flash", "color": [255, 220, 150], "duration": 800}
{"type": "look_at_navi"}
{"type": "state_query"}

### 11.4 Behaviors

zoomies
stillness
glide
shimmer
orbit
perch
drift
patrol
dash
hover
spiral
cross
loop

### 11.5 Personality States

exploring
resting
curious
playful
watchful

### 11.6 Events

shooting_star
satellite
comet
ufo
supernova
kilonova
meteor_shower
gamma_ray_burst
bright_star
galaxy
cosmic_ray
gravity_lens
nebula_pulse

### 11.7 Currently Wired in Brain

Known wiring:

- `thinking` mood before Claude API call
- `speaking_start` and `speaking_stop` inside `speak()`

### 11.8 Not Yet Wired

Not wired or not fully used:

- `happy`
- `alert`
- `angry`
- `speaking_amplitude`
- events
- `goto`
- `point_at`
- behavior changes
- autonomous Claude-controlled face actions

### 11.9 Level 2 Embodiment Future Work

Goal:

Give Navi actual tool-use control of her face.

Possible design:

- Add `control_face` as a Claude tool
- Let Navi choose face commands
- Handle tool calls in `call_claude()`
- Commands should still go through the known WebSocket face API

Do not do this without planning. It is a bigger architecture change.

---

## 12. Voice Output

TTS engine:

Piper

Voice:

Cori, en_GB medium

Voice model path:

/home/pi/navi/voice/en_GB-cori-medium.onnx

Voice config:

/home/pi/navi/voice/en_GB-cori-medium.onnx.json

Playback method:

aplay

Temp audio chunks:

/tmp/navi_chunk_{n}.wav

### 12.1 How Voice Output Works

Known pipeline:

- long responses split into chunks
- first chunk synthesized before `speaking_start`
- while chunk N plays, chunk N+1 synthesizes in background thread
- chunks deleted after playback
- `speaking_stop` sent after all chunks finish

### 12.2 Known Audio Issues

Main issue:

- audio works when brain is launched manually
- audio does not work when brain is launched by `navi-brain.service`

Likely area:

PipeWire / PulseAudio / systemd user service environment

Current safe approach:

cd ~/navi
source venv/bin/activate
python navi.py

Audio output hardware known from old chat:

- two HDMI audio devices
- speakers through touchscreen HDMI
- default device works correctly in manual mode

---

## 13. Microphone — COMPLETE

Status as of 2026-04-24:

- USB mic plugged in and detected (card 2, device 0)
- Recording and playback verified working
- `speech_to_text.py` created at `/home/pi/navi/speech_to_text.py`
- Continuous voice mode integrated into `navi.py`

Microphone model:

Amazon Basics Mini USB Condenser Microphone
Cardioid pickup
Plug-and-play USB
Detected as: C-Media Electronics, Inc. Amazon USB Streaming Mic
Card: 2, Device: 0
arecord device string: plughw:2,0

### 13.1 speech_to_text.py Summary

File: `/home/pi/navi/speech_to_text.py`

Key behavior:

- Records from `plughw:2,0` for 7 seconds
- Transcribes with Whisper base model
- Forced to English, fp16=False, temperature=0
- Garbage filter rejects: empty, Cyrillic, repeated-word nonsense
- Corrects Navy/Neville/Navvy → Navi
- Returns clean text or empty string on failure

### 13.2 Voice Mode in navi.py

Commands:

- `voice` — turns voice mode ON, listens every turn automatically
- `keyboard` — turns voice mode OFF, returns to typed input
- Also exits on: "stop voice mode", "switch to keyboard"

Voice exit commands are intercepted BEFORE Claude sees them.

Actual data flow now:

Rafael speaks
→ USB mic (plughw:2,0)
→ arecord 7 seconds
→ Whisper base model (English, temp=0)
→ garbage filter
→ Navi corrections
→ same user_input pipeline as typed input
→ Claude brain
→ Piper TTS
→ face animation

---

## 14. Environment Variables and Secrets

Environment file:

/home/pi/navi/.env

Known variable names only:

ANTHROPIC_API_KEY
GEMINI_API_KEY
OPENWEATHER_API_KEY
NEWS_API_KEY
TAVILY_API_KEY

Rules:

- never print `.env` contents
- never commit `.env`
- never upload `.env`
- never expose API key values
- if verifying variables, show names only

Safe command to show variable names only:

grep "=" /home/pi/navi/.env | cut -d'=' -f1

Do not run commands that print real key values.

---

## 15. GitHub Backup Status

GitHub repo:

https://github.com/mobbarley01/navi-ai

GitHub username:

mobbarley01

Branch:

main

Remote:

https://github.com/mobbarley01/navi-ai.git

GitHub is the backup/save slot for code.

### 15.1 Git Ignore Rules

`.gitignore` should include:

.env
*.env
navi_memory.db
navi.log
.last_boot
__pycache__/
*.pyc
*.wav
voice/*.onnx

These files should stay local:

- `.env`
- database
- logs
- boot marker
- pycache
- wav test files
- large Piper `.onnx` voice model

Small config file may be tracked:

voice/en_GB-cori-medium.onnx.json

### 15.2 Save Changes to GitHub

Use:

cd ~/navi
git add .
git commit -m "describe what changed"
git push

Plain language:

- `cd ~/navi` = go to Navi folder
- `git add .` = prepare changed files for saving
- `git commit -m "message"` = make a save point with a note
- `git push` = upload save point to GitHub

If Rafael is confused, give one full copy-paste block.

### 15.3 Current GitHub Note

The repo exists and was pushed safely after `.env`, database, logs, wav files, pycache, and the large voice model were removed from Git tracking.

If unsure whether latest changes are pushed, check:

cd ~/navi
git status

Do not assume the latest old-Claude session changes are pushed unless Git confirms working tree is clean and branch is up to date.

---

## 16. Security Notes

Known security history:

- API keys were detected during a blocked GitHub push attempt.
- `.env` was removed from Git tracking and the safe push later succeeded.
- A GitHub token was exposed in chat.
- Anthropic API key was exposed in chat during the long Claude work.
- Rafael may have rotated the Anthropic key, but verify calmly if needed.
- Other free-tier API keys may not have been rotated.

Recommended later:

- rotate GitHub token
- rotate Anthropic API key
- rotate any exposed API keys if possible

Do not panic Rafael. Mention calmly when relevant. Do not block normal work unless required.

---

## 17. Rules for Future Claude / Claude Code

Future Claude should:

- explain like Rafael is a beginner
- inspect files before changing anything
- make small safe edits
- ask before deleting, moving, or renaming files
- not invent files, functions, or behaviors
- not rewrite the whole system unless explicitly asked
- keep a living project map
- avoid token waste
- avoid reading or printing secrets
- backup before editing important files
- prefer safe scripted edits over manual risky edits when possible
- isolate bugs with tests before proposing fixes
- give one step at a time
- wait for confirmation before the next risky step
- after useful changes, remind Rafael to save to GitHub
- do not chase tired debugging spirals at the end of long sessions

---

## 18. Safest Next Steps

Priority order from where the old session stopped.

### Immediate Step 1 — Confirm Brain Autostart Disabled

Run:

systemctl --user stop navi-brain.service
systemctl --user disable navi-brain.service

Then check:

systemctl --user status navi-brain.service

Expected safe state:

inactive / disabled

### Immediate Step 2 — Test Current Runtime

Reboot Pi:

sudo reboot

Expected:

- face server starts automatically
- face browser opens automatically
- face appears on touchscreen

Then manually start brain:

cd ~/navi
source venv/bin/activate
python navi.py

Have a short conversation and verify:

- text response works
- voice plays
- face switches thinking/speaking correctly

### Immediate Step 3 — Check Git Status

Run:

cd ~/navi
git status

If changes are ready and safe, save them:

cd ~/navi
git add .
git commit -m "update Navi project state"
git push

### Option A — Fix Brain Autostart Audio Issue

Focused debugging task.

Known issue:

manual brain launch has audio
systemd brain launch has no audio

Possible first debugging direction:

- inspect `navi-brain.service`
- inspect user service environment
- inspect PipeWire / PulseAudio availability
- test `aplay` from same service context
- temporarily expose real `aplay` error output safely
- do not refactor whole brain for this

### Option B — Fix Animation Issues

Possible tasks:

- fix Navi flying off screen
- diagnose animation slowness on Pi
- check canvas performance
- reduce particle count if needed
- inspect movement clamp logic in `navi_face_1.html`

### Option C — Level 2 Embodiment

Bigger future task:

- add Claude tool for face control
- let Navi choose moods/events/behaviors
- wire `control_face` safely
- handle tool calls in Claude response flow

Do only after current runtime is stable.

### Option D — USB Microphone Integration

Start with hardware test only:

lsusb
arecord -l

Then record test:

arecord -D plughw:X,0 -f cd -t wav -d 5 ~/navi/mic_test.wav
aplay ~/navi/mic_test.wav

Only after the mic records clearly, add speech-to-text.

---

## 19. Future Session Starter Prompt

In future Claude Code sessions, start with:

Read /home/pi/navi/NAVI_PROJECT_MASTER.md first. Then inspect navi.py, tools.py, navi_server_example.py, navi_face_1.html, and .gitignore. Summarize where we are, what is working, what is broken, and the safest next step. Work one step at a time because I am a beginner.

---

## 20. Current Safe Manual Launch

For now, the safest way to run Navi is:

cd ~/navi
source venv/bin/activate
python navi.py

Do not re-enable brain autostart until the audio/systemd issue is debugged.

---

## 21. Session 2026-04-25 — Level 2 Embodiment Shipped

Latest GitHub commit: `44fcc0b` Add embodied face control and joy mood

State changes:

- Level 2 embodiment is working.
- Navi drives her own face via Claude tool-use through `control_face` in `navi.py`.
- `control_face` only calls the existing `face(cmd)` function — no shell, files, db, or services.
- Face tools enabled ONLY for conversation-style `call_claude` calls (main convo, weather, news, search).
  Disabled for classifier, fact extraction, greeting, farewell, briefing — keeps low-token utility calls clean and prevents startup failure.
- Happy mood in `navi_face_1.html` changed from yellow/ONLINE to rose-pink/JOY (`r:255,g:130,b:180`, label `'JOY'`). Spark burst color updated to match.
- After `speak()`, `navi.py` re-applies the last emotional mood Navi chose this turn so happy/alert/angry persist visibly past speech (instead of being wiped by `speaking_stop` → idle).

Tested and verified:

- Celebration prompt → mood=happy + behavior=shimmer/orbit, JOY label visible.
- Danger prompt → mood=alert + behavior=stillness + personality=watchful.
- Neutral factual prompt (Portugal capital) → no face tool call. Correct.
- Face animation remains smooth and stable.
- Voice mode still works.
- Memory, weather, news, wiki, search still work.
- Startup greeting works (no more "Something went wrong").

GitHub push workflow reminder:

If `git push` asks for username/password (token deprecation):

    gh auth status
    gh auth setup-git
    git push

---

End of NAVI_PROJECT_MASTER.md.
