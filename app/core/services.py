from langchain_ollama import ChatOllama

from app.retrieval.embeddings import EmbeddingService
from app.retrieval.vector_store import TravelVectorStore
from app.ranking.ranker import DestinationRanker
from app.query.analyzer import QueryAnalyzer
from app.query.rewriter import QueryRewriter
from app.generation.answer_generator import AnswerGenerator
from app.evaluation.groundedness_checker import GroundednessChecker
from app.ranking.requirement_fit import RequirementFitEvaluator
from app.ranking.recommendation_decision import RecommendationDecision
from app.evaluation.claim_checker import ClaimChecker


CHROMA_PATH = "data/chroma"
COLLECTION_NAME = "india_travel"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL = "qwen3:1.7b"


class ExploreEaseServices:

    def __init__(self):

       
        print("Loading ExploreEase services...")

        # Load LLM once
        self.llm = ChatOllama(
            model=LLM_MODEL,
            temperature=0
        )

        

        # Load embedding model once
        embedding_service = EmbeddingService(
            EMBEDDING_MODEL
        )

        embeddings = embedding_service.get_embeddings()

        # Connect to Chroma once
        self.vector_store = TravelVectorStore(
            embeddings=embeddings,
            persist_directory=CHROMA_PATH,
            collection_name=COLLECTION_NAME
        )

        # Create application components once
        self.ranker = DestinationRanker(
    embeddings
)       
        self.requirement_fit = RequirementFitEvaluator()
        self.recommendation_decision = RecommendationDecision()
        

        self.analyzer = QueryAnalyzer()

        self.rewriter = QueryRewriter()
        self.claim_checker = ClaimChecker()

        self.generator = AnswerGenerator(
            LLM_MODEL
        )

        self.groundedness_checker = GroundednessChecker(
    LLM_MODEL,
    self.claim_checker
)

        print("ExploreEase services loaded.")