import os

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from app.agents.state import AgentState
from app.agents.nodes.planner import planner_node
from app.agents.nodes.retriever import retrieve_node
from app.agents.nodes.responder import generate_node


# 1. Initialize the State Graph
workflow = StateGraph(AgentState)


# 2. Define the Nodes
workflow.add_node("planner", planner_node)
workflow.add_node("retriever", retrieve_node)
workflow.add_node("responder", generate_node)

# 3. Define the Edges & Routing Logic
def route_planner(state: AgentState):
    """
    Routes the workflow based on the planner's decision.
    """
    if state["current_query"] == "CONVERSATIONAL":
        return "responder"
    return "retriever"

workflow.set_entry_point("planner")


# Conditional Edge: Planner -> Router -> (Retriever OR Responder)
workflow.add_conditional_edges(
    "planner",
    route_planner,
    {
        "retriever": "retriever",
        "responder": "responder"
    }
)


workflow.add_edge("retriever", "responder")
workflow.add_edge("responder", END)


# --- MEMORY UPGRADE ---
# MemorySaver keeps thread state in this process's RAM only — fine for a single
# local instance, but silently loses conversations across restarts or when
# scaled to >1 replica. POSTGRES_URL switches to a shared, durable checkpointer
# so conversation memory survives deploys/restarts and works behind autoscaling.


def _build_checkpointer():
    postgres_url = os.getenv("POSTGRES_URL")
    if not postgres_url:
        return MemorySaver()

    from psycopg_pool import ConnectionPool
    from langgraph.checkpoint.postgres import PostgresSaver

    pool = ConnectionPool(
        conninfo=postgres_url,
        max_size=20,
        kwargs={"autocommit": True, "prepare_threshold": 0},
    )
    checkpointer = PostgresSaver(pool)
    checkpointer.setup()
    return checkpointer


checkpointer = _build_checkpointer()


# 4. Compile the Graph with Memory
rag_agent = workflow.compile(checkpointer=checkpointer)