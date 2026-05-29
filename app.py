import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# =========================================
# PAGE CONFIGURATION
# =========================================

st.set_page_config(
    page_title="NHL Analytics Dashboard",
    layout="wide"
)

# =========================================
# CUSTOM CSS
# =========================================

st.markdown("""
<style>

.main {
    background-color: #F5F7FA;
}

h1 {
    color: #111827;
    text-align: center;
    font-size: 42px;
}

h2, h3 {
    color: #1F2937;
}

[data-testid="metric-container"] {
    background-color: white;
    border: 1px solid #E5E7EB;
    padding: 15px;
    border-radius: 15px;
    box-shadow: 2px 2px 10px rgba(0,0,0,0.08);
}

</style>
""", unsafe_allow_html=True)

# =========================================
# LOAD DATA
# =========================================

uploaded_file = st.sidebar.file_uploader(
    "Upload CSV File",
    type=["csv"]
)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

else:
    df = pd.read_csv("data/skaters.csv")

# =========================================
# TITLE
# =========================================

st.markdown("""
<h1>NHL Analytics Dashboard</h1>
""", unsafe_allow_html=True)

st.markdown("""
<div style='text-align:center; font-size:18px; color:gray;'>
Interactive dashboard for NHL player and team performance analysis
</div>
""", unsafe_allow_html=True)

st.success("Dashboard Loaded Successfully")

st.markdown("---")

# =========================================
# KPI CARDS
# =========================================

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Players", df["name"].nunique())

col2.metric("Total Teams", df["team"].nunique())

if "I_F_goals" in df.columns:
    col3.metric(
        "Average Goals",
        round(df["I_F_goals"].mean(), 2)
    )

    col4.metric(
        "Highest Goals",
        int(df["I_F_goals"].max())
    )

st.markdown("""
Dashboard KPIs provide an overview of player performance,
team participation, and scoring statistics.
""")

# =========================================
# SIDEBAR FILTERS
# =========================================

st.sidebar.header("Dashboard Filters")

selected_team = st.sidebar.multiselect(
    "Select Team",
    options=df["team"].unique(),
    default=df["team"].unique()
)

selected_position = st.sidebar.multiselect(
    "Select Position",
    options=df["position"].unique(),
    default=df["position"].unique()
)

selected_season = st.sidebar.multiselect(
    "Select Season",
    options=sorted(df["season"].unique()),
    default=sorted(df["season"].unique())
)

goal_range = st.sidebar.slider(
    "Goals Range",
    int(df["I_F_goals"].min()),
    int(df["I_F_goals"].max()),
    (
        int(df["I_F_goals"].min()),
        int(df["I_F_goals"].max())
    )
)

# =========================================
# SEARCH BOX
# =========================================

player_search = st.sidebar.text_input(
    "Search Player Name or Player ID"
)

st.sidebar.markdown("---")

st.sidebar.info("""
NHL Analytics Dashboard

Technologies Used:
- Python
- Pandas
- Streamlit
- Matplotlib
- Seaborn
""")

# =========================================
# FILTER DATA
# =========================================

filtered_df = df[
    (df["team"].isin(selected_team)) &
    (df["position"].isin(selected_position)) &
    (df["season"].isin(selected_season)) &
    (df["I_F_goals"] >= goal_range[0]) &
    (df["I_F_goals"] <= goal_range[1])
]

# =========================================
# PLAYER SEARCH FILTER
# =========================================

if player_search:

    filtered_df = filtered_df[
        filtered_df["name"].astype(str).str.contains(
            player_search,
            case=False,
            na=False
        )
        |
        filtered_df["playerId"].astype(str).str.contains(
            player_search,
            case=False,
            na=False
        )
    ]

# =========================================
# DATASET OVERVIEW
# =========================================

st.header("Dataset Overview")

with st.expander("View Dataset"):

    st.dataframe(filtered_df.head(10))

# =========================================
# FIRST ROW OF CHARTS
# =========================================

col1, col2 = st.columns(2)

# =========================================
# TOP GOAL SCORERS
# =========================================

with col1:

    st.subheader("Top Goal Scorers")

    top_players = filtered_df.groupby("name")["I_F_goals"] \
                             .sum() \
                             .sort_values(ascending=False) \
                             .head(10)

    fig, ax = plt.subplots(figsize=(7,5))

    top_players.plot(kind='bar', ax=ax)

    ax.set_title("Top 10 Goal Scorers")
    ax.set_xlabel("Player")
    ax.set_ylabel("Goals")

    st.pyplot(fig)

    st.info(f"""
Top scoring players based on selected filters.

Highest Goals: {top_players.max()}
Players Displayed: {len(top_players)}
""")

# =========================================
# SHOTS VS GOALS
# =========================================

with col2:

    st.subheader("Shots vs Goals")

    fig, ax = plt.subplots(figsize=(7,5))

    sns.scatterplot(
        data=filtered_df,
        x="I_F_shotsOnGoal",
        y="I_F_goals",
        ax=ax
    )

    ax.set_title("Shots vs Goals")

    st.pyplot(fig)

    total_goals = filtered_df['I_F_goals'].sum()

total_shots = filtered_df['I_F_shotsOnGoal'].sum()

if total_shots > 0:
    goal_probability = (total_goals / total_shots) * 100
else:
    goal_probability = 0

st.info(f"""
Strong relationship between shots and goals.

Max Goals: {filtered_df['I_F_goals'].max()}
Max Shots: {filtered_df['I_F_shotsOnGoal'].max()}

Goal Scoring Efficiency: {goal_probability:.2f}%
""")

# =========================================
# SECOND ROW OF CHARTS
# =========================================

col1, col2 = st.columns(2)

# =========================================
# HEATMAP
# =========================================

with col1:

    st.subheader("Correlation Heatmap")

    selected = filtered_df[[
        "I_F_goals",
        "I_F_points",
        "I_F_shotsOnGoal",
        "I_F_hits",
        "gameScore",
        "games_played"
    ]]

    corr = selected.corr()

    fig, ax = plt.subplots(figsize=(7,5))

    sns.heatmap(
        corr,
        annot=True,
        cmap="coolwarm",
        ax=ax
    )

    st.pyplot(fig)

    st.info("""
Heatmap shows relationships between numerical variables.

Higher values indicate stronger correlations.
""")

# =========================================
# POSITION DISTRIBUTION
# =========================================

with col2:

    st.subheader("Position Distribution")

    position_counts = filtered_df["position"].value_counts()

    fig, ax = plt.subplots(figsize=(7,5))

    position_counts.plot.pie(
        autopct='%1.1f%%',
        ax=ax
    )

    ax.set_ylabel("")

    st.pyplot(fig)

    st.info(f"""
Distribution of player positions in dataset.

Total Positions: {filtered_df['position'].nunique()}
""")

# =========================================
# THIRD ROW OF CHARTS
# =========================================

col1, col2 = st.columns(2)

# =========================================
# TOP TEAMS
# =========================================

with col1:

    st.subheader("Top Teams by Points")

    top_teams = filtered_df.groupby("team")["I_F_points"] \
                           .sum() \
                           .sort_values(ascending=False) \
                           .head(10)

    fig, ax = plt.subplots(figsize=(7,5))

    top_teams.plot(kind='bar', ax=ax)

    ax.set_title("Top Teams by Points")

    st.pyplot(fig)

    st.info(f"""
Top NHL teams based on total points.

Highest Team Points: {top_teams.max()}
""")

# =========================================
# GOALS DISTRIBUTION
# =========================================

with col2:

    st.subheader("Goals Distribution")

    fig, ax = plt.subplots(figsize=(7,5))

    sns.histplot(
        filtered_df["I_F_goals"],
        bins=20,
        kde=True,
        ax=ax
    )

    ax.set_title("Goals Distribution")

    st.pyplot(fig)

    st.info(f"""
Distribution of goals scored by players.

Average Goals: {round(filtered_df['I_F_goals'].mean(), 2)}
""")

# =========================================
# FINAL CHART
# =========================================

st.subheader("Goals by Position")

fig, ax = plt.subplots(figsize=(10,5))

sns.boxplot(
    data=filtered_df,
    x="position",
    y="I_F_goals",
    ax=ax
)

ax.set_title("Goals by Position")

st.pyplot(fig)

st.info(f"""
Goal comparison across player positions.

Highest Goals: {filtered_df['I_F_goals'].max()}
""")

# =========================================
# DOWNLOAD BUTTON
# =========================================

csv = filtered_df.to_csv(index=False).encode('utf-8')

st.download_button(
    label="Download Filtered Data",
    data=csv,
    file_name='filtered_nhl_data.csv',
    mime='text/csv'
)

# =========================================
# FOOTER
# =========================================

st.markdown("---")

st.caption("Developed by Syed Faran Ali | Data Visualization & Dashboard Project")