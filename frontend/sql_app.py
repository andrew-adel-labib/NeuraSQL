# import streamlit as st
# import requests
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go
# import os

# BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# st.set_page_config(page_title="AI BI Assistant", layout="wide")

# st.title("📊 AI Business Intelligence Assistant")

# mode = st.sidebar.radio("Mode", ["Ask Question", "Forecast"])

# question = st.text_input("Ask your business question")

# viz_type = st.selectbox(
#     "Choose Visualization",
#     [
#         "Auto",
#         "Bar",
#         "Line",
#         "Pie",
#         "Combo",
#         "Waterfall",
#         "Stacked %",
#         "Multi-Line"
#     ]
# )


# def show_kpis(df):

#     numeric_cols = df.select_dtypes(include="number").columns

#     if len(numeric_cols) == 0:
#         return

#     cols = st.columns(min(4, len(numeric_cols)))

#     for i, col in enumerate(numeric_cols[:4]):
#         value = df[col].sum()
#         cols[i].metric(col, f"{value:,.2f}")


# def render_chart(df, chart_type):

#     if df.empty:
#         st.warning("No data available")
#         return

#     num_cols = df.select_dtypes(include="number").columns.tolist()
#     cat_cols = df.select_dtypes(exclude="number").columns.tolist()

#     if len(num_cols) == 0:
#         st.dataframe(df)
#         return

#     y = num_cols[0]
#     x = cat_cols[0] if cat_cols else df.columns[0]

#     st.subheader("📊 Visualization")


#     if chart_type == "Auto":

#         if "date" in x.lower():
#             fig = px.line(df, x=x, y=y, markers=True)

#         elif df[x].nunique() <= 8:
#             fig = px.pie(df, names=x, values=y)

#         else:
#             fig = px.bar(df, x=x, y=y)

#         st.plotly_chart(fig, use_container_width=True)

    
#     elif chart_type == "Bar":

#         fig = px.bar(df, x=x, y=y, text=y)
#         st.plotly_chart(fig, use_container_width=True)

    
#     elif chart_type == "Line":

#         fig = px.line(df, x=x, y=y, markers=True)
#         st.plotly_chart(fig, use_container_width=True)

    
#     elif chart_type == "Pie":

#         fig = px.pie(df, names=x, values=y)
#         st.plotly_chart(fig, use_container_width=True)

    
#     elif chart_type == "Combo" and len(num_cols) >= 2:

#         fig = go.Figure()

#         fig.add_bar(
#             x=df[x],
#             y=df[num_cols[0]],
#             name=num_cols[0]
#         )

#         fig.add_trace(
#             go.Scatter(
#                 x=df[x],
#                 y=df[num_cols[1]],
#                 name=num_cols[1],
#                 mode="lines+markers",
#                 yaxis="y2"
#             )
#         )

#         fig.update_layout(
#             yaxis2=dict(
#                 overlaying="y",
#                 side="right"
#             )
#         )

#         st.plotly_chart(fig, use_container_width=True)

    
#     elif chart_type == "Waterfall":

#         fig = go.Figure(go.Waterfall(
#             x=df[x],
#             y=df[y],
#             measure=["relative"] * len(df)
#         ))

#         st.plotly_chart(fig, use_container_width=True)

    
#     elif chart_type == "Stacked %" and len(num_cols) >= 2:

#         df_pct = df.copy()
#         total = df[num_cols].sum(axis=1)

#         for col in num_cols[:2]:
#             df_pct[col] = df[col] / total * 100

#         fig = px.bar(
#             df_pct,
#             x=x,
#             y=num_cols[:2],
#             barmode="stack"
#         )

#         st.plotly_chart(fig, use_container_width=True)

    
#     elif chart_type == "Multi-Line" and len(num_cols) >= 2:

#         fig = px.line(
#             df,
#             x=x,
#             y=num_cols[:2],
#             markers=True
#         )

#         st.plotly_chart(fig, use_container_width=True)

#     else:
#         st.info("Not enough numeric columns for selected chart")



# if st.button("Run"):

#     if not question:
#         st.warning("Enter question")
#         st.stop()

    
#     if mode == "Ask Question":

#         res = requests.post(
#             f"{BACKEND_URL}/ask",
#             json={"question": question},
#             timeout=180
#         )

#         if res.status_code != 200:
#             st.error(res.text)
#             st.stop()

#         data = res.json()
#         df = pd.DataFrame(data["rows"])

#         st.subheader("💡 Answer")
#         st.write(data["answer"])

#         show_kpis(df)

#         render_chart(df, viz_type)

#         st.subheader("📄 Data")
#         st.dataframe(df)

#         with st.expander("SQL Query"):
#             st.code(data["sql"], language="sql")

    
#     else:

#         res = requests.post(
#             f"{BACKEND_URL}/predict",
#             json={"question": question},
#             timeout=240
#         )

#         if res.status_code != 200:
#             st.error(res.text)
#             st.stop()

#         data = res.json()
#         forecast_df = pd.DataFrame(data["forecast"])

#         st.subheader("📈 Forecast Explanation")
#         st.write(data["explanation"])

#         if "Date" in forecast_df.columns:
#             forecast_df["Date"] = pd.to_datetime(forecast_df["Date"])

#         fig = px.line(
#             forecast_df,
#             x="Date",
#             y="Forecast",
#             markers=True
#         )

#         st.plotly_chart(fig, use_container_width=True)

#         st.dataframe(forecast_df)


#Power BI

# import streamlit as st
# import requests
# import pandas as pd
# import os
# from dotenv import load_dotenv

# load_dotenv()

# BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# # Power BI embed URL
# POWERBI_EMBED_URL = os.getenv("POWERBI_EMBED_URL")

# st.set_page_config(page_title="AI BI Assistant", layout="wide")

# st.title("📊 AI Business Intelligence Assistant")

# mode = st.sidebar.radio("Mode", ["Ask Question", "Forecast"])

# question = st.text_input("Ask your business question")


# # =============================
# # KPI CARDS
# # =============================
# def show_kpis(df):

#     numeric_cols = df.select_dtypes(include="number").columns

#     if len(numeric_cols) == 0:
#         return

#     cols = st.columns(min(4, len(numeric_cols)))

#     for i, col in enumerate(numeric_cols[:4]):
#         value = df[col].sum()
#         cols[i].metric(col, f"{value:,.2f}")


# # =============================
# # RUN BUTTON
# # =============================
# if st.button("Run"):

#     if not question:
#         st.warning("Enter question")
#         st.stop()

#     # =============================
#     # ASK QUESTION MODE
#     # =============================
#     if mode == "Ask Question":

#         res = requests.post(
#             f"{BACKEND_URL}/ask",
#             json={"question": question},
#             timeout=180
#         )

#         if res.status_code != 200:
#             st.error(res.text)
#             st.stop()

#         data = res.json()

#         df = pd.DataFrame(data["rows"])

#         st.subheader("💡 Answer")
#         st.write(data["answer"])

#         show_kpis(df)

#         st.subheader("📄 Data")
#         st.dataframe(df)

#         with st.expander("SQL Query"):
#             st.code(data["sql"], language="sql")

#         # =============================
#         # POWER BI DASHBOARD
#         # =============================
#         st.subheader("📊 Power BI Visualization")

#         if POWERBI_EMBED_URL:
#             st.components.v1.iframe(
#                 POWERBI_EMBED_URL,
#                 height=700
#             )
#         else:
#             st.warning("Power BI embed URL not configured")


#     # =============================
#     # FORECAST MODE
#     # =============================
#     else:

#         res = requests.post(
#             f"{BACKEND_URL}/predict",
#             json={"question": question},
#             timeout=240
#         )

#         if res.status_code != 200:
#             st.error(res.text)
#             st.stop()

#         data = res.json()

#         forecast_df = pd.DataFrame(data["forecast"])

#         st.subheader("📈 Forecast Explanation")
#         st.write(data["explanation"])

#         st.dataframe(forecast_df)

#         st.subheader("📊 Forecast Visualization")

#         if POWERBI_EMBED_URL:
#             st.components.v1.iframe(
#                 POWERBI_EMBED_URL,
#                 height=700
#             )
#         else:
#             st.warning("Power BI embed URL not configured")

#Altair

import streamlit as st
import requests
import pandas as pd
import altair as alt
import os
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="AI BI Assistant", layout="wide")

st.title("📊 ChatSQL Assistant")

mode = st.sidebar.radio("Mode", ["Ask Question", "Forecast"])

question = st.text_input("Ask your business question")

chart_type = st.selectbox(
    "Choose Visualization",
    [
        "Auto",
        "Bar",
        "Line",
        "Pie",
        "Scatter",
        "Stacked Bar",
        "Histogram",
        "Heatmap",
        "Area"
    ]
)


# ===============================
# KPI CARDS
# ===============================
def show_kpis(df):

    numeric_cols = df.select_dtypes(include="number").columns

    if len(numeric_cols) == 0:
        return

    cols = st.columns(min(4, len(numeric_cols)))

    for i, col in enumerate(numeric_cols[:4]):
        value = df[col].sum()
        cols[i].metric(col, f"{value:,.2f}")


# ===============================
# SMART VISUALIZATION ENGINE
# ===============================
def render_chart(df, chart_choice):

    if df.empty:
        st.warning("No data available")
        return

    # Clean columns
    df = df.copy()
    df.columns = [
        f"col_{i}" if c is None or str(c).strip() == "" else str(c).strip()
        for i, c in enumerate(df.columns)
    ]

    df = df.dropna(axis=1, how="all")

    # Detect column types
    num_cols = df.select_dtypes(include="number").columns.tolist()
    date_cols = df.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist()
    cat_cols = df.select_dtypes(exclude=["number", "datetime"]).columns.tolist()

    # Detect date-like strings
    for c in df.columns:
        if "date" in c.lower() or "time" in c.lower():
            try:
                df[c] = pd.to_datetime(df[c])
                date_cols.append(c)
            except:
                pass

    st.subheader("📊 Visualization")

    # ===============================
    # AUTO MODE
    # ===============================
    if chart_choice == "Auto":

        if len(date_cols) > 0 and len(num_cols) > 0:
            chart_choice = "Line"

        elif len(cat_cols) > 0 and len(num_cols) > 0 and df[cat_cols[0]].nunique() <= 8:
            chart_choice = "Pie"

        elif len(num_cols) >= 2:
            chart_choice = "Scatter"

        else:
            chart_choice = "Bar"

    # ===============================
    # BAR
    # ===============================
    if chart_choice == "Bar" and len(num_cols) > 0:

        x = cat_cols[0] if cat_cols else df.columns[0]
        y = num_cols[0]

        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X(x, sort="-y"),
            y=y,
            tooltip=list(df.columns)
        )

    # ===============================
    # LINE
    # ===============================
    elif chart_choice == "Line" and len(num_cols) > 0:

        x = date_cols[0] if date_cols else df.columns[0]
        y = num_cols[0]

        chart = alt.Chart(df).mark_line(point=True).encode(
            x=x,
            y=y,
            tooltip=list(df.columns)
        )

    # ===============================
    # PIE
    # ===============================
    elif chart_choice == "Pie" and len(cat_cols) > 0:

        x = cat_cols[0]
        y = num_cols[0] if num_cols else None

        chart = alt.Chart(df).mark_arc().encode(
            theta=y,
            color=x,
            tooltip=list(df.columns)
        )

    # ===============================
    # SCATTER
    # ===============================
    elif chart_choice == "Scatter" and len(num_cols) >= 2:

        chart = alt.Chart(df).mark_circle(size=80).encode(
            x=num_cols[0],
            y=num_cols[1],
            tooltip=list(df.columns)
        )

    # ===============================
    # STACKED BAR
    # ===============================
    elif chart_choice == "Stacked Bar" and len(num_cols) >= 2 and len(cat_cols) > 0:

        x = cat_cols[0]

        melted = df.melt(
            id_vars=[x],
            value_vars=num_cols[:2],
            var_name="Metric",
            value_name="Value"
        )

        chart = alt.Chart(melted).mark_bar().encode(
            x=x,
            y="Value",
            color="Metric",
            tooltip=[x, "Metric", "Value"]
        )

    # ===============================
    # HISTOGRAM
    # ===============================
    elif chart_choice == "Histogram" and len(num_cols) > 0:

        y = num_cols[0]

        chart = alt.Chart(df).mark_bar().encode(
            alt.X(f"{y}:Q", bin=True),
            y="count()",
            tooltip=[y]
        )

    # ===============================
    # HEATMAP
    # ===============================
    elif chart_choice == "Heatmap" and len(num_cols) >= 2:

        corr = df[num_cols].corr().reset_index().melt(id_vars="index")

        chart = alt.Chart(corr).mark_rect().encode(
            x="index",
            y="variable",
            color="value",
            tooltip=["index", "variable", "value"]
        )

    # ===============================
    # AREA
    # ===============================
    elif chart_choice == "Area" and len(num_cols) > 0:

        x = date_cols[0] if date_cols else df.columns[0]
        y = num_cols[0]

        chart = alt.Chart(df).mark_area().encode(
            x=x,
            y=y,
            tooltip=list(df.columns)
        )

    else:
        st.warning("Selected chart type not compatible with data.")
        return

    st.altair_chart(chart.interactive(), use_container_width=True)


# ===============================
# FORECAST VISUALIZATION
# ===============================
def render_forecast_chart(df):

    if df.empty:
        st.warning("No forecast data available")
        return

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"])

    chart = alt.Chart(df).mark_line(point=True).encode(
        x="Date:T",
        y="Forecast:Q",
        tooltip=["Date", "Forecast"]
    )

    st.altair_chart(chart.interactive(), use_container_width=True)


# ===============================
# RUN BUTTON
# ===============================
if st.button("Run"):

    if not question:
        st.warning("Enter question")
        st.stop()

    # ===============================
    # ASK QUESTION
    # ===============================
    if mode == "Ask Question":

        res = requests.post(
            f"{BACKEND_URL}/ask",
            json={"question": question},
            timeout=180
        )

        if res.status_code != 200:
            st.error(res.text)
            st.stop()

        data = res.json()

        df = pd.DataFrame(data["rows"])

        st.subheader("💡 Answer")
        st.write(data["answer"])

        show_kpis(df)

        render_chart(df, chart_type)

        st.subheader("📄 Data")
        st.dataframe(df)

        with st.expander("SQL Query"):
            st.code(data["sql"], language="sql")

    # ===============================
    # FORECAST
    # ===============================
    else:

        res = requests.post(
            f"{BACKEND_URL}/predict",
            json={"question": question},
            timeout=240
        )

        if res.status_code != 200:
            st.error(res.text)
            st.stop()

        data = res.json()

        forecast_df = pd.DataFrame(data["forecast"])

        st.subheader("📈 Forecast Explanation")
        st.write(data["explanation"])

        render_forecast_chart(forecast_df)

        st.subheader("📄 Forecast Data")
        st.dataframe(forecast_df)