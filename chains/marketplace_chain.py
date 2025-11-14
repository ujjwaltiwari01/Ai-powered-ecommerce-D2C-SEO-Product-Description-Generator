"""Marketplace-specific content generation chain."""
from typing import Dict, Any, List, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import json

class MarketplaceChain:
    """Chain for generating marketplace-specific product content."""
    
    MARKETPLACE_RULES = {
        "amazon_in": {
            "title_max_length": 200,
            "max_bullets": 5,
            "description_style": "features_and_benefits",
            "tone": "professional",
            "requires_technical_specs": True,
            "allows_emoji": False,
            "allows_html": True,
            "keywords_important": True
        },
        "flipkart": {
            "title_max_length": 100,
            "max_bullets": None,  # Uses description format
            "description_style": "paragraph",
            "tone": "conversational",
            "requires_technical_specs": True,
            "allows_emoji": False,
            "allows_html": False,
            "keywords_important": True
        },
        "meesho": {
            "title_max_length": 60,
            "max_bullets": 3,
            "description_style": "simple_points",
            "tone": "simple_hindi_english",
            "requires_technical_specs": False,
            "allows_emoji": True,
            "allows_html": False,
            "keywords_important": False
        },
        # Add more marketplaces as needed
    }
    
    def __init__(self, llm):
        """Initialize the marketplace chain."""
        self.llm = llm
        self.prompt = self._create_prompt()
        self.chain = self.prompt | self.llm | StrOutputParser()
    
    def _create_prompt(self):
        """Create the prompt template for marketplace content generation."""
        return ChatPromptTemplate.from_messages([
            ("system", """You are an expert at creating optimized product content for various marketplaces.
            
            Your task is to generate product content for {marketplace_name} based on the provided product information.
            
            Marketplace Guidelines:
            - Title: {title_guidelines}
            - Description Style: {description_style}
            - Tone: {tone}
            - Technical Specs: {requires_tech_specs}
            - Emoji Allowed: {allows_emoji}
            - HTML Allowed: {allows_html}
            - Keywords Important: {keywords_important}
            
            Generate content that follows these guidelines exactly."""),
            ("human", """
            Product Information:
            {product_info}
            
            Generate the following for {marketplace_name}:
            1. A compelling product title (max {title_max_length} chars)
            2. A product description that highlights key features and benefits
            3. {bullet_count} key bullet points (if applicable)
            4. Any additional required fields for this marketplace
            
            Format your response as a JSON object with these fields:
            {{
                "title": "...",
                "description": "...",
                "bullet_points": ["...", "..."],
                "keywords": ["...", "..."],
                "additional_fields": {{
                    "field1": "value1",
                    "field2": "value2"
                }}
            }}""")
        ])
    
    def _get_marketplace_guidelines(self, marketplace_key: str) -> Dict[str, Any]:
        """Get the guidelines for a specific marketplace."""
        default_rules = {
            "title_max_length": 100,
            "max_bullets": 5,
            "description_style": "standard",
            "tone": "professional",
            "requires_technical_specs": False,
            "allows_emoji": False,
            "allows_html": False,
            "keywords_important": True
        }
        
        return self.MARKETPLACE_RULES.get(marketplace_key, default_rules)
    
    def _format_product_info(self, product_info: Dict[str, Any]) -> str:
        """Format product information for the prompt."""
        basic_info = product_info.get('basic_info', {})
        features = product_info.get('features', [])
        
        formatted = f"""
        Product Name: {basic_info.get('product_name', 'N/A')}
        Brand: {basic_info.get('brand_name', 'N/A')}
        Category: {basic_info.get('category', 'N/A')}
        Target Audience: {basic_info.get('target_audience', 'N/A')}
        Unique Selling Points: {basic_info.get('usp', 'N/A')}
        
        Features:
        """
        formatted += "\n".join([f"- {feature}" for feature in features])
        
        if 'specifications' in product_info:
            formatted += "\n\nSpecifications:\n"
            for key, value in product_info['specifications'].items():
                formatted += f"- {key}: {value}\n"
        
        return formatted
    
    def _parse_output(self, output: str) -> Dict[str, Any]:
        """Parse the output from the LLM."""
        try:
            # Try to parse as JSON
            return json.loads(output.strip())
        except json.JSONDecodeError:
            # If parsing fails, try to extract JSON from the output
            try:
                start = output.find('{')
                end = output.rfind('}') + 1
                if start >= 0 and end > start:
                    return json.loads(output[start:end])
                raise ValueError("Could not parse output as JSON")
            except Exception:
                return {
                    "error": "Failed to parse model output",
                    "raw_output": output
                }
    
    def __call__(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate marketplace-specific content."""
        try:
            marketplace_key = inputs['marketplace_key']
            product_info = inputs['product_info']
            
            # Get marketplace guidelines
            guidelines = self._get_marketplace_guidelines(marketplace_key)
            
            # Format product info
            formatted_product_info = self._format_product_info(product_info)
            
            # Prepare prompt inputs
            prompt_inputs = {
                "marketplace_name": marketplace_key.upper(),
                "title_guidelines": f"Max {guidelines['title_max_length']} characters, include brand and key features",
                "description_style": guidelines['description_style'],
                "tone": guidelines['tone'],
                "requires_tech_specs": "Required" if guidelines['requires_technical_specs'] else "Not required",
                "allows_emoji": "Yes" if guidelines['allows_emoji'] else "No",
                "allows_html": "Yes" if guidelines['allows_html'] else "No",
                "keywords_important": "Yes" if guidelines['keywords_important'] else "No",
                "title_max_length": guidelines['title_max_length'],
                "bullet_count": guidelines.get('max_bullets', 5),
                "product_info": formatted_product_info
            }
            
            # Get response from the model
            response = self.chain.invoke(prompt_inputs)
            
            # Parse the response
            result = self._parse_output(response)
            
            return {
                marketplace_key: result
            }
            
        except Exception as e:
            return {
                "error": f"Error in MarketplaceChain: {str(e)}",
                "marketplace_key": marketplace_key
            }


def create_marketplace_chain(llm):
    """Create a marketplace chain with the given LLM."""
    return MarketplaceChain(llm)
