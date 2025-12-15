"""
Interactive Time Analytics Dashboard
Provides an interactive web interface for analyzing enablement hours
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from time_analytics import TimeAnalytics

# Page config
st.set_page_config(
    page_title="Enablement Hours Dashboard",
    page_icon="📊",
    layout="wide"
)

# Initialize session state
if 'analytics' not in st.session_state:
    st.session_state.analytics = None
    st.session_state.data_loaded = False

# Title
st.title("📊 Enablement Hours Analytics Dashboard")

# Sidebar for data loading and filters
with st.sidebar:
    st.header("⚙️ Settings")

    # Data loading
    if st.button("🔄 Load/Reload Data"):
        with st.spinner("Loading data..."):
            analytics = TimeAnalytics(
                data_path=r"data\stt_records_automatic.csv",
                mapping_path="config/team_mapping.json"
            )
            analytics.load_data()
            analytics.assign_teams()
            st.session_state.analytics = analytics
            st.session_state.data_loaded = True
            st.success("Data loaded successfully!")

    if not st.session_state.data_loaded:
        st.info("👆 Click 'Load/Reload Data' to start")
        st.stop()

    analytics = st.session_state.analytics

    st.divider()
    st.header("🔍 Filters")

    # Date range selector
    min_date = analytics.df['time started'].min().date()
    max_date = analytics.df['time started'].max().date()

    date_preset = st.selectbox(
        "Quick Select",
        ["All Time", "Last 7 Days", "Last 30 Days", "Last 90 Days", "This Year", "Custom Range"]
    )

    if date_preset == "Custom Range":
        start_date = st.date_input("Start Date", min_date, min_value=min_date, max_value=max_date)
        end_date = st.date_input("End Date", max_date, min_value=min_date, max_value=max_date)
    elif date_preset == "Last 7 Days":
        end_date = max_date
        start_date = max_date - timedelta(days=7)
    elif date_preset == "Last 30 Days":
        end_date = max_date
        start_date = max_date - timedelta(days=30)
    elif date_preset == "Last 90 Days":
        end_date = max_date
        start_date = max_date - timedelta(days=90)
    elif date_preset == "This Year":
        end_date = max_date
        start_date = datetime(max_date.year, 1, 1).date()
    else:  # All Time
        start_date = min_date
        end_date = max_date

    st.caption(f"📅 Range: {start_date} to {end_date}")

    # Team filter
    all_teams = sorted(analytics.df[analytics.df['team'].notna()]['team'].unique())
    selected_teams = st.multiselect("Teams", all_teams, default=all_teams)

    # Person filter
    enablement_df = analytics.filter_enablement_records()
    all_people = sorted(enablement_df['activity name'].unique())
    selected_people = st.multiselect("People (optional)", all_people)

# Main content
if st.session_state.data_loaded:
    analytics = st.session_state.analytics

    # Get filtered data
    team_hours = analytics.get_hours_by_team(start_date, end_date)
    person_hours = analytics.get_hours_by_person(start_date, end_date)
    monthly_hours = analytics.get_monthly_team_hours()

    # Apply team filter
    if selected_teams:
        team_hours = team_hours[team_hours['Team'].isin(selected_teams)]
        person_hours = person_hours[person_hours['Team'].isin(selected_teams)]
        monthly_hours = monthly_hours[monthly_hours['Team'].isin(selected_teams)]

    # Apply person filter
    if selected_people:
        person_hours = person_hours[person_hours['Person'].isin(selected_people)]

    # Filter monthly data by date range
    monthly_hours_filtered = monthly_hours.copy()
    monthly_hours_filtered['Month_dt'] = pd.to_datetime(monthly_hours_filtered['Month'])
    monthly_hours_filtered = monthly_hours_filtered[
        (monthly_hours_filtered['Month_dt'] >= pd.to_datetime(start_date)) &
        (monthly_hours_filtered['Month_dt'] <= pd.to_datetime(end_date))
    ]

    # Summary metrics
    st.header("📈 Enablement Overview")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_hours = team_hours['Total Hours'].sum()
        st.metric("Total Enablement Hours", f"{total_hours:.1f}")

    with col2:
        total_sessions = team_hours['Number of Sessions'].sum()
        st.metric("Total Support Sessions", f"{total_sessions:,}")

    with col3:
        num_teams = len(team_hours)
        st.metric("Teams Supported", num_teams)

    with col4:
        num_people = len(person_hours)
        st.metric("People Supported", num_people)

    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["🏆 Team Analysis", "👤 Individual Support", "📊 Trends", "📋 Data Table"])

    with tab1:
        st.subheader("Team Enablement Analysis")

        st.info("💡 **Interpretation:** Teams with higher hours received more enablement support. This could indicate growth, new projects, or complex challenges.")

        col1, col2 = st.columns(2)

        with col1:
            # Team hours bar chart
            if not team_hours.empty:
                fig = px.bar(
                    team_hours,
                    x='Team',
                    y='Total Hours',
                    title='Enablement Hours Received by Team',
                    color='Total Hours',
                    color_continuous_scale='Blues',
                    text='Total Hours'
                )
                fig.update_traces(texttemplate='%{text:.1f}h', textposition='outside')
                fig.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Team distribution pie chart
            if not team_hours.empty:
                fig = px.pie(
                    team_hours,
                    values='Total Hours',
                    names='Team',
                    title='Enablement Effort Distribution',
                    hole=0.4
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)

        # Sessions by team
        if not team_hours.empty:
            fig = px.bar(
                team_hours,
                x='Team',
                y='Number of Sessions',
                title='Support Sessions by Team',
                color='Number of Sessions',
                color_continuous_scale='Greens',
                text='Number of Sessions'
            )
            fig.update_traces(texttemplate='%{text}', textposition='outside')
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("Individual Enablement Analysis")

        st.info("💡 **Note:** Higher hours indicate more enablement support received. Lower hours suggest greater independence.")

        # Sorting option
        col1, col2 = st.columns([2, 1])
        with col1:
            sort_order = st.radio(
                "Sort by",
                ["Most Support Needed (High to Low)", "Most Independent (Low to High)"],
                horizontal=True
            )
        with col2:
            top_n = st.slider("Show top", 5, 50, 15)

        # Sort data based on selection
        if sort_order == "Most Independent (Low to High)":
            person_hours_sorted = person_hours.sort_values('Total Hours', ascending=True).head(top_n)
            sort_label = "Most Independent"
        else:
            person_hours_sorted = person_hours.head(top_n)  # Already sorted high to low
            sort_label = "Highest Support Hours"

        col1, col2 = st.columns(2)

        with col1:
            # Enablement hours by person
            if not person_hours_sorted.empty:
                fig = px.bar(
                    person_hours_sorted,
                    x='Total Hours',
                    y='Person',
                    orientation='h',
                    title=f'{sort_label} - Top {top_n} by Hours',
                    color='Team',
                    text='Total Hours'
                )
                fig.update_traces(texttemplate='%{text:.1f}h', textposition='outside')
                fig.update_layout(height=max(400, top_n * 25), yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Sessions per person
            if not person_hours_sorted.empty:
                fig = px.bar(
                    person_hours_sorted,
                    x='Number of Sessions',
                    y='Person',
                    orientation='h',
                    title=f'{sort_label} - Top {top_n} by Sessions',
                    color='Team',
                    text='Number of Sessions'
                )
                fig.update_traces(texttemplate='%{text}', textposition='outside')
                fig.update_layout(height=max(400, top_n * 25), yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig, use_container_width=True)

        # Average session duration by person
        st.subheader("Session Duration Analysis")
        st.caption("Longer sessions may indicate complex issues or deeper learning needs")

        if not person_hours.empty:
            person_hours_with_avg = person_hours.copy()
            person_hours_with_avg['Avg Session (hours)'] = person_hours_with_avg['Total Hours'] / person_hours_with_avg['Number of Sessions']

            # Let user choose sorting for average duration too
            avg_sort = st.radio(
                "Sort average session duration by",
                ["Longest Sessions", "Shortest Sessions"],
                horizontal=True,
                key="avg_sort"
            )

            if avg_sort == "Shortest Sessions":
                person_hours_with_avg = person_hours_with_avg.sort_values('Avg Session (hours)', ascending=True).head(top_n)
            else:
                person_hours_with_avg = person_hours_with_avg.sort_values('Avg Session (hours)', ascending=False).head(top_n)

            fig = px.bar(
                person_hours_with_avg,
                x='Avg Session (hours)',
                y='Person',
                orientation='h',
                title=f'Average Session Duration - Top {top_n}',
                color='Team',
                text='Avg Session (hours)'
            )
            fig.update_traces(texttemplate='%{text:.2f}h', textposition='outside')
            fig.update_layout(height=max(400, top_n * 25), yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.subheader("Trends Over Time")

        # Normalization options
        col1, col2 = st.columns([2, 1])
        with col1:
            trend_view = st.radio(
                "View Type",
                ["Absolute Hours", "Percentage of Total", "Moving Average (4 weeks)"],
                horizontal=True
            )
        with col2:
            show_stacked = st.checkbox("Show Stacked View", value=False)

        # Monthly trends
        if not monthly_hours_filtered.empty:
            monthly_pivot = monthly_hours_filtered.pivot(index='Month', columns='Team', values='Total Hours').fillna(0)

            # Apply normalization based on selection
            if trend_view == "Percentage of Total":
                # Calculate percentage of total for each month
                monthly_pivot_normalized = monthly_pivot.div(monthly_pivot.sum(axis=1), axis=0) * 100
                y_label = "Percentage of Total Hours (%)"
                title_suffix = "as Percentage of Total"
                value_format = ".1f"
            elif trend_view == "Moving Average (4 weeks)":
                # Apply 4-week moving average
                monthly_pivot_normalized = monthly_pivot.rolling(window=4, min_periods=1).mean()
                y_label = "Hours (4-week Moving Average)"
                title_suffix = "with 4-week Moving Average"
                value_format = ".1f"
            else:  # Absolute Hours
                monthly_pivot_normalized = monthly_pivot
                y_label = "Total Hours"
                title_suffix = ""
                value_format = ".1f"

            # Create the appropriate chart
            if show_stacked:
                # Stacked area chart
                fig = go.Figure()
                for team in monthly_pivot_normalized.columns:
                    fig.add_trace(go.Scatter(
                        x=monthly_pivot_normalized.index,
                        y=monthly_pivot_normalized[team],
                        name=team,
                        mode='lines',
                        stackgroup='one',
                        hovertemplate='%{y:' + value_format + '}<extra></extra>'
                    ))
                chart_title = f'Stacked Team Hours Over Time {title_suffix}'
            else:
                # Line chart
                fig = go.Figure()
                for team in monthly_pivot_normalized.columns:
                    fig.add_trace(go.Scatter(
                        x=monthly_pivot_normalized.index,
                        y=monthly_pivot_normalized[team],
                        name=team,
                        mode='lines+markers',
                        hovertemplate='%{y:' + value_format + '}<extra></extra>'
                    ))
                chart_title = f'Monthly Team Hours {title_suffix}'

            fig.update_layout(
                title=chart_title,
                xaxis_title='Month',
                yaxis_title=y_label,
                height=500,
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)

            # Add explanation for normalization
            if trend_view == "Percentage of Total":
                st.info("📊 **Percentage View:** Shows each team's contribution as a percentage of total hours per month. This normalizes for overall activity level and makes it easier to see relative team effort over time.")
            elif trend_view == "Moving Average (4 weeks)":
                st.info("📈 **Moving Average:** Smooths out weekly variations and missing data by averaging the last 4 weeks. This helps identify genuine trends while reducing noise from irregular logging.")

        # Weekly granularity option
        st.divider()
        st.subheader("Detailed Time Period Analysis")

        time_granularity = st.radio(
            "Time Granularity",
            ["Monthly", "Weekly"],
            horizontal=True
        )

        if time_granularity == "Weekly":
            # Get weekly data
            weekly_df = analytics.filter_enablement_records()
            weekly_df = weekly_df[
                (weekly_df['time started'] >= pd.to_datetime(start_date)) &
                (weekly_df['time started'] <= pd.to_datetime(end_date))
            ]

            if selected_teams:
                weekly_df = weekly_df[weekly_df['team'].isin(selected_teams)]

            # Group by week
            weekly_df['year_week'] = weekly_df['time started'].dt.to_period('W').astype(str)
            weekly_hours = weekly_df.groupby(['team', 'year_week']).agg({
                'duration minutes': 'sum'
            }).reset_index()
            weekly_hours['Total Hours'] = weekly_hours['duration minutes'] / 60

            weekly_pivot = weekly_hours.pivot(index='year_week', columns='team', values='Total Hours').fillna(0)

            # Apply moving average for weekly data (2 weeks)
            weekly_smoothed = weekly_pivot.rolling(window=2, min_periods=1).mean()

            fig = go.Figure()
            for team in weekly_smoothed.columns:
                fig.add_trace(go.Scatter(
                    x=weekly_smoothed.index,
                    y=weekly_smoothed[team],
                    name=team,
                    mode='lines+markers',
                    hovertemplate='%{y:.1f}h<extra></extra>'
                ))

            fig.update_layout(
                title='Weekly Team Hours (2-week Moving Average)',
                xaxis_title='Week',
                yaxis_title='Hours (2-week MA)',
                height=500,
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
            st.info("📅 **Weekly View:** Shows hours at weekly granularity with 2-week moving average to smooth out individual week variations.")

        # Person-specific trends
        if selected_people:
            st.divider()
            st.subheader("Individual Trends")

            person_trend_view = st.radio(
                "Normalization for Individual Trends",
                ["Actual Hours", "Moving Average (4 weeks)"],
                horizontal=True,
                key="person_trend_view"
            )

            for person in selected_people:
                person_data = enablement_df[enablement_df['activity name'] == person].copy()
                person_data = person_data[
                    (person_data['time started'] >= pd.to_datetime(start_date)) &
                    (person_data['time started'] <= pd.to_datetime(end_date))
                ]

                if not person_data.empty:
                    person_data['year_month'] = person_data['time started'].dt.to_period('M').astype(str)
                    person_monthly = person_data.groupby('year_month').agg({
                        'duration minutes': 'sum'
                    }).reset_index()
                    person_monthly['Total Hours'] = person_monthly['duration minutes'] / 60

                    # Apply moving average if selected
                    if person_trend_view == "Moving Average (4 weeks)":
                        person_monthly = person_monthly.set_index('year_month')
                        person_monthly['Total Hours'] = person_monthly['Total Hours'].rolling(window=4, min_periods=1).mean()
                        person_monthly = person_monthly.reset_index()
                        y_title = "Hours (4-week MA)"
                    else:
                        y_title = "Total Hours"

                    fig = px.line(
                        person_monthly,
                        x='year_month',
                        y='Total Hours',
                        title=f'{person} - Monthly Hours',
                        markers=True
                    )
                    fig.update_layout(
                        height=300,
                        yaxis_title=y_title
                    )
                    st.plotly_chart(fig, use_container_width=True)

    with tab4:
        st.subheader("Data Tables")

        view_option = st.radio("Select View", ["Team Summary", "Person Summary", "Monthly Data"])

        if view_option == "Team Summary":
            st.dataframe(
                team_hours.style.format({
                    'Total Hours': '{:.2f}',
                    'Total Minutes': '{:.0f}'
                }),
                use_container_width=True,
                hide_index=True
            )

            # Download button
            csv = team_hours.to_csv(index=False)
            st.download_button(
                label="📥 Download Team Data as CSV",
                data=csv,
                file_name=f"team_hours_{start_date}_to_{end_date}.csv",
                mime="text/csv"
            )

        elif view_option == "Person Summary":
            st.dataframe(
                person_hours.style.format({
                    'Total Hours': '{:.2f}',
                    'Total Minutes': '{:.0f}'
                }),
                use_container_width=True,
                hide_index=True
            )

            # Download button
            csv = person_hours.to_csv(index=False)
            st.download_button(
                label="📥 Download Person Data as CSV",
                data=csv,
                file_name=f"person_hours_{start_date}_to_{end_date}.csv",
                mime="text/csv"
            )

        else:  # Monthly Data
            st.dataframe(
                monthly_hours_filtered[['Team', 'Month', 'Total Hours']].style.format({
                    'Total Hours': '{:.2f}'
                }),
                use_container_width=True,
                hide_index=True
            )

            # Download button
            csv = monthly_hours_filtered[['Team', 'Month', 'Total Hours']].to_csv(index=False)
            st.download_button(
                label="📥 Download Monthly Data as CSV",
                data=csv,
                file_name=f"monthly_hours_{start_date}_to_{end_date}.csv",
                mime="text/csv"
            )

# Footer
st.divider()
st.caption("📊 Time Analytics Dashboard | Built with Streamlit & Plotly")
