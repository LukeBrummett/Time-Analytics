# Changelog

All notable changes to this project will be documented in this file.

## [Current] - 2025-12-12

### Added
- Interactive web dashboard using Streamlit and Plotly
- Date range filtering with quick presets
- Team and person filtering capabilities
- Multiple analysis views (Team, Individual, Trends, Data Tables)
- CSV export functionality for all data views
- Organized project structure with separate directories
- **Trend normalization options**:
  - Percentage of total (relative team contribution)
  - Moving averages (4-week for monthly, 2-week for weekly)
  - Weekly granularity view
  - Stacked vs. line chart options
- Individual contributor trend analysis with normalization

### Changed
- Reorganized project into logical folder structure:
  - `src/` - Source code
  - `config/` - Configuration files
  - `output/` - Generated reports
  - `scripts/` - Helper scripts
- Updated README to remove temporal language ("NEW", etc.)
- Updated all file paths to match new structure
- **Reframed metrics from "performance" to "enablement support"**:
  - Higher hours = more support needed/received
  - Lower hours = greater independence
  - Added context and interpretation guides throughout dashboard
  - Renamed "Individual Performance" to "Individual Support"
  - Added sorting options for both high and low support needs

### Fixed
- Bug in `get_hours_by_person` method that caused pandas column conflict

## Project Structure

```
Time Analytics/
├── src/                      # Source code
│   ├── time_analytics.py    # Core analytics library
│   ├── interactive_dashboard.py  # Streamlit dashboard
│   └── team_mapper_ui.py    # Team mapping utility
├── config/                   # Configuration files
│   └── team_mapping.json    # Team and category mappings
├── data/                     # Data files
│   └── stt_records_automatic.csv
├── output/                   # Generated reports and exports
├── scripts/                  # Helper scripts
│   └── start_dashboard.bat  # Windows launcher
├── requirements.txt          # Python dependencies
├── README.md                 # Documentation
├── .gitignore               # Git ignore rules
└── CHANGELOG.md             # This file
```
