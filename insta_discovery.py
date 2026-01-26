from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
import json

load_dotenv()

#class InstaDiscoveryTool(BaseModel):

def insta_search_query_generator(niche:str , location: str , keyword: str , language: str) -> json:
    """Generate Instagram search query using Google GenAI."""
    PROMPT_TEMPLATE = """
                    You are a search query generation agent.

                    Your task is to generate Google/Bing search queries
                    that can be used to discover Instagram influencer profiles.

                    Rules:
                    - Queries MUST target Instagram profiles only
                    - Use site:instagram.com
                    - Include niche keywords
                    - Include optional location or language hints
                    - Avoid generic or broad queries
                    - Each query should be realistic and human-like

                    Input:
                    Niche: {niche}
                    Keywords: {keywords}
                    Location: {location}
                    Language: {language}

                    Output:
                    Return ONLY a JSON array of search queries.
                    No explanations. No markdown.
        """



    llm = ChatGoogleGenerativeAI(
        model="gemini-3-pro-preview",
        temperature = 0.3
        )
    #prompt = f"Generate an Instagram search query for the following topic: {niche} in {location} with keyword {keyword}. "

    prompt = PromptTemplate(
        template=PROMPT_TEMPLATE,
        input_variables=["niche", "location", "keyword" , "language"])

    chain = prompt | llm | JsonOutputParser()

    response = chain.invoke({
        "niche": niche,
        "keywords": keyword,
        "location": location,
        "language": language
    })

    return response


if __name__ == "__main__":
    niche = input("Enter niche (e.g., fitness, fashion, travel): ")
    location = input("Enter location (e.g., delhi, Kolkata) or leave blank: ")
    keyword = input("Enter keyword (e.g., yoga, street style) or leave blank: ")
    language = input("Enter language (e.g., English, Spanish) or leave blank: ")

    queries = insta_search_query_generator(niche, location, keyword, language)
    print("Generated Instagram Search Queries:")
    print(queries)
    print(type(queries))

