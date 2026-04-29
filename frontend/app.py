import streamlit as st
import requests
import pandas as pd
import json
import os


BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://localhost:8000"
)

st.set_page_config(
    layout="wide",
    page_title="AI BI Copilot"
)


st.title("AI BI Copilot")

st.markdown("""
Enterprise-grade BI semantic intelligence:
- Multi-LLM benchmarking (Claude / OpenAI / Groq)
- Query rewriting
- Semantic planning
- Dimension correction
- DAX generation
- Validation
- Evaluation
- LLM-as-Judge
- Power BI embedding
""")


model_choice = st.radio(
    "Select LLM Provider",
    ["claude", "openai", "groq"],
    horizontal=True
)


question = st.text_input(
    "Ask your business question"
)


if st.button("Run"):

    if not question:
        st.warning(
            "Enter question"
        )
        st.stop()

    with st.spinner(
        f"Running enterprise BI pipeline using {model_choice.upper()}..."
    ):

        res = requests.post(
            f"{BACKEND_URL}/ask",
            json={
                "question": question,
                "model_provider": model_choice
            },
            timeout=300
        )

    if res.status_code != 200:
        st.error(
            res.text
        )
        st.stop()

    data = res.json()

    df = pd.DataFrame(
        data.get(
            "rows",
            []
        )
    )

    st.subheader(
        "🧠 Active LLM Provider"
    )

    st.success(
        f"Using: {data.get('model_provider', model_choice).upper()}"
    )

    st.subheader(
        "📌 Executive Summary"
    )

    st.info(
        data.get(
            "summary",
            "No summary available."
        )
    )

    st.subheader(
        "📊 Data Preview"
    )

    if not df.empty:
        st.dataframe(
            df,
            use_container_width=True
        )
    else:
        st.warning(
            "No rows returned."
        )

    if data.get(
        "execution_error"
    ):
        st.error(
            "DAX Execution Error:\n\n" +
            data[
                "execution_error"
            ]
        )

    st.subheader(
        "🧠 Semantic Pipeline"
    )

    col1, col2 = st.columns(2)

    with col1:

        with st.expander(
            "Rewritten Query"
        ):
            st.write(
                data.get(
                    "rewritten_query",
                    ""
                )
            )

        with st.expander(
            "Query Intent"
        ):
            st.json(
                data.get(
                    "query_intent",
                    {}
                )
            )

        with st.expander(
            "Dimension Plan"
        ):
            st.json(
                data.get(
                    "dimension_plan",
                    {}
                )
            )

    with col2:

        with st.expander(
            "Semantic Plan"
        ):
            st.json(
                data.get(
                    "semantic_plan",
                    {}
                )
            )

        with st.expander(
            "Generated DAX"
        ):
            st.code(
                data.get(
                    "dax",
                    ""
                ),
                language="sql"
            )

        validation = data.get(
            "validation",
            {}
        )

        if not validation.get(
            "valid",
            True
        ):
            st.error(
                "DAX Validation Failed:\n" +
                "\n".join(
                    validation.get(
                        "errors",
                        []
                    )
                )
            )

    st.subheader(
        "📈 Pipeline Evaluation"
    )

    evaluation = data.get(
        "evaluation",
        {}
    )

    metric1, metric2, metric3 = st.columns(3)

    metric1.metric(
        "Confidence",
        f"{evaluation.get('confidence', 0) * 100:.0f}%"
    )

    metric2.metric(
        "Quality",
        evaluation.get(
            "quality",
            "Unknown"
        )
    )

    metric3.metric(
        "Complexity",
        evaluation.get(
            "complexity_score",
            0
        )
    )

    with st.expander(
        "Evaluation Breakdown"
    ):
        st.json(
            evaluation
        )

    st.subheader(
        "🤖 LLM-as-Judge"
    )

    judge = data.get(
        "llm_judge",
        {}
    )

    judge_col1, judge_col2 = st.columns(2)

    judge_col1.metric(
        "Overall Score",
        f"{judge.get('overall_score', 0) * 100:.0f}%"
    )

    judge_col2.metric(
        "Summary Quality",
        f"{judge.get('summary_quality', 0) * 100:.0f}%"
    )

    st.success(
        judge.get(
            "final_verdict",
            "No verdict."
        )
    )

    with st.expander(
        "LLM Judge Full Review"
    ):
        st.json(
            judge
        )

    if evaluation.get(
        "recommendations"
    ):

        st.subheader(
            "🛠 Optimization Recommendations"
        )

        for rec in evaluation[
            "recommendations"
        ]:
            st.write(
                f"- {rec}"
            )

    embed = data.get(
        "powerbi"
    )

    if (
        embed
        and embed.get(
            "accessToken"
        )
    ):

        html = f"""
        <div id="reportContainer" style="height:800px;"></div>

        <script src="https://cdn.jsdelivr.net/npm/powerbi-client/dist/powerbi.js"></script>

        <script>
        var models = window['powerbi-client'].models;

        var config = {{
            type: 'report',
            embedUrl: "{embed['embedUrl']}",
            accessToken: "{embed['accessToken']}",
            tokenType: models.TokenType.Embed,

            settings: {{
                panes: {{
                    filters: {{ visible: false }},
                    pageNavigation: {{ visible: true }}
                }}
            }},

            filters: {json.dumps(embed['filters'])}
        }};

        var container = document.getElementById(
            'reportContainer'
        );

        powerbi.embed(
            container,
            config
        );
        </script>
        """

        st.subheader(
            "📈 Power BI Embedded Dashboard"
        )

        st.components.v1.html(
            html,
            height=850
        )

    else:
        st.warning(
            "Power BI embedding unavailable."
        )