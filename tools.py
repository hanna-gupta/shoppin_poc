"""
Module: tools.py

This module provides utility functions for performing web searches using Google Serper API 
and scraping product details using the Firecrawl API. It also defines a Pydantic model
(ProductSchema) to structure extracted product details.
"""

from langchain_core.tools import Tool
from dotenv import load_dotenv
from langchain_community.utilities import GoogleSerperAPIWrapper
from firecrawl import FirecrawlApp
from pydantic import BaseModel, Field
import os

# Load API Keys from environment variables
load_dotenv()
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

# Initialize Google Serper API Wrapper for search functionality
search = GoogleSerperAPIWrapper(type="search", serper_api_key=SERPER_API_KEY, gl="in")

# Initialize Firecrawl API Client for web scraping
app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)

class ProductSchema(BaseModel):
    """
    Pydantic model defining the structure of product details extracted from a webpage.
    """
    product_name: str = Field(..., description="Name of the product")
    price: str = Field(..., description="Price of the product")
    discount: str = Field(..., description="Discount details")
    available_discounts: list[str] = Field([], description="Applicable discounts and promo codes")
    shipping_time: str = Field(..., description="Estimated shipping time")
    return_policy: str = Field(..., description="Return policy details")

def search_wrapper(query: str):
    """
    Perform a Google search using the Serper API.
    
    Args:
        query (str): The search query string.
    
    Returns:
        list or str: A list of search results or a message if no results are found.
    """
    results = search.results(query)
    return results if results else "No relevant results found."

def scrape_product_details(url: str):
    """
    Scrape product details from a given URL using the Firecrawl API.
    
    Args:
        url (str): The webpage URL to scrape.
    
    Returns:
        dict: Extracted product details in JSON format or an error message.
    """
    if not FIRECRAWL_API_KEY:
        return {"Error": "Firecrawl API key is missing."}
    
    try:
        response = app.scrape_url(url, {
            'formats': ['json'],
            'jsonOptions': {
                'schema': ProductSchema.model_json_schema()
            }
        })
        return response.get("json", {})
    except Exception as e:
        return {"Error": str(e)}

# Define tools 
tools= [
    Tool(
        name="Google Search",
        func=search_wrapper,
        description="Useful for searching products online."
    ),
    Tool(
        name="Scrape Product Details",
        func=scrape_product_details,
        description="Fetch product details from a given URL using Firecrawl API."
    )
]
