
```
rtfm/
├── README.md
├── LICENSE
├── STATUS.md                    # Current state, what works/doesn't
├── ROADMAP.md                   # MK2-MK5 goals
├── CONTRIBUTING.md
├── Makefile                     # install, run, test, clean targets
├── requirements.txt
├── pyproject.toml              # proper Python packaging
├── pytest.ini
│
├── config/
│   ├── default.yml             # Sane defaults
│   └── examples/
│       ├── conservative.yml    # 2% risk, tight stops
│       ├── aggressive.yml      # 10% risk, YOLO mode
│       └── scalper.yml         # High frequency settings
│
├── core/
│   ├── __init__.py
│   ├── session.py              # Session class, risk calculations
│   ├── trade.py                # Trade dataclass, TradeResult enum
│   ├── statistics.py           # Stats calculations, expectancy, etc
│   └── risk_engine.py          # Stop-loss logic, position sizing
│
├── interfaces/
│   ├── __init__.py
│   ├── tui/
│   │   ├── __init__.py
│   │   ├── main.py             # TUI entry point
│   │   ├── renderer.py         # Drawing logic
│   │   ├── keybinds.py         # Input handling
│   │   └── themes.py           # Color schemes
│   └── cli/
│       ├── __init__.py
│       └── main.py             # For future CLI commands
│
├── storage/
│   ├── __init__.py
│   ├── sessions/               # SQLite DBs or JSON dumps
│   ├── exports/                # CSV exports
│   └── backups/
│
├── utils/
│   ├── __init__.py
│   ├── config.py               # YAML loading, validation
│   ├── logging.py              # Structured logging
│   └── formatters.py           # Money/percentage formatting
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   │   ├── test_session.py
│   │   ├── test_risk_engine.py
│   │   └── test_statistics.py
│   └── integration/
│       └── test_tui_session.py
│
├── docs/
│   ├── keybinds.md             # Full keybind reference
│   ├── risk_models.md          # Explain Kelly, fixed fractional, etc
│   └── examples/
│       └── sample_session.md
│
└── tools/
    ├── import_trades.py        # Import from CSV
    ├── analyze_session.py      # Post-session analysis
    └── backtest.py             # Future: historical backtesting
```

**Key changes:**
- `core/` houses the business logic (no TUI shit in there)
- `interfaces/tui/` is now properly separated
- `storage/` for when we add persistence
- Proper `utils/` for config/logging
- `tests/` structure ready for actual testing
- `tools/` for auxiliary scripts
- `config/examples/` for different risk profiles

Non monolithic structure later:
- `core/session.py` - Session class
- `core/trade.py` - Trade/TradeResult 
- `core/statistics.py` - Stats calculations
- `interfaces/tui/main.py` - TUI entry point
- `interfaces/tui/renderer.py` - All the drawing logic
- `utils/config.py` - Config loading


