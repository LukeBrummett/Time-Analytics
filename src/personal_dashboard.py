"""
Personal Role Profile Dashboard
Interactive dashboard showing what YOU actually work on
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from personal_role_profile import PersonalRoleProfile

# Page config
st.set_page_config(
    page_title="Personal Role Profile",
    page_icon="👤",
    layout="wide"
)

# Initialize session state
if 'profile_analyzer' not in st.session_state:
    st.session_state.profile_analyzer = None
    st.session_state.data_loaded = False

# Title
st.title("👤 Personal Role Profile - What Do I Actually Do?")

# Sidebar for data loading and filters
with st.sidebar:
    st.header("⚙️ Settings")

    # Data loading
    if st.button("🔄 Load/Reload Data"):
        with st.spinner("Loading data..."):
            analyzer = PersonalRoleProfile(
                data_path=r"data\stt_records_automatic.csv"
            )
            analyzer.load_data()
            st.session_state.profile_analyzer = analyzer
            st.session_state.data_loaded = True
            st.success("Data loaded successfully!")

    if not st.session_state.data_loaded:
        st.info("👆 Click 'Load/Reload Data' to start")
        st.stop()

    analyzer = st.session_state.profile_analyzer

    st.divider()
    st.header("🔍 Filters")

    # Date range selector
    min_date = analyzer.df['time started'].min().date()
    max_date = analyzer.df['time started'].max().date()

    date_preset = st.selectbox(
        "Quick Select",
        ["All Time", "Last 30 Days", "Last 90 Days", "Last 6 Months", "This Year", "Custom Range"]
    )

    if date_preset == "Custom Range":
        start_date = st.date_input("Start Date", min_date, min_value=min_date, max_value=max_date)
        end_date = st.date_input("End Date", max_date, min_value=min_date, max_value=max_date)
    elif date_preset == "Last 30 Days":
        end_date = max_date
        start_date = max_date - timedelta(days=30)
    elif date_preset == "Last 90 Days":
        end_date = max_date
        start_date = max_date - timedelta(days=90)
    elif date_preset == "Last 6 Months":
        end_date = max_date
        start_date = max_date - timedelta(days=180)
    elif date_preset == "This Year":
        end_date = max_date
        start_date = datetime(max_date.year, 1, 1).date()
    else:  # All Time
        start_date = min_date
        end_date = max_date

    st.caption(f"📅 Range: {start_date} to {end_date}")

# Main content
if st.session_state.data_loaded:
    analyzer = st.session_state.profile_analyzer

    # Get profile data
    profile = analyzer.get_role_profile(start_date, end_date)

    if 'error' in profile:
        st.error(f"Error: {profile['error']}")
        st.stop()

    # Summary metrics
    st.header("📈 Your Work Overview")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Hours", f"{profile['total_hours']:.1f}")

    with col2:
        st.metric("Total Tasks", f"{profile['task_count']:,}")

    with col3:
        st.metric("Unique Topics", profile['all_keywords_count'])

    with col4:
        completion_rate = (profile['tasks_with_comments'] / profile['task_count'] * 100)
        st.metric("Tasks Documented", f"{completion_rate:.0f}%")

    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["🎨 Word Cloud", "📊 Keywords Analysis", "📈 Time Distribution", "📋 Export"])

    with tab1:
        st.subheader("🎨 What You Actually Work On")
        st.info("💡 **Word Bubble**: Larger bubbles = more time spent. This visualizes the actual topics/projects you work on based on your task descriptions.")

        if profile['keywords']:
            col1, col2 = st.columns([2, 1])

            with col1:
                # Create bubble chart (word cloud alternative)
                top_50 = profile['keywords'][:50]
                keywords_df = pd.DataFrame(top_50)

                # Create scatter plot with text as bubbles
                fig = px.scatter(
                    keywords_df,
                    x='count',
                    y='hours',
                    size='hours',
                    color='percentage',
                    hover_data=['keyword', 'hours', 'count', 'percentage'],
                    text='keyword',
                    title='Keyword Bubble Chart (Top 50)',
                    labels={'count': 'Number of Occurrences', 'hours': 'Hours Spent'},
                    color_continuous_scale='Viridis',
                    size_max=60
                )

                # Update layout for better text visibility
                fig.update_traces(
                    textposition='middle center',
                    textfont=dict(size=10, color='white')
                )
                fig.update_layout(
                    height=600,
                    showlegend=False,
                    xaxis_title="Number of Occurrences",
                    yaxis_title="Hours Spent"
                )
                st.plotly_chart(fig, use_container_width=True)

                st.caption("💡 Hover over bubbles for details. Larger bubbles = more hours spent.")

            with col2:
                st.markdown("### Top 10 Topics")
                top_10 = profile['keywords'][:10]
                for i, kw in enumerate(top_10, 1):
                    st.markdown(f"**{i}. {kw['keyword']}**")
                    st.caption(f"{kw['hours']:.1f}h ({kw['percentage']:.1f}%) • {kw['count']} times")
                    # Normalize progress bar relative to top keyword
                    max_pct = profile['keywords'][0]['percentage'] if profile['keywords'][0]['percentage'] > 0 else 1
                    st.progress(kw['percentage'] / max_pct)

        else:
            st.warning("No keywords found in your task descriptions.")

    with tab2:
        st.subheader("📊 Detailed Keywords Analysis")

        # Number of keywords to display
        top_n = st.slider("Number of keywords to display", 10, 50, 25)

        if profile['keywords']:
            keywords_df = pd.DataFrame(profile['keywords'][:top_n])

            col1, col2 = st.columns([3, 2])

            with col1:
                # Horizontal bar chart
                fig = px.bar(
                    keywords_df,
                    y='keyword',
                    x='hours',
                    orientation='h',
                    title=f'Top {top_n} Keywords by Time Spent',
                    text='hours',
                    color='hours',
                    color_continuous_scale='Blues'
                )
                fig.update_traces(texttemplate='%{text:.1f}h', textposition='outside')
                fig.update_layout(
                    height=max(500, top_n * 20),
                    yaxis={'categoryorder':'total ascending'},
                    showlegend=False,
                    xaxis_title="Hours",
                    yaxis_title=""
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Treemap
                fig = px.treemap(
                    keywords_df.head(15),
                    path=['keyword'],
                    values='hours',
                    title='Top 15 Keywords (Treemap)',
                    color='hours',
                    color_continuous_scale='Greens'
                )
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)

            # Detailed table
            st.markdown("### Keyword Details")
            st.dataframe(
                keywords_df[['keyword', 'hours', 'percentage', 'count']].style.format({
                    'hours': '{:.2f}',
                    'percentage': '{:.1f}%',
                    'count': '{:.0f}'
                }),
                use_container_width=True,
                hide_index=True
            )

        else:
            st.warning("No keywords found.")

    with tab3:
        st.subheader("📈 How You Spend Your Time")

        col1, col2 = st.columns(2)

        with col1:
            # Category breakdown
            if profile['categories']:
                cat_df = pd.DataFrame(profile['categories'])

                fig = px.pie(
                    cat_df,
                    values='hours',
                    names='category',
                    title='Time by Category',
                    hole=0.4
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)

                # Category details
                st.markdown("#### Category Breakdown")
                st.dataframe(
                    cat_df[['category', 'hours', 'percentage', 'task_count']].style.format({
                        'hours': '{:.1f}',
                        'percentage': '{:.1f}%',
                        'task_count': '{:.0f}'
                    }),
                    use_container_width=True,
                    hide_index=True
                )

        with col2:
            # Activity type breakdown
            if profile['activity_types']:
                act_df = pd.DataFrame(profile['activity_types'])

                fig = px.bar(
                    act_df,
                    x='activity_type',
                    y='hours',
                    title='Time by Activity Type',
                    text='hours',
                    color='hours',
                    color_continuous_scale='Oranges'
                )
                fig.update_traces(texttemplate='%{text:.1f}h', textposition='outside')
                fig.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

                # Activity details
                st.markdown("#### Activity Type Breakdown")
                st.dataframe(
                    act_df[['activity_type', 'hours', 'percentage', 'task_count']].style.format({
                        'hours': '{:.1f}',
                        'percentage': '{:.1f}%',
                        'task_count': '{:.0f}'
                    }),
                    use_container_width=True,
                    hide_index=True
                )

        # Monthly trends
        st.divider()
        st.markdown("### Activity Over Time")

        if profile['monthly_distribution']:
            monthly_df = pd.DataFrame(profile['monthly_distribution'])

            col1, col2 = st.columns(2)

            with col1:
                # Hours over time
                fig = px.line(
                    monthly_df,
                    x='month',
                    y='hours',
                    title='Hours per Month',
                    markers=True
                )
                fig.update_layout(height=300, xaxis_title="Month", yaxis_title="Hours")
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Tasks over time
                fig = px.line(
                    monthly_df,
                    x='month',
                    y='task_count',
                    title='Tasks per Month',
                    markers=True,
                    color_discrete_sequence=['green']
                )
                fig.update_layout(height=300, xaxis_title="Month", yaxis_title="Tasks")
                st.plotly_chart(fig, use_container_width=True)

    with tab4:
        st.subheader("📋 Export & Role Description Helper")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Role Summary Text")
            if st.button("📝 Generate Role Summary"):
                with st.spinner("Generating summary..."):
                    summary = analyzer.generate_role_summary(
                        start_date=start_date,
                        end_date=end_date,
                        top_n=20
                    )
                    st.text_area("Role Summary", summary, height=600)

                    # Download button
                    st.download_button(
                        label="📥 Download as Text",
                        data=summary,
                        file_name=f"personal_role_profile_{start_date}_to_{end_date}.txt",
                        mime="text/plain"
                    )

        with col2:
            st.markdown("### Excel Export")
            if st.button("📊 Export to Excel"):
                with st.spinner("Generating Excel report..."):
                    output_path = f"output/personal_role_profile_{start_date}_to_{end_date}.xlsx"
                    analyzer.export_to_excel(
                        start_date=start_date,
                        end_date=end_date,
                        output_file=output_path
                    )
                    st.success(f"✅ Excel report saved to: {output_path}")

                    # Read and provide download
                    with open(output_path, 'rb') as f:
                        st.download_button(
                            label="📥 Download Excel File",
                            data=f,
                            file_name=f"personal_role_profile_{start_date}_to_{end_date}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )

        # Quick insights
        st.divider()
        st.markdown("### Quick Insights for Role Description")

        if profile['keywords']:
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### Top 5 Focus Areas")
                top_5 = [kw['keyword'] for kw in profile['keywords'][:5]]
                for i, keyword in enumerate(top_5, 1):
                    st.markdown(f"{i}. **{keyword}**")

            with col2:
                st.markdown("#### Suggested Bullets")
                if len(profile['categories']) > 0:
                    top_cat = profile['categories'][0]['category']
                    top_pct = profile['categories'][0]['percentage']
                    st.markdown(f"• Primary work area: {top_cat} ({top_pct:.0f}%)")

                if len(profile['keywords']) >= 3:
                    top_3 = ', '.join([kw['keyword'] for kw in profile['keywords'][:3]])
                    st.markdown(f"• Key focus: {top_3}")

                st.markdown(f"• Worked across {profile['all_keywords_count']} different topics/projects")
                st.markdown(f"• Completed {profile['task_count']} tasks over {profile['total_hours']:.0f} hours")

# Footer
st.divider()
st.caption("👤 Personal Role Profile Dashboard | Built with Streamlit & Plotly")
