
import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Page Configuration
st.set_page_config(
    page_title="Oscar Awards Analytics",
    page_icon="🏆",
    layout="wide"
)

st.title("🏆 Oscar Awards Analytics Dashboard")

st.write(
    "An interactive dashboard to explore Oscar nominees, "
    "winners, movie ratings, and award trends."
)

# Load Datasets
DATA_FILES = {
    "Acting": "oscardata_acting.csv",
    "Best Director": "oscardata_bestdirector.csv",
    "Best Picture": "oscardata_bestpicture.csv",
    "Acting 2021": "oscardata_2021_acting.csv",
    "Best Director 2021": "oscardata_2021_bestdirector.csv",
    "Best Picture 2021": "oscardata_2021_bestpicture.csv"
}

dataframes = []

for category, filename in DATA_FILES.items():

    if os.path.exists(filename):

        df = pd.read_csv(filename)
        df["Dataset"] = category
        dataframes.append(df)

if not dataframes:
    st.error("Dataset files not found!")
    st.stop()

data = pd.concat(dataframes, ignore_index=True, sort=False)

# Data Cleaning
for column in ["Year", "Rating_IMDB", "Rating_rtcritic", "Winner"]:

    if column in data.columns:
        data[column] = pd.to_numeric(data[column], errors="coerce")

# Sidebar Filters
st.sidebar.title("Dataset Filters")

datasets = st.sidebar.multiselect(
    "Select Dataset",
    data["Dataset"].unique(),
    default=list(data["Dataset"].unique())
)

filtered_data = data[data["Dataset"].isin(datasets)].copy()

# Category Filter
if "Category" in filtered_data.columns:

    categories = filtered_data["Category"].dropna().unique()

    selected_category = st.sidebar.multiselect(
        "Select Award Category",
        categories,
        default=list(categories)
    )

    filtered_data = filtered_data[
        filtered_data["Category"].isin(selected_category)
    ]

# Year Filter
if "Year" in filtered_data.columns and filtered_data["Year"].notna().any():

    min_year = int(filtered_data["Year"].min())
    max_year = int(filtered_data["Year"].max())

    if min_year < max_year:

        year_range = st.sidebar.slider(
            "Select Oscar Year",
            min_year,
            max_year,
            (min_year, max_year)
        )

        filtered_data = filtered_data[
            filtered_data["Year"].between(year_range[0], year_range[1])
        ]

# Winner Filter
if "Winner" in filtered_data.columns:

    winner_option = st.sidebar.selectbox(
        "Winner Status",
        ["All", "Winners Only", "Non-Winners Only"]
    )

    if winner_option == "Winners Only":
        filtered_data = filtered_data[filtered_data["Winner"] == 1]

    elif winner_option == "Non-Winners Only":
        filtered_data = filtered_data[filtered_data["Winner"] == 0]

# IMDb Rating Filter
if "Rating_IMDB" in filtered_data.columns and filtered_data["Rating_IMDB"].notna().any():

    rating_min = float(filtered_data["Rating_IMDB"].min())
    rating_max = float(filtered_data["Rating_IMDB"].max())

    if rating_min < rating_max:

        rating_range = st.sidebar.slider(
            "IMDb Rating",
            rating_min,
            rating_max,
            (rating_min, rating_max)
        )

        filtered_data = filtered_data[
            filtered_data["Rating_IMDB"].between(
                rating_range[0], rating_range[1]
            )
        ]

# KPI Dashboard
st.header("📊 Dashboard Overview")

total_records = len(filtered_data)

total_winners = (
    (filtered_data["Winner"] == 1).sum()
    if "Winner" in filtered_data.columns
    else 0
)

average_rating = (
    filtered_data["Rating_IMDB"].mean()
    if "Rating_IMDB" in filtered_data.columns
    else None
)

average_critic_rating = (
    filtered_data["Rating_rtcritic"].mean()
    if "Rating_rtcritic" in filtered_data.columns
    else None
)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Records", total_records)
col2.metric("Total Winners", int(total_winners))

col3.metric(
    "Average IMDb Rating",
    round(average_rating, 2) if pd.notna(average_rating) else "N/A"
)

col4.metric(
    "Average Critics Rating",
    round(average_critic_rating, 2)
    if pd.notna(average_critic_rating)
    else "N/A"
)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(
    ["Dataset Overview", "Data Analysis", "Visualizations", "Insights"]
)

# Dataset Overview
with tab1:

    st.subheader("Dataset Preview")

    st.dataframe(filtered_data.head(100), use_container_width=True)

    with st.expander("Dataset Information"):

        st.write("Dataset Shape:", filtered_data.shape)
        st.write("Column Information:")
        st.write(filtered_data.dtypes)

        st.write("Missing Values:")
        st.write(filtered_data.isnull().sum())

        st.write("Descriptive Statistics:")
        st.write(filtered_data.describe(include="all"))

# Data Analysis
with tab2:

    st.subheader("Category-wise Analysis")

    if "Category" in filtered_data.columns:

        category_summary = (
            filtered_data.groupby("Category")
            .size()
            .reset_index(name="Number of Records")
        )

        st.dataframe(category_summary, use_container_width=True)

    st.subheader("Top Rated Movies")

    if "Film" in filtered_data.columns and "Rating_IMDB" in filtered_data.columns:

        top_movies = (
            filtered_data.dropna(subset=["Rating_IMDB"])
            .sort_values("Rating_IMDB", ascending=False)
            .head(10)
        )

        st.dataframe(top_movies, use_container_width=True)

# Visualizations
with tab3:

    # Bar Chart
    st.subheader("Oscar Records by Category")

    if "Category" in filtered_data.columns:

        category_counts = (
            filtered_data.groupby("Category")
            .size()
            .reset_index(name="Count")
        )

        fig_bar = px.bar(
            category_counts,
            x="Category",
            y="Count",
            title="Oscar Records by Category",
            labels={
                "Category": "Award Category",
                "Count": "Number of Records"
            }
        )

        st.plotly_chart(fig_bar, use_container_width=True)

        st.write("Interpretation: This chart compares records across Oscar categories.")

    # Line Chart
    st.subheader("Oscar Records Across Years")

    if "Year" in filtered_data.columns and filtered_data["Year"].notna().any():

        yearly_data = (
            filtered_data.groupby("Year")
            .size()
            .reset_index(name="Count")
            .sort_values("Year")
        )

        fig_line = px.line(
            yearly_data,
            x="Year",
            y="Count",
            markers=True,
            title="Oscar Records Across Years",
            labels={
                "Year": "Oscar Year",
                "Count": "Number of Records"
            }
        )

        st.plotly_chart(fig_line, use_container_width=True)

        st.write("Interpretation: This chart shows Oscar records over time.")

    # Scatter Plot
    st.subheader("IMDb Rating vs Critics Rating")

    if (
        "Rating_IMDB" in filtered_data.columns
        and "Rating_rtcritic" in filtered_data.columns
    ):

        scatter_data = filtered_data.dropna(
            subset=["Rating_IMDB", "Rating_rtcritic"]
        )

        if not scatter_data.empty:

            fig_scatter = px.scatter(
                scatter_data,
                x="Rating_IMDB",
                y="Rating_rtcritic",
                color="Category" if "Category" in scatter_data.columns else None,
                title="IMDb Rating vs Critics Rating",
                labels={
                    "Rating_IMDB": "IMDb Rating",
                    "Rating_rtcritic": "Critics Rating"
                }
            )

            st.plotly_chart(fig_scatter, use_container_width=True)

            st.write("Interpretation: This chart compares IMDb and critics ratings.")

# Insights
with tab4:

    st.subheader("Key Insights")

    st.write(f"Total records: {len(filtered_data)}")
    st.write(f"Total Oscar winners: {int(total_winners)}")

    if "Category" in filtered_data.columns:

        category_counts = filtered_data["Category"].value_counts()

        if not category_counts.empty:

            st.write(
                f"Most represented category: {category_counts.index[0]}"
            )

    if "Rating_IMDB" in filtered_data.columns:

        if filtered_data["Rating_IMDB"].notna().any():

            highest_rating = filtered_data["Rating_IMDB"].max()

            st.write(f"Highest IMDb rating: {highest_rating}")

    st.success("Insights update dynamically based on the selected filters.")