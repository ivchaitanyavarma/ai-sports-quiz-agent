from langchain_community.tools import DuckDuckGoSearchRun
from src.config import get_logger

logger = get_logger(__name__)

class SearchManager:
    """Handles query generation and live scraping constraints via DuckDuckGo."""
    
    def __init__(self):
        self.search_tool = DuckDuckGoSearchRun()

    def discover_live_data(self, topic: str, difficulty: str) -> str:
        """Modifies programmatic search parameters to shape context depth based on specific sport domains."""
        
        domain_mapping = {
            "Formula 1": "Drivers Constructors Championship youngest oldest records streaks",
            "Football": "World Cup Euro UEFA Champions League European Cup finals host score",
            "Cricket": "ODI World Cup T20 World Test Championship finals records",
            "Basketball": "NBA Finals FIBA World Cup champions records"
        }
        
        domain_context = domain_mapping.get(topic, topic)
        logger.info(f"Building search criteria for: {topic} | Tier: {difficulty}")
        
        if difficulty == "Hard":
            query = f"obscure rare {topic} {domain_context} trivia unexpected stats historical anomalies"
        elif difficulty == "Medium":
            query = f"significant milestones breaking news {topic} {domain_context} history"
        else:
            query = f"basic recent winners standard records {topic} {domain_context}"
            
        try:
            return self.search_tool.run(query)
        except Exception as e:
            logger.warning(f"DuckDuckGo search gateway timeout or block: {e}")
            return "Live lookup metrics currently unavailable via search engine."

search_manager = SearchManager()