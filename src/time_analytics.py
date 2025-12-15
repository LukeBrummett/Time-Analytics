"""
Time Analytics Application
Analyzes enablement hours by team from time tracking data
"""

import pandas as pd
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import seaborn as sns

class TimeAnalytics:
    """Main class for analyzing time tracking data"""

    def __init__(self, data_path: str, mapping_path: str = "config/team_mapping.json"):
        """
        Initialize the analytics application

        Args:
            data_path: Path to the CSV file with time records
            mapping_path: Path to the JSON file with team mappings
        """
        self.data_path = Path(data_path)
        self.mapping_path = Path(mapping_path)
        self.df = None
        self.team_mapping = None
        self.person_to_team = {}
        self.enablement_categories = []

    def load_data(self):
        """Load the CSV data and team mapping"""
        print(f"Loading data from {self.data_path}...")
        self.df = pd.read_csv(self.data_path)

        # Convert date columns to datetime
        self.df['time started'] = pd.to_datetime(self.df['time started'])
        self.df['time ended'] = pd.to_datetime(self.df['time ended'])

        # Load team mapping
        with open(self.mapping_path, 'r') as f:
            self.team_mapping = json.load(f)

        # Create reverse mapping: person -> team
        for team, people in self.team_mapping['teams'].items():
            for person in people:
                self.person_to_team[person] = team

        self.enablement_categories = self.team_mapping['enablement_categories']

        print(f"Loaded {len(self.df)} records")
        print(f"Date range: {self.df['time started'].min()} to {self.df['time started'].max()}")

    def assign_teams(self):
        """Assign team information to each record"""
        self.df['team'] = self.df['activity name'].map(self.person_to_team)
        self.df['is_enablement'] = self.df['categories'].isin(self.enablement_categories)

    def filter_enablement_records(self) -> pd.DataFrame:
        """Filter to only enablement records with assigned teams"""
        return self.df[
            (self.df['is_enablement'] == True) &
            (self.df['team'].notna())
        ].copy()

    def get_hours_by_team(self, start_date=None, end_date=None) -> pd.DataFrame:
        """
        Get total enablement hours by team

        Args:
            start_date: Optional start date filter (string or datetime)
            end_date: Optional end date filter (string or datetime)

        Returns:
            DataFrame with team hours summary
        """
        filtered_df = self.filter_enablement_records()

        # Apply date filters if provided
        if start_date:
            start_date = pd.to_datetime(start_date)
            filtered_df = filtered_df[filtered_df['time started'] >= start_date]
        if end_date:
            end_date = pd.to_datetime(end_date)
            filtered_df = filtered_df[filtered_df['time started'] <= end_date]

        # Group by team and sum duration
        team_hours = filtered_df.groupby('team').agg({
            'duration minutes': 'sum',
            'activity name': 'count'
        }).reset_index()

        team_hours.columns = ['Team', 'Total Minutes', 'Number of Sessions']
        team_hours['Total Hours'] = team_hours['Total Minutes'] / 60
        team_hours = team_hours.sort_values('Total Hours', ascending=False)

        return team_hours

    def get_hours_by_person(self, start_date=None, end_date=None) -> pd.DataFrame:
        """
        Get total enablement hours by person with team information

        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            DataFrame with person hours summary
        """
        filtered_df = self.filter_enablement_records()

        # Apply date filters
        if start_date:
            start_date = pd.to_datetime(start_date)
            filtered_df = filtered_df[filtered_df['time started'] >= start_date]
        if end_date:
            end_date = pd.to_datetime(end_date)
            filtered_df = filtered_df[filtered_df['time started'] <= end_date]

        # Group by person and team
        person_hours = filtered_df.groupby(['activity name', 'team']).agg({
            'duration minutes': ['sum', 'count']
        }).reset_index()

        # Flatten multi-level columns
        person_hours.columns = ['Person', 'Team', 'Total Minutes', 'Number of Sessions']
        person_hours['Total Hours'] = person_hours['Total Minutes'] / 60
        person_hours = person_hours.sort_values('Total Hours', ascending=False)

        return person_hours

    def get_monthly_team_hours(self) -> pd.DataFrame:
        """Get enablement hours by team broken down by month"""
        filtered_df = self.filter_enablement_records()

        # Extract year-month
        filtered_df['year_month'] = filtered_df['time started'].dt.to_period('M')

        # Group by team and month
        monthly_hours = filtered_df.groupby(['team', 'year_month']).agg({
            'duration minutes': 'sum'
        }).reset_index()

        monthly_hours.columns = ['Team', 'Month', 'Total Minutes']
        monthly_hours['Total Hours'] = monthly_hours['Total Minutes'] / 60
        monthly_hours['Month'] = monthly_hours['Month'].astype(str)

        return monthly_hours

    def get_weekly_team_hours(self) -> pd.DataFrame:
        """Get enablement hours by team broken down by week"""
        filtered_df = self.filter_enablement_records()

        # Extract year-week
        filtered_df['year_week'] = filtered_df['time started'].dt.to_period('W')

        # Group by team and week
        weekly_hours = filtered_df.groupby(['team', 'year_week']).agg({
            'duration minutes': 'sum'
        }).reset_index()

        weekly_hours.columns = ['Team', 'Week', 'Total Minutes']
        weekly_hours['Total Hours'] = weekly_hours['Total Minutes'] / 60
        weekly_hours['Week'] = weekly_hours['Week'].astype(str)

        return weekly_hours

    def plot_team_hours_bar(self, start_date=None, end_date=None, save_path=None):
        """Create a bar chart of total hours by team"""
        team_hours = self.get_hours_by_team(start_date, end_date)

        plt.figure(figsize=(10, 6))
        plt.bar(team_hours['Team'], team_hours['Total Hours'])
        plt.xlabel('Team')
        plt.ylabel('Total Hours')
        plt.title('Enablement Hours by Team')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path)
            print(f"Chart saved to {save_path}")
        else:
            plt.show()

    def plot_monthly_trends(self, save_path=None):
        """Create a line chart showing monthly trends by team"""
        monthly_hours = self.get_monthly_team_hours()

        plt.figure(figsize=(12, 6))
        for team in monthly_hours['Team'].unique():
            team_data = monthly_hours[monthly_hours['Team'] == team]
            plt.plot(team_data['Month'], team_data['Total Hours'], marker='o', label=team)

        plt.xlabel('Month')
        plt.ylabel('Total Hours')
        plt.title('Monthly Enablement Hours by Team')
        plt.legend()
        plt.xticks(rotation=45, ha='right')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path)
            print(f"Chart saved to {save_path}")
        else:
            plt.show()

    def generate_report(self, start_date=None, end_date=None, output_file="report.txt"):
        """Generate a text report of enablement hours"""
        with open(output_file, 'w') as f:
            f.write("=" * 60 + "\n")
            f.write("ENABLEMENT HOURS REPORT\n")
            f.write("=" * 60 + "\n\n")

            if start_date or end_date:
                f.write(f"Date Range: {start_date or 'Beginning'} to {end_date or 'End'}\n\n")

            # Team summary
            team_hours = self.get_hours_by_team(start_date, end_date)
            f.write("HOURS BY TEAM\n")
            f.write("-" * 60 + "\n")
            f.write(team_hours.to_string(index=False))
            f.write("\n\n")

            # Person summary
            person_hours = self.get_hours_by_person(start_date, end_date)
            f.write("HOURS BY PERSON\n")
            f.write("-" * 60 + "\n")
            f.write(person_hours.to_string(index=False))
            f.write("\n\n")

            # Monthly trends
            monthly_hours = self.get_monthly_team_hours()
            f.write("MONTHLY BREAKDOWN\n")
            f.write("-" * 60 + "\n")
            f.write(monthly_hours.to_string(index=False))
            f.write("\n")

        print(f"Report generated: {output_file}")

    def export_to_excel(self, output_file="enablement_analysis.xlsx"):
        """Export all analyses to an Excel file with multiple sheets"""
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Team summary
            team_hours = self.get_hours_by_team()
            team_hours.to_excel(writer, sheet_name='Team Summary', index=False)

            # Person summary
            person_hours = self.get_hours_by_person()
            person_hours.to_excel(writer, sheet_name='Person Summary', index=False)

            # Monthly trends
            monthly_hours = self.get_monthly_team_hours()
            monthly_hours.to_excel(writer, sheet_name='Monthly Trends', index=False)

            # Weekly trends
            weekly_hours = self.get_weekly_team_hours()
            weekly_hours.to_excel(writer, sheet_name='Weekly Trends', index=False)

            # Raw enablement data
            enablement_df = self.filter_enablement_records()
            enablement_df.to_excel(writer, sheet_name='Raw Data', index=False)

        print(f"Excel report generated: {output_file}")


def main():
    """Example usage of the TimeAnalytics class"""

    # Initialize the analytics app
    analytics = TimeAnalytics(
        data_path=r"data\stt_records_automatic.csv",
        mapping_path="config/team_mapping.json"
    )

    # Load and process data
    analytics.load_data()
    analytics.assign_teams()

    # Print quick summary
    print("\n" + "="*60)
    print("TEAM HOURS SUMMARY")
    print("="*60)
    team_hours = analytics.get_hours_by_team()
    print(team_hours.to_string(index=False))

    print("\n" + "="*60)
    print("PERSON HOURS SUMMARY")
    print("="*60)
    person_hours = analytics.get_hours_by_person()
    print(person_hours.to_string(index=False))

    # Generate reports
    analytics.generate_report(output_file="output/enablement_report.txt")
    analytics.export_to_excel(output_file="output/enablement_analysis.xlsx")

    # Create visualizations (optional - uncomment to generate)
    # analytics.plot_team_hours_bar(save_path="team_hours_chart.png")
    # analytics.plot_monthly_trends(save_path="monthly_trends_chart.png")


if __name__ == "__main__":
    main()
