# RTFM - Risk/Trade Flow Manager

```
 ██████╗ ████████╗███████╗███╗   ███╗
 ██╔══██╗╚══██╔══╝██╔════╝████╗ ████║
 ██████╔╝   ██║   █████╗  ██╔████╔██║
 ██╔══██╗   ██║   ██╔══╝  ██║╚██╔╝██║
 ██║  ██║   ██║   ██║     ██║ ╚═╝ ██║
 ╚═╝  ╚═╝   ╚═╝   ╚═╝     ╚═╝     ╚═╝
 Risk/Trade Flow Manager (for Binary Options)
```

**Read The F*cking Manual** - A vim-style TUI for session-based binary options risk management.  
Built from scratch because casino odds deserve proper engineering.

> ⚠️ **STATUS**: Prototype / Proof-of-Concept / Glorified Calculator  
> This is MK1. It barely qualifies as functional. You've been warned.

---

## Vision

Binary options trading is high-frequency, high-risk gambling dressed in a suit. Most traders blow their accounts because they can't do basic math under pressure. RTFM fixes that by:

- **Calculating risk in real-time** so you're not guessing position sizes
- **Enforcing stop-losses** before you revenge-trade your rent money
- **Tracking session stats** to show you're not as good as you think
- **Vim keybinds** because clicking is for normies

This isn't about making you profitable. It's about making you *aware* of how fast you're bleeding.

---

## The Problem

You sit down with $2000. You decide "5% risk per trade" sounds responsible. Then:
- Win 3 in a row → compound gains, balance grows
- Lose 2 back-to-back → tilt sets in, risk calculation goes out the window
- Chase losses with oversized positions
- Account goes to $800 before you realize what happened

**RTFM solves this** by doing the math FOR you and force-stopping your session when you hit predefined risk limits.

---

## Current State (MK1)

What works:
- ✅ Session-based balance tracking
- ✅ Dynamic risk calculation (% of current balance)
- ✅ Win/Loss/Push logging with vim keybinds
- ✅ Real-time stats (win rate, expectancy, ROI, drawdown)
- ✅ Auto stop-loss (% drawdown OR consecutive losses)
- ✅ Undo last trade (because fat fingers)
- ✅ Command mode for config changes mid-session
- ✅ YAML config file support

What doesn't work (yet):
- ❌ Session persistence (no SQLite, everything dies on exit)
- ❌ CSV/JSON export for post-session analysis
- ❌ Trade type differentiation (CALL vs PUT)
- ❌ Multi-session history/comparison
- ❌ Profit lock mechanisms (e.g., pull initial capital after +20%)
- ❌ Custom payout per trade (brokers vary)
- ❌ Hotkeys for batch trade entry
- ❌ Visual charts/graphs (it's a TUI, not Grafana)
- ❌ Any sort of broker API integration
- ❌ Literally any testing

---

## Installation

**Requirements:**
- Python 3.8+
- `pyyaml` for config parsing

```bash
git clone https://github.com/yourusername/rtfm.git
cd rtfm
pip install pyyaml

# Create your config
cp config.example.yml config.yml
# Edit to taste

# Run it
python main.py -c config.yml
```

---

## Configuration

`config.yml`:
```yaml
initial_balance: 2000.0          # Starting capital
risk_percent: 5.0                # Risk per trade (% of current balance)
payout_percent: 80.0             # Broker payout rate (typically 70-90%)
stop_loss_percent: 20.0          # Max drawdown before force-stop
max_consecutive_losses: 5        # Kill switch after N losses in a row
```

---

## Usage

### Keybinds (Normal Mode)

| Key | Action |
|-----|--------|
| `w` | Log a WIN |
| `l` | Log a LOSS |
| `p` | Log a PUSH (refund) |
| `u` | Undo last trade |
| `j` / `k` | Scroll trade history |
| `g` / `G` | Jump to top/bottom of history |
| `:` | Enter command mode |
| `q` | Quit (will warn if session active) |

### Commands (Command Mode)

| Command | Description |
|---------|-------------|
| `:q` | Quit |
| `:w` | Save session (not implemented yet) |
| `:wq` | Save and quit |
| `:reset` | Start new session |
| `:risk <n>` | Change risk % (e.g., `:risk 3`) |
| `:payout <n>` | Set payout % (e.g., `:payout 85`) |
| `:help` | Show quick help |

### Workflow Example

1. Launch RTFM with your config
2. Take a trade on your broker platform
3. Hit `w` for win or `l` for loss in RTFM
4. Watch your risk amount auto-adjust based on new balance
5. RTFM force-stops you when you hit stop-loss or max losses
6. Cry into your keyboard (optional)

---

## Goals (Roadmap)

> **Note**: See `docs/TODO.md` for detailed implementation tasks and `docs/STRUCTURE.md` for architecture decisions.

### Phase 1: Core Foundation (Current)
**Status**: In Progress - Building the skeleton

- [x] Repository structure (`core/`, `interface/`, `storage/`, `infra/`)
- [x] Base config system (`config/std/base.yml`)
- [x] Makefile for common tasks
- [ ] Refactor monolithic `main.py` into proper modules
  - [ ] `core/session.py` - Session management and state
  - [ ] `core/trade.py` - Trade models and enums
  - [ ] `core/statistics.py` - Stats calculations (expectancy, ROI, etc)
  - [ ] `core/risk_engine.py` - Risk calculations and stop-loss logic
  - [ ] `utils/config.py` - Config loading and validation
  - [ ] `utils/logging.py` - Structured logging
- [ ] `interface/tui/` separation
  - [ ] `main.py` - TUI entry point
  - [ ] `renderer.py` - All drawing/display logic
  - [ ] `keybinds.py` - Input handling and command routing
- [ ] Basic unit tests (`tests/unit/`)
- [ ] Docker setup for reproducible environments

### Phase 2: Make It Actually Useful
**Status**: Not Started

- [ ] Session persistence (SQLite in `storage/sessions/`)
- [ ] CSV/JSON export (`storage/exports/`)
- [ ] Session history browser (TUI mode to review past sessions)
- [ ] Trade notes/tags (track which strategy was used)
- [ ] Multiple config profiles (`config/std/*.yml`)
  - [ ] Conservative (2% risk, tight stops)
  - [ ] Aggressive (10% risk, wide stops)
  - [ ] Scalper (high frequency, small positions)
- [ ] CLI tools (`tools/`)
  - [ ] `analyze_session.py` - Post-session analysis
  - [ ] `import_trades.py` - Import from CSV
  - [ ] `export_report.py` - Generate PDF/HTML reports
- [ ] Integration tests
- [ ] Proper error handling and recovery

### Phase 3: Advanced Risk Management
**Status**: Not Started

- [ ] Multiple position sizing algorithms
  - [ ] Fixed fractional (current implementation)
  - [ ] Kelly Criterion
  - [ ] Volatility-adjusted (ATR-based)
  - [ ] Martingale/Anti-Martingale (for the degenerates)
- [ ] Profit lock mechanisms
  - [ ] Auto-pull initial capital after X% gain
  - [ ] Trailing stop-loss
  - [ ] Partial profit taking rules
- [ ] Multi-asset session tracking
  - [ ] Track different pairs/assets separately
  - [ ] Portfolio-level risk calculation
  - [ ] Correlation warnings (don't bet on 5 correlated pairs)
- [ ] Risk scenario simulator
  - [ ] "What if I lose the next 5 trades?"
  - [ ] Monte Carlo simulation for expectancy ranges
- [ ] Configurable stop-loss strategies
  - [ ] Time-based (stop after X hours)
  - [ ] Profit target (stop at +Y%)
  - [ ] Dynamic drawdown (adjust based on win streak)

### Phase 4: Integration & Automation
**Status**: Not Started

- [ ] Broker API connectors (`connectors/apis/`)
  - [ ] Auto-log trades from broker
  - [ ] Real-time balance sync
  - [ ] Position verification
- [ ] Real-time data feeds (`connectors/web/`)
  - [ ] Price data for decision support
  - [ ] Economic calendar integration
- [ ] Notification system
  - [ ] Discord/Telegram webhooks
  - [ ] Email alerts for stop-loss hits
  - [ ] Desktop notifications (libnotify)
- [ ] Web interface (`interface/web/`)
  - [ ] REST API for remote access
  - [ ] Basic dashboard (read-only TUI mirror)
  - [ ] Mobile-friendly view
- [ ] Infrastructure as Code
  - [ ] Docker Compose for full stack
  - [ ] Nginx reverse proxy
  - [ ] Monitoring (Prometheus/Grafana)

### Phase 5: The Dream (Probably Never)
**Status**: Pipe Dream

- [ ] Backtesting engine (`tools/backtest.py`)
  - [ ] Feed historical trades
  - [ ] Test risk strategies against past data
  - [ ] Generate what-if reports
- [ ] ML-based features (probably useless but fun)
  - [ ] Pattern recognition in trade timing
  - [ ] Expectancy prediction based on time-of-day
  - [ ] Tilt detection (warning when behavior deviates)
- [ ] Multi-user mode
  - [ ] Host for your buddies
  - [ ] Shared risk pools
  - [ ] Leaderboards (for shame)
- [ ] Compliance & Audit
  - [ ] Detailed audit logs
  - [ ] Tax report generation
  - [ ] Regulatory compliance exports
- [ ] Plugin system
  - [ ] Custom risk algorithms
  - [ ] Third-party integrations
  - [ ] Strategy modules

---

## Philosophy

This tool operates on a few principles:

1. **You are bad at mental math under pressure** - Let the computer do it
2. **Emotions will wreck you** - Enforce stop-losses automatically
3. **Past performance ≠ future results** - Track stats anyway, learn from pain
4. **KISS** - One Python file, one config, no bullshit dependencies
5. **Build for yourself first** - If it works for you, maybe it'll work for others

---

## Warning / Disclaimer

Binary options are essentially glorified coin flips with a house edge. Most brokers are unregulated offshore entities. You will probably lose money. RTFM won't make you profitable - it just makes your losses more *organized*.

**This software is provided AS-IS with no guarantees.** Don't risk money you can't afford to lose. Don't blame me when you do anyway. Go Learn proper trading and risk management and study price action. Rise above the casino mentality. Create your own edge.

---

## Why "RTFM"?

1. **Risk/Trade Flow Manager** - What it actually does
2. **Read The F*cking Manual** - Classic sysadmin energy
3. **Perfect passive-aggression** - "How do I use this?" "Well, RTFM."

---

## Contributing

This is a personal project built for my own trading workflow. PRs welcome but I'm picky. If you want a feature, fork it and build it yourself - that's the whole point.

**Code style:**
- Keep it simple, stupid
- No unnecessary abstractions
- Comments for non-obvious logic only
- If it needs more than one file, you're overthinking it

---

## License

MIT - Do whatever you want. Just don't sue me when you lose money.

---

## Acknowledgments

Built with:
- Python's `curses` library (TUI rendering)
- `pyyaml` (config parsing)
- Spite (primary motivation)
- Coffee (secondary motivation)

Inspired by every blown trading account and every "just one more trade" moment.

---

**Now go read the f*cking manual and stop losing money.**
