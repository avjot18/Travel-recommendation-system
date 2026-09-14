
from langchain_ollama import ChatOllama

from app.retrieval.embeddings import EmbeddingService
from app.retrieval.vector_store import TravelVectorStore

from app.ranking.ranker import DestinationRanker
from app.ranking.requirement_fit import RequirementFitEvaluator
from app.ranking.recommendation_decision import (
    RecommendationDecision
)

from app.query.analyzer import QueryAnalyzer
from app.query.rewriter import QueryRewriter

from app.generation.answer_generator import (
    AnswerGenerator
)

from app.evaluation.groundedness_checker import (
    GroundednessChecker
)

from app.evaluation.claim_checker import (
    ClaimChecker
)

# -------------------------------------------------
# Destination knowledge
# -------------------------------------------------

from app.destination.repository import (
    DestinationRepository
)

from app.destination.mapper import (
    DestinationMapper
)

# -------------------------------------------------
# Travel planning
# -------------------------------------------------

from app.planning.activity_planner import (
    ActivityPlanner
)

from app.planning.itinerary_planner import (
    ItineraryPlanner
)

from app.planning.budget_estimator import (
    BudgetEstimator
)

from app.planning.stay_area_planner import (
    StayAreaRecommender
)


CHROMA_PATH = "data/chroma"

COLLECTION_NAME = "india_travel"

EMBEDDING_MODEL = (
    "sentence-transformers/all-MiniLM-L6-v2"
)

LLM_MODEL = "qwen3:1.7b"

DATASET_PATH = (
    "data/"
    "india_travel_knowledge_base_v2_fully_populated.json"
)


class ExploreEaseServices:

    def __init__(self):

        print(
            "Loading ExploreEase services..."
        )

        # -------------------------------------------------
        # LLM
        # -------------------------------------------------

        self.llm = ChatOllama(
            model=LLM_MODEL,
            temperature=0
        )

        # -------------------------------------------------
        # Embeddings
        # -------------------------------------------------

        embedding_service = EmbeddingService(
            EMBEDDING_MODEL
        )

        embeddings = (
            embedding_service.get_embeddings()
        )

        # -------------------------------------------------
        # Vector store
        # -------------------------------------------------

        self.vector_store = TravelVectorStore(
            embeddings=embeddings,
            persist_directory=CHROMA_PATH,
            collection_name=COLLECTION_NAME
        )

        # -------------------------------------------------
        # Query understanding
        # -------------------------------------------------

        self.analyzer = QueryAnalyzer()

        self.rewriter = QueryRewriter()

        # -------------------------------------------------
        # Ranking
        # -------------------------------------------------

        self.ranker = DestinationRanker(
            embeddings
        )

        self.requirement_fit = (
            RequirementFitEvaluator()
        )

        self.recommendation_decision = (
            RecommendationDecision()
        )

        # -------------------------------------------------
        # Answer generation
        # -------------------------------------------------

        self.generator = AnswerGenerator(
            LLM_MODEL
        )

        # -------------------------------------------------
        # Evaluation
        # -------------------------------------------------

        self.claim_checker = ClaimChecker()

        self.groundedness_checker = (
            GroundednessChecker(
                LLM_MODEL,
                self.claim_checker
            )
        )

        # -------------------------------------------------
        # Destination knowledge
        # -------------------------------------------------

        self.destination_repository = (
            DestinationRepository(
                DATASET_PATH
            )
        )

        self.destination_mapper = (
            DestinationMapper(
                self.destination_repository
            )
        )

        # -------------------------------------------------
        # Travel planning
        # -------------------------------------------------

        self.activity_planner = (
            ActivityPlanner()
        )

        self.itinerary_planner = (
            ItineraryPlanner()
        )

        self.budget_estimator = (
            BudgetEstimator()
        )

        self.stay_area_recommender = (
            StayAreaRecommender()
        )

        print(
            "ExploreEase services loaded."
        )
