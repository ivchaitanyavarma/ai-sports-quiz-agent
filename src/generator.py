from typing import TypedDict, List, Optional
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI

from src.config import settings, get_logger
from src.database import db_manager
from src.search import search_manager

logger = get_logger(__name__)

# --- Architectural Runtime Schema Contracts ---
class GraphState(TypedDict):
    topic: str
    difficulty: str
    local_context: str
    web_context: str
    quiz_result: Optional[dict]
    system_errors: List[str]

class QuizItem(BaseModel):
    """Schema for a single question."""
    question: str = Field(description="The final multiple choice quiz question text.")
    options: List[str] = Field(description="Exactly 4 distinct answers, including the true answer and 3 distractors.")
    correct_answer: str = Field(description="The exact text option matching the correct answer choice.")
    explanation: str = Field(description="Historical and logical confirmation backing up the answer validation.")

class QuizBatchOutput(BaseModel):
    """Schema for the 10-question batch."""
    questions: List[QuizItem] = Field(description="A list of exactly 10 distinct multiple-choice quiz questions.")

# --- Initialize Core LLM Client Runtime ---
try:
    gemini_llm = ChatGoogleGenerativeAI(
        model=settings.LLM_MODEL,
        temperature=settings.LLM_TEMPERATURE,
        google_api_key=settings.GOOGLE_API_KEY
    )
    # Bind the new batch schema
    structured_generator = gemini_llm.with_structured_output(QuizBatchOutput)
except Exception as e:
    logger.critical(f"Critical initialization failure for Google Gemini API engine: {e}")
    raise

# --- Operational Node Implementations ---
def node_extract_local_facts(state: GraphState) -> dict:
    context = db_manager.query_sampled_facts(topic=state["topic"])
    return {"local_context": context}

def node_extract_web_trends(state: GraphState) -> dict:
    context = search_manager.discover_live_data(
        topic=state["topic"], 
        difficulty=state["difficulty"]
    )
    return {"web_context": context}

def node_synthesize_quiz(state: GraphState) -> dict:
    logger.info("Fusing pipelines to formulate structured LLM quiz challenge batch...")
    
    prompt = f"""
    You are a professional sports quiz system. Construct a batch of exactly 10 valid multiple-choice questions centered on: {state['topic']}.
    Target Difficulty Specification: {state['difficulty']}

    Strictly base factual validity on these combined inputs:
    [Historical Local Archive Data]:
    {state['local_context']}

    [Current Live Web Context]:
    {state['web_context']}

    CRITICAL RULES FOR DISTRACTORS:
    - Easy Mode: Make the incorrect options obvious and non-competitive.
    - Medium Mode: Ensure incorrect options are plausible historic athletes, scores, or milestones.
    - Hard Mode: Deceive the user using highly sophisticated, structurally related real dates, similar sports personalities, or inverse statistics that are contextually invalid for this specific prompt.

    Validate your constraints before finishing: The data must be accurate, avoid hallucinating facts, and output exactly 10 unique questions.
    """
    
    try:
        response = structured_generator.invoke(prompt)
        return {"quiz_result": response.model_dump()}
    except Exception as e:
        logger.error(f"Structured response generation crash: {e}")
        return {"system_errors": [f"LLM compilation failure: {str(e)}"]}

# --- Workflow Compilation ---
def generate_graph_application():
    builder = StateGraph(GraphState)
    
    builder.add_node("local_retrieval", node_extract_local_facts)
    builder.add_node("web_retrieval", node_extract_web_trends)
    builder.add_node("llm_generation", node_synthesize_quiz)
    
    builder.set_entry_point("local_retrieval")
    builder.add_edge("local_retrieval", "web_retrieval")
    builder.add_edge("web_retrieval", "llm_generation")
    builder.add_edge("llm_generation", END)
    
    return builder.compile()

compiled_agent_graph = generate_graph_application()