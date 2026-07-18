import streamlit as st
import random
from src.generator import compiled_agent_graph
from src.config import get_logger

logger = get_logger("UI_App")

st.set_page_config(
    page_title="Enterprise AI Sports Quiz Agent", 
    page_icon="🏟️", 
    layout="wide"
)

# --- Dynamic Message Pools ---
SPINNER_MESSAGES = [
    "Processing local graphs and running dynamic search indices...",
    "Consulting the historical sports archives and live web sources...",
    "Fusing local vector data with real-time web search trends...",
    "Compiling your custom sports challenge..."
]

SUCCESS_MESSAGES = [
    "🎯 **Elite Performance!** Your answer perfectly matches our database.",
    "✅ **Spot on!** That is the correct answer.",
    "🏆 **Nailed it!** Outstanding sports knowledge.",
    "🔥 **Correct!** You really know your sports history."
]

ERROR_PREFIXES = [
    "🚨 **Incorrect Reference!**",
    "❌ **Not quite!**",
    "⚠️ **Missed that one!**",
    "🛑 **Tough luck!**"
]

COMPLETION_PREFIXES = [
    "🎉 Quiz Complete!",
    "🏆 Challenge Finished!",
    "🏁 That's a wrap!"
]

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
    if "selected_answer" not in st.session_state:
        st.session_state.selected_answer = None
    if "has_celebrated" not in st.session_state:
        st.session_state.has_celebrated = False
    if "feedback_message" not in st.session_state:
        st.session_state.feedback_message = ""
    if "completion_message" not in st.session_state:
        st.session_state.completion_message = ""

def trigger_graph_pipeline(selected_sport: str, chosen_difficulty: str):
    """Executes the deterministic state graph engine."""
    with st.spinner(random.choice(SPINNER_MESSAGES)):
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
                
            st.session_state.active_quiz_batch = execution_response.get("quiz_result")["questions"]
            st.session_state.current_question_index = 0
            st.session_state.score = 0
            st.session_state.is_evaluated = False
            st.session_state.selected_answer = None
            st.session_state.has_celebrated = False
            st.session_state.feedback_message = ""
            st.session_state.completion_message = ""
            logger.info("Successfully loaded graph results into memory parameters.")
        except Exception as e:
            logger.error(f"Critical execution block encountered: {e}", exc_info=True)
            st.error("Engine failed to resolve graph sequences completely.")

def main():
    setup_session_state()
    
    st.title("🏟️ AI Sports Quiz Agent")
    
    # --- Sidebar Configuration Controls ---
    with st.sidebar:
        st.header("🔧 Quiz Configurations")
        sport_selection = st.selectbox(
            "Target Sport", 
            ["Formula 1", "Football", "Cricket", "Basketball", "Tennis", "Athletics"] # <-- Added Tennis and Athletics
        )
        difficulty_selection = st.select_slider(
            "System Tier Level", 
            options=["Easy", "Medium", "Hard"]
        )
        
        st.markdown("---")
        if st.button("Generate Quiz", type="primary", use_container_width=True):
            trigger_graph_pipeline(sport_selection, difficulty_selection)
            st.rerun()

    # --- Persistent Quiz Rendering from Session State ---
    if st.session_state.active_quiz_batch:
        batch = st.session_state.active_quiz_batch
        index = st.session_state.current_question_index
        
        # End of Quiz State
        if index >= len(batch):
            if not st.session_state.has_celebrated:
                # FIX: Only trigger balloons if score is 7 or higher
                if st.session_state.score >= 7:
                    st.balloons()
                st.session_state.has_celebrated = True
                # Lock in the completion message variation
                st.session_state.completion_message = random.choice(COMPLETION_PREFIXES)
                
            st.success(f"{st.session_state.completion_message} Your final score is {st.session_state.score} / {len(batch)}.")
            
            if st.button("Start Over", use_container_width=True):
                st.session_state.active_quiz_batch = None
                st.session_state.current_question_index = 0
                st.session_state.score = 0
                st.session_state.is_evaluated = False
                st.session_state.has_celebrated = False
                st.rerun()
            return

        current_quiz = batch[index]
        
        st.subheader(f"Question {index + 1} of {len(batch)}")
        st.progress((index) / len(batch))
        st.markdown(f"#### {current_quiz['question']}")
        
        user_choice = st.radio(
            "Select your option:",
            options=current_quiz["options"],
            index=None if st.session_state.selected_answer is None else current_quiz["options"].index(st.session_state.selected_answer),
            disabled=st.session_state.is_evaluated,
            key=f"radio_q_{index}"
        )
        
        if user_choice:
            st.session_state.selected_answer = user_choice

        st.markdown("---")

        if not st.session_state.is_evaluated:
            if st.button("Submit Answer Validation", use_container_width=True):
                if not st.session_state.selected_answer:
                    st.warning("Please make a selection before verifying metrics.")
                else:
                    st.session_state.is_evaluated = True
                    # Lock in the dynamic feedback message based on the answer
                    if st.session_state.selected_answer == current_quiz["correct_answer"]:
                        st.session_state.score += 1
                        st.session_state.feedback_message = random.choice(SUCCESS_MESSAGES)
                    else:
                        prefix = random.choice(ERROR_PREFIXES)
                        st.session_state.feedback_message = f"{prefix} Correct Answer: `{current_quiz['correct_answer']}`"
                    st.rerun()
        else:
            # Display the locked feedback message
            if st.session_state.selected_answer == current_quiz["correct_answer"]:
                st.success(st.session_state.feedback_message)
            else:
                st.error(st.session_state.feedback_message)
                
            st.info(f"**Historical Context Verification:**\n\n{current_quiz['explanation']}")
            
            if st.button("Next Question ➡️", use_container_width=True):
                st.session_state.current_question_index += 1
                st.session_state.is_evaluated = False
                st.session_state.selected_answer = None
                st.session_state.feedback_message = ""
                st.rerun()
                
    else:
        st.info("👈 Select your sport and preferred difficulty tier in the sidebar pane to generate your custom quiz batch.")
        
        with st.expander("📊 View Agent Knowledge Base Domains", expanded=True):
            st.markdown("""
            This agent is fully grounded on verified historic datasets coupled with real-time web execution vectors:
            *   🏎️ **Formula 1:** Drivers' (1950–2025) & Constructors' Champions (1958–2025), plus key records.
            *   ⚽ **Football:** World Cup (1930–2022), Euro (1960–2024), UEFA Champions League (1956–2026).
            *   🏏 **Cricket:** ODI (1975–2023) & T20 World Cups (2007–2026), World Test Championship (2021–2025).
            *   🏀 **Basketball:** NBA Finals (1947–2026), FIBA World Cup (1950–2023).
            *   🎾 **Tennis:** Wimbledon, French Open, US Open (1968–2026), and Australian Open (1988–2026) Men's Singles Open Era champions & records.
            *   🏃 **Athletics:** Olympic Men's (1896–2024) & Women's (1928–2024) 100m Champions & records.
            """)

if __name__ == "__main__":
    main()