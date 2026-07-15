import logfire
from app.agents.state import AgentState
from app.gateway.client import portkey_client, extract_cache_status


def generate_node(state: AgentState):
    """
    Synthesizes a response using both Documentation Context AND Conversation History.
    Uses the native Portkey client (not LangChain) so we can read the
    x-portkey-cache-status response header and surface Cache: Hit in the UI.
    """
    query = state["current_query"]

    history_str = ""
    for msg in state["messages"][:-1]:
        role = "User" if msg["role"] == "user" else "Assistant"
        history_str += f"{role}: {msg['content']}\n"

    user_msg = state["messages"][-1]["content"] if state["messages"] else ""

    if query == "CONVERSATIONAL":
        logfire.info("Generating conversational response using memory.")
        prompt = f"""
        You are an Enterprise IT Assistant that ONLY helps with Kubernetes,
        Intel hardware, and enterprise networking.

        Rules:
        - If the latest message is a greeting, farewell, or a follow-up that can
          be answered from the CONVERSATION HISTORY, respond helpfully and concisely.
        - If the latest message is off-topic — general knowledge, math, jokes,
          trivia, current events, or any subject outside Kubernetes / Intel
          hardware / enterprise networking (e.g. "what is 2+2", "what is vector RAG") —
          DO NOT answer it. Reply exactly:
          "I'm an Enterprise IT Assistant focused on Kubernetes, Intel hardware, and enterprise networking. I can't help with that — but ask me anything in those areas!"

        CONVERSATION HISTORY:
        {history_str}

        LATEST MESSAGE:
        "{user_msg}"
        """
    else:
        logfire.info("Generating technical RAG response.")
        max_context_chars = 25000
        full_context = ""

        for doc in state["documents"]:
            if len(full_context) + len(doc) < max_context_chars:
                full_context += doc + "\n\n"
            else:
                logfire.warning("Context truncated to fit Groq TPM limits.")
                break

        prompt = f"""
        You are a Senior Technical Architect specialising in Kubernetes, Intel
        hardware, and enterprise networking.

        Answer the USER QUESTION using ONLY the TECHNICAL CONTEXT provided.
        - Do NOT use outside/general knowledge to fill gaps.
        - If the question is not about Kubernetes, Intel hardware, or enterprise
          networking, OR the TECHNICAL CONTEXT does not contain the answer, reply
          exactly: "I'm an Enterprise IT Assistant focused on Kubernetes, Intel hardware, and enterprise networking, and I don't have that in my documentation."

        TECHNICAL CONTEXT:
        {full_context}

        CONVERSATION HISTORY:
        {history_str}

        USER QUESTION:
        "{user_msg}"
        """

    with logfire.span("✍️ LLM Synthesis"):
        try:
            response = portkey_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            content = response.choices[0].message.content
            cache_status = extract_cache_status(response)
            is_cache_hit = cache_status == "HIT"

            if is_cache_hit:
                logfire.info("⚡ Gateway Cache Hit — response served from Portkey cache.")
                plan_update = state["plan"] + ["Cache: Hit ⚡"]
                status = "Cache hit — instant response."
            else:
                logfire.info("✅ Response synthesised via LLM.")
                plan_update = state["plan"]
                status = "Response generated."

            return {
                "final_answer": content,
                "status": status,
                "plan": plan_update,
                "messages": [{"role": "assistant", "content": content}]
            }

        except Exception as e:
            logfire.error(f"LLM Generation failed: {e}")
            raise e