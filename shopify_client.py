"""
Shopify GraphQL API Client

This module provides a client for interacting with Shopify's GraphQL Admin API.
"""

import requests
import json
from typing import Dict, Any, Optional

class ShopifyGraphQLClient:
    def __init__(self, shop_url: str, access_token: str):
        self.shop_url = shop_url.rstrip('/')
        self.access_token = access_token
        self.graphql_endpoint = f"{self.shop_url}/admin/api/2025-10/graphql.json"
    
    def _get_headers(self) -> Dict[str, str]:
        """Get the required headers for API requests."""
        return {
            "X-Shopify-Access-Token": self.access_token,
            "Content-Type": "application/json",
        }
    
    def query(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = {
            "query": query,
        }
        if variables:
            payload["variables"] = variables
        
        try:
            response = requests.post(
                self.graphql_endpoint,
                headers=self._get_headers(),
                json=payload,
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Check for GraphQL errors
            if "errors" in data:
                error_msg = json.dumps(data["errors"], indent=2)
                raise Exception(f"GraphQL Error: {error_msg}")
            
            return data.get("data", {})
        
        except requests.exceptions.RequestException as e:
            raise Exception(f"API Request Failed: {str(e)}")
    
    def mutation(self, mutation: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self.query(mutation, variables)
    
if __name__ == "__main__":
    print("Shopify GraphQL Client ready. Import this module to use ShopifyGraphQLClient.")
