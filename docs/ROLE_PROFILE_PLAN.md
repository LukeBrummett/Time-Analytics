# Role Profile Analysis Feature - Implementation Plan

## Overview
Add role profile analysis capability to the Time Analytics application to help users understand "what they actually do" based on their time entry data. This will analyze task patterns, keywords, and activity types to support writing role descriptions and understanding work distribution.

## Current State Analysis

### Available Data
- **Source**: `data/stt_records_automatic.csv` (3,934 records)
- **Key Field**: `comment` - Contains task/activity descriptions
- **Other Fields**: person name, timestamps, duration, categories, teams
- **Comment Examples**:
  - "CIMA Inventories"
  - "Simphony Cloud API"
  - "kiosk issues"
  - "Stand Up"
  - "code reviews"

### Gaps
- No keyword extraction or analysis
- No task categorization beyond manual comment entry
- No role-based profiling
- Comments are currently display-only (not analyzed)

## Proposed Solution

### 1. Keyword Extraction Engine

**Purpose**: Parse comment field to identify task patterns and themes

**Approach**:
- Simple pattern matching and frequency analysis
- Group similar terms (e.g., "Kiosk", "kiosks", "Kiosk Client" → "Kiosk Systems")
- Extract technical domains, activity types, and support levels

**Categories to Extract**:

#### Technical Domains
- APIs / Integration
- Kiosk Systems
- Gaming / Betting
- F&B (Food & Beverage)
- Reports / Analytics
- Configuration
- Infrastructure / Cloud

#### Activity Types
- Development / Coding
- Troubleshooting / Support
- Configuration / Setup
- Meetings / Collaboration
- Code Review
- Documentation
- Planning / Design

#### Support Levels
- Direct hands-on support
- Consultation / Advisory
- Knowledge transfer
- Documentation creation

### 2. Role Profile Analysis

**Purpose**: Aggregate task patterns by person to create "work fingerprint"

**Output Metrics**:
- Time distribution by technical domain (% of total hours)
- Time distribution by activity type (% of total hours)
- Most common keywords/themes (frequency and hours)
- Task diversity score (how varied the work is)
- Evolution over time (how role has changed)

**Report Insights**:
- "You spend 40% of time on API integration, 30% troubleshooting..."
- "Most common systems: Kiosk (45h), Gaming (32h), F&B (28h)"
- "Primary activities: Development (55%), Support (30%), Meetings (15%)"
- Generated bullet points for role description

### 3. Dashboard Integration

**New Tab**: "Role Profile" in Streamlit dashboard

**Visualizations**:
- Pie chart: Time distribution by technical domain
- Pie chart: Time distribution by activity type
- Horizontal bar: Top keywords by hours
- Word cloud: Most frequent task terms
- Timeline: Activity distribution over time (monthly)
- Comparison view: Your profile vs team average (optional)

**Interactive Features**:
- Filter by date range
- Select person (view others' profiles)
- Export role profile as text summary
- Download data as CSV/Excel

**Summary Cards**:
- Total hours analyzed
- Number of unique tasks
- Primary domain (highest %)
- Primary activity (highest %)
- Task diversity score

## Implementation Plan

### Phase 1: Core Analysis Engine
**File**: `src/time_analytics.py`

1. Add keyword extraction method
   - Parse comments field
   - Extract domain keywords
   - Extract activity keywords
   - Handle empty comments gracefully

2. Add role profile analysis method
   - Aggregate keywords by person
   - Calculate time distributions
   - Generate frequency statistics
   - Create summary insights

3. Add export capabilities
   - Generate text role profile report
   - Export to Excel (new sheet)
   - CSV export for raw keyword data

### Phase 2: Dashboard Visualization
**File**: `src/interactive_dashboard.py`

1. Create new "Role Profile" tab
2. Add summary metrics display
3. Add pie charts for distributions
4. Add bar charts for top keywords
5. Add word cloud visualization
6. Add timeline/trend view
7. Add export buttons

### Phase 3: Configuration & Refinement
**File**: `config/role_profile_keywords.json` (new)

1. Create configurable keyword mappings
2. Define domain categories
3. Define activity type mappings
4. Allow user customization

### Phase 4: Testing & Documentation
1. Test with actual data
2. Validate keyword extraction accuracy
3. Update README.md with new feature
4. Update CHANGELOG.md
5. Add usage examples

## Technical Details

### New Methods in TimeAnalytics Class

```python
def extract_keywords(self, comment):
    """Extract categorized keywords from a comment string"""
    pass

def get_role_profile(self, person_name=None):
    """Generate role profile for person or all people"""
    pass

def generate_role_summary(self, person_name):
    """Generate text summary of role for description writing"""
    pass

def export_role_profile_excel(self, output_path):
    """Export role profile analysis to Excel"""
    pass
```

### New Dependencies
- No new dependencies needed (use existing: pandas, plotly, streamlit)
- Optional: `wordcloud` package for word cloud visualization
- Optional: `nltk` for advanced text processing (only if needed)

### Data Structures

```python
role_profile = {
    'person': 'John Doe',
    'total_hours': 120.5,
    'task_count': 145,
    'domains': {
        'API Integration': {'hours': 48.2, 'percentage': 40, 'count': 52},
        'Kiosk Systems': {'hours': 36.15, 'percentage': 30, 'count': 43},
        # ...
    },
    'activities': {
        'Development': {'hours': 66.28, 'percentage': 55, 'count': 78},
        'Support': {'hours': 36.15, 'percentage': 30, 'count': 45},
        # ...
    },
    'keywords': [
        {'term': 'API', 'hours': 32.5, 'count': 28},
        {'term': 'Kiosk', 'hours': 28.3, 'count': 35},
        # ...
    ]
}
```

## Expected Outcomes

### For User
- Clear understanding of work distribution
- Data-driven insights for role description writing
- Bullet points and summaries ready to use
- Ability to track role evolution over time

### For Teams
- Compare role profiles across team members
- Identify specialization areas
- Balance workload by activity type
- Understand team capability distribution

## Next Steps

1. Review and approve this plan
2. Implement Phase 1 (core engine)
3. Test keyword extraction with sample data
4. Implement Phase 2 (dashboard)
5. Iterate based on feedback

## Questions to Consider

- Should we use a predefined keyword list or purely frequency-based extraction?
- Do you want to manually tag/categorize some keywords first?
- Should role profiles compare against team averages or just show individual data?
- What time period is most relevant for role description (last 3 months? 6 months? All time?)
- Do you want to exclude certain activity types (e.g., meetings) from the profile?
