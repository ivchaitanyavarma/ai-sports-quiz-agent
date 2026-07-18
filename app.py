import streamlit as st
from src.generator import compiled_agent_graph
from src.config import get_logger

logger = get_logger("UI_App")

st.set_page_config(
    page_title="Enterprise AI Sports Quiz Agent", 
    page_icon="🏟️", 
    layout="centered"
)

def setup_session_state():
    """Protects active state metrics from standard browser refresh cycles."""
    if "active_quiz_batch" not in st.session_state:
        st.session_state.active_quiz_batch = None
    if "current_question_index" not in st.session_state:
        st.session_state.current_question_index = 0
    if "score" not in st.session_state:
        st.session_state.score = 0
    if "is_evaluated" not in st.session_state:
        st.session_state.is_evaluated = False

def trigger_graph_pipeline(selected_sport: str, chosen_difficulty: str):
    """Executes the deterministic state graph engine."""
    with st.spinner("Processing local graphs and running dynamic search indices to generate 10 questions..."):
        initial_state = {
            "topic": selected_sport,
            "difficulty": chosen_difficulty,
            "local_context": "",
            "web_context": "",
            "quiz_result": None,
            "system_errors": []
        }
        
        try:
            execution_response = compiled_agent_graph.invoke(initial_state)
            
            if execution_response.get("system_errors"):
                st.error(f"Pipeline Interruption: {execution_response['system_errors'][0]}")
                return
                
            # Load the batch of 10 questions into session state
            st.session_state.active_quiz_batch = execution_response.get("quiz_result")["questions"]
            st.session_state.current_question_index = 0
            st.session_state.score = 0
            st.session_state.is_evaluated = False
            logger.info("Successfully loaded graph results into memory parameters.")
        except Exception as e:
            logger.error(f"Critical execution block encountered: {e}", exc_info=True)
            st.error("Engine failed to resolve graph sequences completely.")

def main():
    setup_session_state()
    
    st.title("🏟️ AI Sports Quiz Agent")
    st.caption("Production Grade LangGraph Workflow leveraging Retrieval-Augmented Generation")
    
    with st.expander("📊 View Agent Knowledge Base Domains"):
        st.markdown("""
        **This agent is grounded on verified historic datasets and live web searches:**
        *   🏎️ **Formula 1:** Drivers' (1950–2025) & Constructors' Champions (1958–2025), plus 15 key records.
        *   ⚽ **Football:** World Cup (1930–2022), Euro (1960–2024), UEFA Champions League (1956–2026).
        *   🏏 **Cricket:** ODI (1975–2023) & T20 World Cups (2007–2026), World Test Championship (2021–2025).
        *   🏀 **Basketball:** NBA Finals (1947–2026), FIBA World Cup (1950–2023).
        """)

    layout_col_1, layout_col_2 = st.columns(2)
    with layout_col_1:
        sport_selection = st.selectbox("Target Sport", ["Formula 1", "Football", "Cricket", "Basketball"])
    with layout_col_2:
        difficulty_selection = st.select_slider("System Tier Level", options=["Easy", "Medium", "Hard"])
        
    if st.button("Generate 10-Question Quiz Challenge", type="primary", use_container_width=True):
        trigger_graph_pipeline(sport_selection, difficulty_selection)
        
    # --- Presentation Rendering for Batch Quiz ---
    if st.session_state.active_quiz_batch:
        batch = st.session_state.active_quiz_batch
        index = st.session_state.current_question_index
        
        # Check if quiz is finished
        if index >= len(batch):
            st.success(f"🎉 Quiz Complete! Your final score is {st.session_state.score} / 10.")
            if st.button("Start Over"):
                st.session_state.active_quiz_batch = None
                st.rerun()
            return

        current_quiz = batch[index]
        st.markdown("---")
        st.markdown(f"### Question {index + 1} of 10")
        st.subheader(current_quiz["question"])
        
        selected_option = st.radio(
            "Select the correct answer from the list below:",
            options=current_quiz["options"],
            index=None,
            key=f"quiz_interaction_{index}_{hash(current_quiz['question'])}"
        )
        
        if not st.session_state.is_evaluated:
            if st.button("Submit Answer Validation"):
                if not selected_option:
                    st.warning("Please make a selection before verifying metrics.")
                else:
                    st.session_state.is_evaluated = True
                    if selected_option == current_quiz["correct_answer"]:
                        st.session_state.score += 1
                    st.rerun()
        else:
            # Display results
            if selected_option == current_quiz["correct_answer"]:
                st.success("🎯 Elite Performance! Your answer matches our database record.")
            else:
                st.error(f"🚨 Incorrect Reference! True Value: '{current_quiz['correct_answer']}'")
                
            st.info(f"**Historical Context Verification:** {current_quiz['explanation']}")
            
            # Button to move to the next question
            if st.button("Next Question"):
                st.session_state.current_question_index += 1
                st.session_state.is_evaluated = False
                st.rerun()

if __name__ == "__main__":
    main()