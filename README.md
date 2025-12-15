# Time Analytics Application

A Python application for analyzing enablement hours by team from time tracking data. Features an interactive web dashboard for exploring data with date range filtering, team comparisons, and individual performance tracking.

## Features

- Load and process time tracking data from CSV
- Map team members to their respective teams
- Filter enablement-related activities
- Interactive web dashboard with real-time filtering
- Generate comprehensive reports including:
  - Total hours by team
  - Total hours by person
  - Monthly and weekly trends
- Export analysis to Excel with multiple sheets
- Create static visualizations (bar charts, trend lines)

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
└── README.md
```

## Installation

Install Python dependencies:

```bash
pip install -r requirements.txt
```

## Quick Start

### Interactive Dashboard

The easiest way to explore your data is with the interactive web dashboard:

**Windows:**
```bash
scripts\start_dashboard.bat
```

**Mac/Linux:**
```bash
python -m streamlit run src/interactive_dashboard.py
```

Then open your browser to **http://localhost:8501**

### Command Line Analysis

Run the analytics script directly:

```bash
python src/time_analytics.py
```

This will:
- Load data from `data/stt_records_automatic.csv`
- Print summary tables to console
- Generate `output/enablement_report.txt`
- Generate `output/enablement_analysis.xlsx`

## Dashboard Features

The interactive dashboard provides:

- **Date Range Selection**: Quick presets (Last 7/30/90 days, This Year, All Time) or custom ranges
- **Team Filtering**: Select specific teams to analyze
- **Person Filtering**: Focus on individual contributors
- **Multiple Views**:
  - **Team Analysis**: Enablement hours and sessions by team
  - **Individual Support**: Sort by most/least support needed, session duration analysis
  - **Trends**: Monthly and weekly trends with multiple normalization options
  - **Data Tables**: Exportable CSV data for further analysis

### Understanding the Metrics

**Important Context**: This application tracks enablement hours, where:
- **Higher hours** = More support/enablement received (learning, troubleshooting, guidance)
- **Lower hours** = Greater independence and self-sufficiency
- **Session duration** = Longer sessions may indicate complex issues or deeper learning needs

Teams or individuals with higher hours aren't "underperforming" - they may be working on new technologies, tackling complex challenges, or actively growing their skills.

### Trend Normalization Options

To handle gaps in logging and identify genuine trends, the dashboard offers:

1. **Absolute Hours**: Raw hour totals per time period
2. **Percentage of Total**: Shows each team's relative contribution, normalizing for overall activity level
3. **Moving Average**: Smooths out variations by averaging across multiple weeks (4-week for monthly, 2-week for weekly)
4. **Weekly Granularity**: View data at weekly resolution with automatic smoothing

These options help you:
- Identify genuine trends vs. noise from irregular logging
- Compare relative team effort over time
- Spot patterns that might be hidden in raw data

All charts are interactive - hover for details, zoom, pan, and more!

## Configuration

### Team Mapping

Edit [config/team_mapping.json](config/team_mapping.json) to map people to their teams:

```json
{
  "teams": {
    "Team Alpha": [
      "Claire Miksch",
      "Caden Caffey"
    ],
    "Team Beta": [
      "Karl Martenson",
      "Ty Chavous"
    ]
  },
  "enablement_categories": [
    "Enablement",
    "Dev Enablement"
  ]
}
```

**Important**: Update the team assignments with your actual team structure. The names must match exactly with the "activity name" column in your CSV data.

## Advanced Usage

Use the `TimeAnalytics` class in your own scripts:

```python
from src.time_analytics import TimeAnalytics

# Initialize
analytics = TimeAnalytics(
    data_path="data/stt_records_automatic.csv",
    mapping_path="config/team_mapping.json"
)

# Load and process
analytics.load_data()
analytics.assign_teams()

# Get hours by team
team_hours = analytics.get_hours_by_team()
print(team_hours)

# Filter by date range
team_hours_filtered = analytics.get_hours_by_team(
    start_date="2024-05-01",
    end_date="2024-05-31"
)

# Get hours by person
person_hours = analytics.get_hours_by_person()

# Get monthly breakdown
monthly_hours = analytics.get_monthly_team_hours()

# Get weekly breakdown
weekly_hours = analytics.get_weekly_team_hours()

# Generate reports
analytics.generate_report(
    start_date="2024-05-01",
    end_date="2024-05-31",
    output_file="output/may_report.txt"
)

# Export to Excel
analytics.export_to_excel(output_file="output/analysis.xlsx")

# Create visualizations
analytics.plot_team_hours_bar(save_path="output/team_hours.png")
analytics.plot_monthly_trends(save_path="output/monthly_trends.png")
```

## Output Files

### Text Report (`output/enablement_report.txt`)
- Summary of hours by team
- Summary of hours by person
- Monthly breakdown

### Excel Report (`output/enablement_analysis.xlsx`)
Multiple sheets containing:
- **Team Summary**: Total hours and sessions by team
- **Person Summary**: Total hours and sessions by person
- **Monthly Trends**: Hours by team per month
- **Weekly Trends**: Hours by team per week
- **Raw Data**: Filtered enablement records with team assignments

### Visualizations
- **team_hours_chart.png**: Bar chart of total hours by team
- **monthly_trends_chart.png**: Line chart showing monthly trends

## Data Structure

The application expects a CSV file with the following columns:
- `activity name`: Person's name or activity identifier
- `time started`: Start timestamp
- `time ended`: End timestamp
- `comment`: Optional comment
- `categories`: Category (e.g., "Enablement", "Dev Enablement")
- `record tags`: Tags
- `duration`: Duration in HH:MM:SS format
- `duration minutes`: Duration in minutes

## Customization

### Adding More Teams

Edit [config/team_mapping.json](config/team_mapping.json) and add your teams:

```json
{
  "teams": {
    "Your Team Name": [
      "Person 1",
      "Person 2"
    ]
  }
}
```

### Changing Enablement Categories

Modify the `enablement_categories` array in [config/team_mapping.json](config/team_mapping.json):

```json
{
  "enablement_categories": [
    "Enablement",
    "Dev Enablement",
    "Training"
  ]
}
```

### Date Filtering

Filter analysis by date range:

```python
# Last month only
team_hours = analytics.get_hours_by_team(
    start_date="2024-05-01",
    end_date="2024-05-31"
)

# From a specific date onwards
team_hours = analytics.get_hours_by_team(start_date="2024-05-01")

# Up to a specific date
team_hours = analytics.get_hours_by_team(end_date="2024-05-31")
```

## Troubleshooting

### Issue: Names not being mapped to teams
- Verify that names in [config/team_mapping.json](config/team_mapping.json) exactly match the "activity name" in your CSV
- Names are case-sensitive

### Issue: No data showing up
- Check that the categories in your data match the `enablement_categories` in [config/team_mapping.json](config/team_mapping.json)
- Verify the CSV path is correct

### Issue: Import errors
- Make sure all dependencies are installed: `pip install -r requirements.txt`

### Issue: Dashboard not loading data
- Click the "Load/Reload Data" button in the sidebar
- Check that file paths in the source code match your actual file locations
