import streamlit as st
import json
from main import sleep_prediction_pipeline

st.set_page_config(
    page_title="Sleep Analytics System",
    page_icon="🛌",
    layout="centered"
)

st.title("🛌 AI Sleep Analytics")
st.markdown("Upload your sleep data (JSON) and get AI-powered analysis.")

st.divider()

uploaded_file = st.file_uploader(
    "📂 Upload your Sleep Data JSON file",
    type=["json"],
    help="Drag and drop a JSON file here."
)

if uploaded_file is not None:
    try:
        sleep_data = json.load(uploaded_file)

        st.success("File uploaded successfully!")

        # Run AI Pipeline
        result = sleep_prediction_pipeline(sleep_data)

        st.divider()



        st.subheader("📊 Sleep Statistics")

        stats = result["statistics"]

        col1, col2 = st.columns(2)
        col1.metric("Average Sleep", stats["average_sleep"])
        col2.metric("Sleep Score", f"{stats['sleep_score_percent']}%")

        col3, col4 = st.columns(2)
        col3.metric("Minimum Sleep", stats["minimum_sleep"])
        col4.metric("Maximum Sleep", stats["maximum_sleep"])

        st.markdown(f"**Trend:** {stats['trend']['direction']} ({stats['trend']['change']})")
        st.markdown(f"**Pattern:** {stats['sleep_pattern']}")
        st.markdown(f"**Grade:** {stats['sleep_grade']}")

        st.divider()


        st.subheader("🤖 AI Analysis")

        ai_analysis = result["ai_analysis"]

        # Summary 
        st.subheader("1. Data-Based Summary")
        st.markdown(result["data_summary"])

        st.subheader("2. AI Analysis Summary")
        st.markdown(result["ai_analysis"]["summary"])

        st.subheader("3. Final Recommendation")
        st.markdown(result["final_recommendation"])


        st.divider()

    except json.JSONDecodeError:
        st.error("Invalid JSON format. Please upload a valid JSON file.")

    except Exception as e:
        st.error(f"Error during analysis: {str(e)}")
