"""
OpenAPI tool specifications for Market Sentinel agents.

Contains GDELT DOC API and Watchlist placeholder API specs.
"""

from typing import Any


def get_gdelt_openapi_spec() -> dict[str, Any]:
    """
    Return the OpenAPI 3.0 specification for GDELT DOC API.
    
    GDELT DOC API: https://api.gdeltproject.org/api/v2/doc/doc
    
    Returns articles matching a query with tone analysis and metadata.
    """
    return {
        "openapi": "3.0.3",
        "info": {
            "title": "GDELT DOC API",
            "description": "GDELT 2.0 DOC API for querying global news articles with sentiment analysis",
            "version": "2.0.0",
        },
        "servers": [
            {
                "url": "https://api.gdeltproject.org",
                "description": "GDELT Production API",
            }
        ],
        "paths": {
            "/api/v2/doc/doc": {
                "get": {
                    "operationId": "searchArticles",
                    "summary": "Search GDELT articles",
                    "description": "Query GDELT database for news articles matching search criteria",
                    "parameters": [
                        {
                            "name": "query",
                            "in": "query",
                            "required": True,
                            "description": "Search query. Supports boolean operators (AND, OR, NOT), quotes for exact phrases, and parentheses for grouping. Example: (port OR shipping) AND (delay OR congestion)",
                            "schema": {
                                "type": "string",
                            },
                        },
                        {
                            "name": "format",
                            "in": "query",
                            "required": False,
                            "description": "Output format",
                            "schema": {
                                "type": "string",
                                "enum": ["json", "csv", "html"],
                                "default": "json",
                            },
                        },
                        {
                            "name": "mode",
                            "in": "query",
                            "required": False,
                            "description": "Response mode - ArtList returns article list",
                            "schema": {
                                "type": "string",
                                "enum": ["ArtList", "TimelineVol", "TimelineTone", "TimelineSourceCountry"],
                                "default": "ArtList",
                            },
                        },
                        {
                            "name": "maxrecords",
                            "in": "query",
                            "required": False,
                            "description": "Maximum number of records to return (max 250)",
                            "schema": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 250,
                                "default": 50,
                            },
                        },
                        {
                            "name": "sort",
                            "in": "query",
                            "required": False,
                            "description": "Sort order for results",
                            "schema": {
                                "type": "string",
                                "enum": ["datedesc", "dateasc", "tonedesc", "toneasc"],
                                "default": "datedesc",
                            },
                        },
                        {
                            "name": "timespan",
                            "in": "query",
                            "required": False,
                            "description": "Time span to search (e.g., '24h', '7d', '1m')",
                            "schema": {
                                "type": "string",
                                "default": "24h",
                            },
                        },
                        {
                            "name": "sourcelang",
                            "in": "query",
                            "required": False,
                            "description": "Filter by source language (ISO 639-1 code)",
                            "schema": {
                                "type": "string",
                                "default": "english",
                            },
                        },
                    ],
                    "responses": {
                        "200": {
                            "description": "Successful response with article list",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "articles": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "url": {
                                                            "type": "string",
                                                            "description": "Article URL",
                                                        },
                                                        "url_mobile": {
                                                            "type": "string",
                                                            "description": "Mobile URL if available",
                                                        },
                                                        "title": {
                                                            "type": "string",
                                                            "description": "Article title",
                                                        },
                                                        "seendate": {
                                                            "type": "string",
                                                            "description": "Date article was seen (YYYYMMDDTHHMMSSZ)",
                                                        },
                                                        "socialimage": {
                                                            "type": "string",
                                                            "description": "Social sharing image URL",
                                                        },
                                                        "domain": {
                                                            "type": "string",
                                                            "description": "Source domain",
                                                        },
                                                        "language": {
                                                            "type": "string",
                                                            "description": "Article language",
                                                        },
                                                        "sourcecountry": {
                                                            "type": "string",
                                                            "description": "Source country",
                                                        },
                                                        "tone": {
                                                            "type": "number",
                                                            "description": "Article tone score (-100 to +100)",
                                                        },
                                                    },
                                                },
                                            },
                                        },
                                    },
                                },
                            },
                        },
                        "400": {
                            "description": "Bad request - invalid query parameters",
                        },
                        "500": {
                            "description": "Server error",
                        },
                    },
                },
            },
        },
    }


def get_watchlist_openapi_spec() -> dict[str, Any]:
    """
    Return the OpenAPI 3.0 specification for the Watchlist/Shipments API.
    
    This is a placeholder specification for an internal API that would
    provide watchlist and shipment data in a production environment.
    
    Returns:
        OpenAPI 3.0 specification dict
    """
    return {
        "openapi": "3.0.3",
        "info": {
            "title": "Watchlist & Shipments API",
            "description": "Internal API for supply chain watchlist and active shipment data",
            "version": "1.0.0",
        },
        "servers": [
            {
                "url": "https://example.internal.api",
                "description": "Internal API server (placeholder)",
            }
        ],
        "paths": {
            "/watchlist": {
                "get": {
                    "operationId": "getWatchlist",
                    "summary": "Get current watchlist",
                    "description": "Retrieve the current supply chain watchlist including monitored lanes, entities, and commodities",
                    "responses": {
                        "200": {
                            "description": "Watchlist data",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "watchlist_id": {
                                                "type": "string",
                                                "description": "Unique watchlist identifier",
                                            },
                                            "updated_at": {
                                                "type": "string",
                                                "format": "date-time",
                                                "description": "Last update timestamp",
                                            },
                                            "lanes": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "origin": {
                                                            "type": "string",
                                                            "description": "Origin port/location code",
                                                        },
                                                        "destination": {
                                                            "type": "string",
                                                            "description": "Destination port/location code",
                                                        },
                                                        "commodities": {
                                                            "type": "array",
                                                            "items": {
                                                                "type": "string",
                                                            },
                                                            "description": "Commodities on this lane",
                                                        },
                                                        "priority": {
                                                            "type": "string",
                                                            "enum": ["low", "medium", "high", "critical"],
                                                            "description": "Lane priority level",
                                                        },
                                                    },
                                                },
                                            },
                                            "entities": {
                                                "type": "array",
                                                "items": {
                                                    "type": "string",
                                                },
                                                "description": "Monitored entity names",
                                            },
                                            "keywords": {
                                                "type": "array",
                                                "items": {
                                                    "type": "string",
                                                },
                                                "description": "Additional keywords to monitor",
                                            },
                                        },
                                    },
                                },
                            },
                        },
                        "401": {
                            "description": "Unauthorized",
                        },
                        "500": {
                            "description": "Server error",
                        },
                    },
                },
            },
            "/shipments": {
                "get": {
                    "operationId": "getShipments",
                    "summary": "Get active shipments",
                    "description": "Retrieve details of active shipments, optionally filtered by shipment IDs",
                    "parameters": [
                        {
                            "name": "shipment_ids",
                            "in": "query",
                            "required": False,
                            "description": "Comma-separated list of shipment IDs to filter",
                            "schema": {
                                "type": "string",
                            },
                        },
                        {
                            "name": "status",
                            "in": "query",
                            "required": False,
                            "description": "Filter by shipment status",
                            "schema": {
                                "type": "string",
                                "enum": ["pending", "in_transit", "delayed", "arrived", "customs"],
                            },
                        },
                        {
                            "name": "limit",
                            "in": "query",
                            "required": False,
                            "description": "Maximum number of shipments to return",
                            "schema": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 100,
                                "default": 50,
                            },
                        },
                    ],
                    "responses": {
                        "200": {
                            "description": "Shipment data",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "shipments": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "shipment_id": {
                                                            "type": "string",
                                                            "description": "Unique shipment identifier",
                                                        },
                                                        "origin": {
                                                            "type": "string",
                                                            "description": "Origin port/location code",
                                                        },
                                                        "destination": {
                                                            "type": "string",
                                                            "description": "Destination port/location code",
                                                        },
                                                        "carrier": {
                                                            "type": "string",
                                                            "description": "Carrier/shipping line name",
                                                        },
                                                        "vessel_name": {
                                                            "type": "string",
                                                            "description": "Vessel name if applicable",
                                                        },
                                                        "commodity": {
                                                            "type": "string",
                                                            "description": "Primary commodity",
                                                        },
                                                        "status": {
                                                            "type": "string",
                                                            "enum": ["pending", "in_transit", "delayed", "arrived", "customs"],
                                                        },
                                                        "eta": {
                                                            "type": "string",
                                                            "format": "date-time",
                                                            "description": "Estimated time of arrival",
                                                        },
                                                        "current_location": {
                                                            "type": "object",
                                                            "properties": {
                                                                "lat": {
                                                                    "type": "number",
                                                                },
                                                                "lon": {
                                                                    "type": "number",
                                                                },
                                                                "name": {
                                                                    "type": "string",
                                                                },
                                                            },
                                                        },
                                                        "value_usd": {
                                                            "type": "number",
                                                            "description": "Shipment value in USD",
                                                        },
                                                    },
                                                },
                                            },
                                            "total_count": {
                                                "type": "integer",
                                                "description": "Total number of matching shipments",
                                            },
                                        },
                                    },
                                },
                            },
                        },
                        "401": {
                            "description": "Unauthorized",
                        },
                        "500": {
                            "description": "Server error",
                        },
                    },
                },
            },
        },
    }


