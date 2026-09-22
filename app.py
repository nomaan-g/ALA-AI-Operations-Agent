import streamlit as st
import pandas as pd
import os
import json
import requests
from dotenv import load_dotenv


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

API_KEY = os.getenv("AGIONE_API_KEY")

API_URL = "https://agione.pro/hyperone/xapi/api/v1/chat/completions"

MODEL = "deepseek/deepseek-v4-flash/02acd"


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="ALA AI Operations Agent",
    page_icon="🤖",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .subtitle {
        font-size: 17px;
        color: #9aa0aa;
        margin-bottom: 25px;
    }

    .section-title {
        font-size: 25px;
        font-weight: 650;
        margin-top: 25px;
        margin-bottom: 15px;
    }

    .agent-card {
        background: #151a21;
        border: 1px solid #303640;
        border-radius: 12px;
        padding: 22px;
        margin-top: 10px;
        margin-bottom: 20px;
    }

    .trace-card {
        background: #11161c;
        border: 1px solid #303640;
        border-radius: 10px;
        padding: 18px;
        margin-top: 10px;
    }

    .trace-success {
        margin: 8px 0;
        color: #6ee7a8;
    }

    .trace-active {
        margin: 8px 0;
        color: #64b5ff;
    }

    .trace-title {
        font-size: 18px;
        font-weight: 650;
        margin-bottom: 12px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🤖 ALA AI Operations Agent</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Intelligent supplier analysis, decision support and workflow automation'
    '</div>',
    unsafe_allow_html=True
)

st.divider()


# ============================================================
# LOAD SUPPLIER DATA
# ============================================================

df = pd.read_csv("ala_supplier_data.csv")


# ============================================================
# TOOL: SUPPLIER ANALYSIS
# ============================================================

def analyze_supplier_data():

    total_quantity = df["quantity_kg"].sum()

    weighted_average_price = (
        (df["quantity_kg"] * df["price_per_kg"]).sum()
        / total_quantity
    )

    average_quality = df["quality_percent"].mean()

    highest_volume = df.loc[
        df["quantity_kg"].idxmax()
    ]

    lowest_quality = df.loc[
        df["quality_percent"].idxmin()
    ]

    return {
        "total_quantity": int(total_quantity),

        "average_price": round(
            float(weighted_average_price), 2
        ),

        "average_quality": round(
            float(average_quality), 2
        ),

        "highest_volume_supplier":
            highest_volume["supplier"],

        "highest_volume_quantity":
            int(highest_volume["quantity_kg"]),

        "lowest_quality_supplier":
            lowest_quality["supplier"],

        "lowest_quality":
            int(lowest_quality["quality_percent"])
    }


# ============================================================
# AGENT: DECIDE WHICH TOOL TO USE
# ============================================================

def ask_agent(user_question):

    prompt = f"""
You are an AI operations agent.

The user asked:

"{user_question}"

You have access to the following tools.

1. analyze_supplier_data

Use this tool when the user asks about:

- supplier quantities
- supplier prices
- supplier quality
- supplier performance
- supplier analysis
- overall supplier information

2. calculate_total

Use this tool for mathematical calculations
involving quantity and price.

Decide which tool is required.

Respond with ONLY ONE of:

SUPPLIER_ANALYSIS

CALCULATOR

NO_TOOL
"""

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 100
    }

    response = requests.post(
        API_URL,
        headers=headers,
        json=data
    )

    if response.status_code != 200:
        return None, response.text

    result = response.json()

    decision = result[
        "choices"
    ][0]["message"]["content"].strip()

    return decision, None


# ============================================================
# AI: GENERATE FINAL MANAGEMENT SUMMARY
# ============================================================

def generate_ai_summary(
    user_question,
    tool_result
):

    prompt = f"""
You are an AI operations assistant.

The user asked:

"{user_question}"

The supplier analysis tool returned
the following verified data:

{json.dumps(tool_result, indent=2)}

Create a professional management summary.

Use these sections:

### Overall Situation

Give a concise overview.

### Key Observations

Mention the most important findings
from the verified data.

### Suppliers That May Warrant Review

Identify suppliers that deserve attention
based only on the available data.

### Suggested Areas for Investigation

Suggest useful areas for further analysis.

Important rules:

- Use only the provided data.
- Do not invent information.
- Do not assume company benchmarks.
- Do not make final procurement decisions.
- Clearly distinguish observations from recommendations.
- Keep the answer concise and professional.
"""

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 700
    }

    response = requests.post(
        API_URL,
        headers=headers,
        json=data
    )

    if response.status_code != 200:
        return None, response.text

    result = response.json()

    answer = result[
        "choices"
    ][0]["message"]["content"]

    return answer, None


# ============================================================
# USER QUESTION
# ============================================================

st.markdown(
    '<div class="section-title">Ask the AI Agent</div>',
    unsafe_allow_html=True
)

user_question = st.text_input(
    "What would you like to know?",
    value="Analyze the supplier data and give me a management summary",
    label_visibility="visible"
)


# ============================================================
# RUN AGENT
# ============================================================

run_agent = st.button(
    "🚀 Run AI Agent",
    type="primary"
)


if run_agent:

    if not API_KEY:

        st.error(
            "AGIONE_API_KEY was not found in .env"
        )

        st.stop()


    # ========================================================
    # AGENT EXECUTION TRACE
    # ========================================================

    st.markdown(
        '<div class="section-title">⚙️ Agent Execution</div>',
        unsafe_allow_html=True
    )

    with st.status(
        "AI Agent is executing...",
        expanded=True
    ) as status:

        st.write("✓ User request received")

        # ----------------------------------------------------
        # STEP 1: AGENT REASONING
        # ----------------------------------------------------

        st.write(
            "🧠 Sending request to DeepSeek through AGIOne..."
        )

        decision, error = ask_agent(
            user_question
        )

        if error:

            status.update(
                label="Agent execution failed",
                state="error"
            )

            st.error(error)

            st.stop()


        st.write(
            f"✓ Agent selected: **{decision}**"
        )


        # ----------------------------------------------------
        # STEP 2: TOOL EXECUTION
        # ----------------------------------------------------

        if "SUPPLIER_ANALYSIS" in decision:

            st.write(
                "🔧 Calling Supplier Analysis Tool..."
            )

            tool_result = analyze_supplier_data()

            st.write(
                "✓ Deterministic supplier calculations completed"
            )

            st.write(
                "✓ Verified tool results generated"
            )


            # ------------------------------------------------
            # STEP 3: SEND TOOL RESULT TO AI
            # ------------------------------------------------

            st.write(
                "🧠 Sending verified results to DeepSeek..."
            )

            ai_summary, error = generate_ai_summary(
                user_question,
                tool_result
            )

            if error:

                status.update(
                    label="AI interpretation failed",
                    state="error"
                )

                st.error(error)

                st.stop()


            st.write(
                "✓ Management summary generated"
            )


            status.update(
                label="Agent completed successfully",
                state="complete"
            )


        else:

            status.update(
                label="No supplier analysis tool required",
                state="complete"
            )

            tool_result = None
            ai_summary = None


    # ========================================================
    # RESULTS
    # ========================================================

    if tool_result:

        st.divider()

        # ====================================================
        # SUPPLIER OVERVIEW
        # ====================================================

        st.markdown(
            '<div class="section-title">📊 Supplier Overview</div>',
            unsafe_allow_html=True
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Total Material",
                f"{tool_result['total_quantity']:,} kg"
            )

        with col2:

            st.metric(
                "Average Purchase Price",
                f"${tool_result['average_price']:.2f}/kg"
            )

        with col3:

            st.metric(
                "Average Quality",
                f"{tool_result['average_quality']:.1f}%"
            )


        # ====================================================
        # SUPPLIER INSIGHTS
        # ====================================================

        st.divider()

        st.markdown(
            '<div class="section-title">'
            '🏭 Key Supplier Insights'
            '</div>',
            unsafe_allow_html=True
        )

        col1, col2 = st.columns(2)

        with col1:

            st.info(
                f"""
                **Highest Volume Supplier**

                ## {tool_result['highest_volume_supplier']}

                **{tool_result['highest_volume_quantity']:,} kg**

                Highest recorded supplier volume.
                """
            )

        with col2:

            st.warning(
                f"""
                **Lowest Quality Supplier**

                ## {tool_result['lowest_quality_supplier']}

                **{tool_result['lowest_quality']}% quality**

                May warrant further quality review.
                """
            )


        # ====================================================
        # SUPPLIER DATA
        # ====================================================

        st.divider()

        st.markdown(
            '<div class="section-title">📋 Supplier Data</div>',
            unsafe_allow_html=True
        )

        display_df = df.copy()

        display_df.columns = [
            "Supplier",
            "Material",
            "Quantity (kg)",
            "Price ($/kg)",
            "Quality (%)"
        ]

        st.dataframe(
            display_df,
            width="stretch",
            hide_index=True
        )


        # ====================================================
        # AI MANAGEMENT SUMMARY
        # ====================================================

        st.divider()

        st.markdown(
            '<div class="section-title">'
            '🤖 AI Management Summary'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="agent-card">',
            unsafe_allow_html=True
        )

        st.markdown(ai_summary)

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )


        # ====================================================
        # ARCHITECTURE
        # ====================================================

        st.divider()

        st.markdown(
            '<div class="section-title">'
            '🔄 Agent Workflow'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <div class="trace-card">

            <div class="trace-success">
            ✓ User Question
            </div>

            ↓

            <div class="trace-active">
            🧠 DeepSeek Agent Reasoning
            </div>

            ↓

            <div class="trace-active">
            🔧 Tool Selection
            </div>

            ↓

            <div class="trace-success">
            ✓ Supplier Analysis Tool
            </div>

            ↓

            <div class="trace-success">
            ✓ Deterministic Data Analysis
            </div>

            ↓

            <div class="trace-active">
            🧠 DeepSeek Interpretation
            </div>

            ↓

            <div class="trace-success">
            ✓ Management Insight
            </div>

            </div>
            """,
            unsafe_allow_html=True
        )