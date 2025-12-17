"""
Personal Role Profile Analysis
Analyzes YOUR work activities (colon-prefixed entries) to understand what you actually do
"""

import pandas as pd
import re
from collections import Counter
from typing import Dict, List
from pathlib import Path


class PersonalRoleProfile:
    """Analyzes personal work activities to generate role profile insights"""

    def __init__(self, data_path: str):
        """
        Initialize the personal role profile analyzer

        Args:
            data_path: Path to the CSV file with time records
        """
        self.data_path = Path(data_path)
        self.df = None

    def load_data(self):
        """Load the CSV data"""
        print(f"Loading data from {self.data_path}...")
        self.df = pd.read_csv(self.data_path)

        # Convert date columns to datetime
        self.df['time started'] = pd.to_datetime(self.df['time started'])
        self.df['time ended'] = pd.to_datetime(self.df['time ended'])

        print(f"Loaded {len(self.df)} records")
        print(f"Date range: {self.df['time started'].min()} to {self.df['time started'].max()}")

    def filter_personal_activities(self) -> pd.DataFrame:
        """
        Filter to only personal work activities (those starting with ':')
        These represent YOUR work, not enablement for others

        Returns:
            DataFrame with only personal activities
        """
        return self.df[self.df['activity name'].str.startswith(':')].copy()

    def extract_keywords_from_comment(self, comment: str, min_length: int = 3) -> List[str]:
        """
        Extract meaningful keywords from a comment string

        Args:
            comment: The comment text to analyze
            min_length: Minimum length for keywords (default 3)

        Returns:
            List of extracted keywords
        """
        if pd.isna(comment) or not comment:
            return []

        # Convert to string and clean
        comment = str(comment).strip()

        # Split on common separators while preserving meaningful phrases
        segments = re.split(r'[,;/|]+|\s{2,}', comment)

        keywords = []
        for segment in segments:
            segment = segment.strip()

            # Skip very short segments
            if len(segment) < min_length:
                continue

            # Remove special characters but keep alphanumeric, spaces, hyphens, and underscores
            cleaned = re.sub(r'[^\w\s\-]', '', segment)
            cleaned = cleaned.strip()

            if cleaned and len(cleaned) >= min_length:
                keywords.append(cleaned)

        return keywords

    def get_role_profile(self, start_date=None, end_date=None) -> Dict:
        """
        Generate a role profile based on ALL your time entries

        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            Dictionary containing role profile analysis
        """
        # Get ALL time entries (not just personal activities)
        personal_df = self.df.copy()

        # Apply date filters
        if start_date:
            start_date = pd.to_datetime(start_date)
            personal_df = personal_df[personal_df['time started'] >= start_date]
        if end_date:
            end_date = pd.to_datetime(end_date)
            personal_df = personal_df[personal_df['time started'] <= end_date]

        if len(personal_df) == 0:
            return {
                'total_hours': 0,
                'task_count': 0,
                'keywords': [],
                'categories': [],
                'error': 'No personal work data found for the specified filters'
            }

        # Calculate basic metrics
        total_hours = personal_df['duration minutes'].sum() / 60
        task_count = len(personal_df)

        # Category analysis
        category_stats = personal_df.groupby('categories').agg({
            'duration minutes': 'sum',
            'activity name': 'count'
        }).reset_index()
        category_stats.columns = ['category', 'minutes', 'task_count']
        category_stats['hours'] = category_stats['minutes'] / 60
        category_stats['percentage'] = (category_stats['hours'] / total_hours * 100).round(1)
        category_stats = category_stats.sort_values('hours', ascending=False)

        # Activity type analysis (the part after the colon)
        personal_df['activity_type'] = personal_df['activity name'].str.replace(':', '', regex=False)
        activity_stats = personal_df.groupby('activity_type').agg({
            'duration minutes': 'sum',
            'activity name': 'count'
        }).reset_index()
        activity_stats.columns = ['activity_type', 'minutes', 'task_count']
        activity_stats['hours'] = activity_stats['minutes'] / 60
        activity_stats['percentage'] = (activity_stats['hours'] / total_hours * 100).round(1)
        activity_stats = activity_stats.sort_values('hours', ascending=False)

        # Extract and count keywords from comments
        all_keywords = []
        keyword_hours = Counter()

        for _, row in personal_df.iterrows():
            keywords = self.extract_keywords_from_comment(row['comment'])
            duration_hours = row['duration minutes'] / 60

            for keyword in keywords:
                # Normalize to title case for consistency
                normalized = keyword.title()
                all_keywords.append(normalized)
                keyword_hours[normalized] += duration_hours

        # Count keyword frequencies
        keyword_counts = Counter(all_keywords)

        # Combine frequency and hours into ranked list
        keyword_data = []
        for keyword in keyword_counts:
            keyword_data.append({
                'keyword': keyword,
                'count': keyword_counts[keyword],
                'hours': round(keyword_hours[keyword], 2),
                'percentage': round((keyword_hours[keyword] / total_hours * 100), 1)
            })

        # Sort by hours (most time spent)
        keyword_data.sort(key=lambda x: x['hours'], reverse=True)

        # Get monthly distribution
        personal_df['year_month'] = personal_df['time started'].dt.to_period('M')
        monthly_dist = personal_df.groupby('year_month').agg({
            'duration minutes': 'sum',
            'activity name': 'count'
        }).reset_index()
        monthly_dist.columns = ['month', 'minutes', 'task_count']
        monthly_dist['hours'] = monthly_dist['minutes'] / 60
        monthly_dist['month'] = monthly_dist['month'].astype(str)

        return {
            'total_hours': round(total_hours, 2),
            'task_count': task_count,
            'tasks_with_comments': personal_df['comment'].notna().sum(),
            'tasks_without_comments': personal_df['comment'].isna().sum(),
            'categories': category_stats.to_dict('records'),
            'activity_types': activity_stats.to_dict('records'),
            'keywords': keyword_data[:100],  # Top 100 keywords
            'all_keywords_count': len(keyword_counts),
            'monthly_distribution': monthly_dist.to_dict('records'),
            'date_range': {
                'start': personal_df['time started'].min().strftime('%Y-%m-%d'),
                'end': personal_df['time started'].max().strftime('%Y-%m-%d')
            }
        }

    def generate_role_summary(self, start_date=None, end_date=None, top_n: int = 20) -> str:
        """
        Generate a text summary of YOUR role profile for writing role descriptions

        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter
            top_n: Number of top keywords to include in summary

        Returns:
            Formatted text summary
        """
        profile = self.get_role_profile(start_date, end_date)

        if 'error' in profile:
            return f"Error: {profile['error']}"

        summary = []
        summary.append("=" * 70)
        summary.append("PERSONAL ROLE PROFILE SUMMARY")
        summary.append("=" * 70)
        summary.append("")

        # Overview
        summary.append("OVERVIEW")
        summary.append("-" * 70)
        summary.append(f"Analysis Period: {profile['date_range']['start']} to {profile['date_range']['end']}")
        summary.append(f"Total Hours Logged: {profile['total_hours']:.1f} hours")
        summary.append(f"Total Tasks: {profile['task_count']}")
        summary.append(f"Tasks with Descriptions: {profile['tasks_with_comments']} ({profile['tasks_with_comments']/profile['task_count']*100:.0f}%)")
        summary.append(f"Unique Topics/Keywords: {profile['all_keywords_count']}")
        summary.append("")

        # Category breakdown
        summary.append("TIME DISTRIBUTION BY CATEGORY")
        summary.append("-" * 70)
        summary.append(f"{'Category':<30} {'Hours':<10} {'% Time':<10} {'Tasks'}")
        summary.append("-" * 70)
        for cat in profile['categories']:
            summary.append(f"{cat['category']:<30} {cat['hours']:<10.1f} {cat['percentage']:<10.1f} {cat['task_count']}")
        summary.append("")

        # Activity type breakdown
        summary.append("TIME DISTRIBUTION BY ACTIVITY TYPE")
        summary.append("-" * 70)
        summary.append(f"{'Activity Type':<30} {'Hours':<10} {'% Time':<10} {'Tasks'}")
        summary.append("-" * 70)
        for act in profile['activity_types']:
            summary.append(f"{act['activity_type']:<30} {act['hours']:<10.1f} {act['percentage']:<10.1f} {act['task_count']}")
        summary.append("")

        # Top keywords
        summary.append(f"TOP {top_n} TOPICS/PROJECTS (by time spent)")
        summary.append("-" * 70)
        summary.append(f"{'Keyword':<35} {'Hours':<10} {'% Time':<10} {'Occurrences'}")
        summary.append("-" * 70)

        for kw in profile['keywords'][:top_n]:
            summary.append(f"{kw['keyword']:<35} {kw['hours']:<10.1f} {kw['percentage']:<10.1f} {kw['count']}")

        summary.append("")

        # Role description bullets
        summary.append("SUGGESTED ROLE DESCRIPTION BULLETS")
        summary.append("-" * 70)

        # Category-based bullets
        top_categories = [cat['category'] for cat in profile['categories'][:3]]
        if len(top_categories) >= 2:
            summary.append(f"• Primary work areas: {', '.join(top_categories)}")

        # Hours breakdown
        if len(profile['categories']) >= 2:
            cat_breakdown = ", ".join([f"{cat['category']} ({cat['percentage']:.0f}%)"
                                      for cat in profile['categories'][:3]])
            summary.append(f"• Time allocation: {cat_breakdown}")

        # Keyword-based bullets
        top_keywords = [kw['keyword'] for kw in profile['keywords'][:10] if kw['hours'] > 1]
        if len(top_keywords) >= 5:
            summary.append(f"• Key technical areas: {', '.join(top_keywords[:5])}")

        if len(top_keywords) >= 10:
            summary.append(f"• Additional experience: {', '.join(top_keywords[5:10])}")

        # Volume metrics
        if profile['total_hours'] > 0:
            avg_task_duration = profile['total_hours'] / profile['task_count']
            summary.append(f"• Completed {profile['task_count']} tasks over {profile['total_hours']:.0f} hours (avg {avg_task_duration:.1f}h per task)")

        summary.append(f"• Worked across {profile['all_keywords_count']} different topics/systems/projects")

        summary.append("")

        # Monthly trend
        summary.append("ACTIVITY OVER TIME")
        summary.append("-" * 70)
        summary.append(f"{'Month':<15} {'Hours':<10} {'Tasks'}")
        summary.append("-" * 70)
        for month_data in profile['monthly_distribution']:
            summary.append(f"{month_data['month']:<15} {month_data['hours']:<10.1f} {month_data['task_count']}")

        summary.append("")
        summary.append("=" * 70)

        return "\n".join(summary)

    def export_to_excel(self, start_date=None, end_date=None, output_file="personal_role_profile.xlsx"):
        """
        Export personal role profile analysis to Excel

        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter
            output_file: Output Excel file path
        """
        profile = self.get_role_profile(start_date, end_date)

        if 'error' in profile:
            print(f"Error: {profile['error']}")
            return

        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Summary sheet
            summary_data = {
                'Metric': ['Total Hours', 'Task Count', 'Tasks with Comments',
                          'Tasks without Comments', 'Unique Keywords', 'Start Date', 'End Date'],
                'Value': [
                    profile['total_hours'],
                    profile['task_count'],
                    profile['tasks_with_comments'],
                    profile['tasks_without_comments'],
                    profile['all_keywords_count'],
                    profile['date_range']['start'],
                    profile['date_range']['end']
                ]
            }
            pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)

            # Categories sheet
            categories_df = pd.DataFrame(profile['categories'])
            categories_df.to_excel(writer, sheet_name='Categories', index=False)

            # Activity Types sheet
            activity_df = pd.DataFrame(profile['activity_types'])
            activity_df.to_excel(writer, sheet_name='Activity Types', index=False)

            # Keywords sheet
            keywords_df = pd.DataFrame(profile['keywords'])
            keywords_df.to_excel(writer, sheet_name='Keywords', index=False)

            # Monthly distribution sheet
            monthly_df = pd.DataFrame(profile['monthly_distribution'])
            monthly_df.to_excel(writer, sheet_name='Monthly Activity', index=False)

        print(f"Personal role profile exported to: {output_file}")


def main():
    """Example usage of the PersonalRoleProfile class"""

    # Initialize
    profile_analyzer = PersonalRoleProfile(
        data_path=r"data\stt_records_automatic.csv"
    )

    # Load data
    profile_analyzer.load_data()

    # Generate role profile for last 6 months
    print("\n" + "=" * 70)
    print("GENERATING PERSONAL ROLE PROFILE")
    print("=" * 70)

    # Generate and print summary
    summary = profile_analyzer.generate_role_summary(
        start_date="2024-05-01",
        end_date="2024-12-31",
        top_n=20
    )
    print(summary)

    # Export to text file
    with open("output/personal_role_profile.txt", 'w') as f:
        f.write(summary)
    print(f"\nText summary saved to: output/personal_role_profile.txt")

    # Export to Excel
    profile_analyzer.export_to_excel(
        start_date="2024-05-01",
        end_date="2024-12-31",
        output_file="output/personal_role_profile.xlsx"
    )


if __name__ == "__main__":
    main()
