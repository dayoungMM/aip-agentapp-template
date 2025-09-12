import os
from adxp_sdk.auth import TokenCredentials, ApiKeyCredentials
from adxp_sdk.knowledges.retriever import AXKnowledgeRetriever
from adxp_sdk.knowledges.schemas import RetrievalSimpleQuery, RetrievalAdvancedQuery, RetrievalOptions
from langchain_core.tools import tool, BaseTool

from langchain_core.messages import ToolMessage
from langgraph.prebuilt import ToolNode
from langchain_core.runnables import RunnableLambda



@tool
def univ_retriever(query: str):
    """대학 입학, 입시(수시, 정시 등) 관련 검색"""
    apikey_credentials = ApiKeyCredentials(
        api_key=os.getenv("AIP_API_KEY", "EMPTY_APIKEY"),
        base_url=os.getenv("AIP_BASE_URL", "http://aip.sktai.io"),
    )

    retriever = AXKnowledgeRetriever(apikey_credentials, repo_id="f7f6253a-30a5-4e76-92ce-ce375dcaf3b2")

    a_query = RetrievalAdvancedQuery(query_text=query, retrieval_options=RetrievalOptions(top_k=3))
    return [d.model_dump() for d in retriever.get_relevant_documents(a_query)]

@tool
def household_retriever(query: str):
    """기업정보, 코드 """
    apikey_credentials = ApiKeyCredentials(
        api_key=os.getenv("AIP_API_KEY", "USE_YOUR_API_KEY"),
        base_url=os.getenv("AIP_BASE_URL", "http://aip.sktai.io"),
    )

    retriever = AXKnowledgeRetriever(apikey_credentials, repo_id="65853c6d-d2c9-4c0d-972d-1c190a4c0d32")

    a_query = RetrievalAdvancedQuery(query_text=query, retrieval_options=RetrievalOptions(top_k=3))
    return [d.model_dump() for d in retriever.get_relevant_documents(a_query)]
    

    