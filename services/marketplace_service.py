"""Service for generating marketplace-specific content."""
import json
from typing import Dict, Any, List, Optional
import logging
from pathlib import Path
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import AI services
from utils.ai_services import ai_service

class MarketplaceService:
    """Service for generating and managing marketplace content."""
    
    # Marketplace-specific templates and rules
    MARKETPLACE_TEMPLATES = {
        # Amazon India
        "amazon_in": {
            "name": "Amazon India",
            "title": "{brand} {product_name} - {key_features}",
            "description": """**{brand} {product_name}**\n\n{product_description}\n\n**Key Features:**\n{features}\n\n**Specifications:**\n{specifications}\n\n**Why Choose {brand}?**\n{usps}\n\n{additional_notes}""",
            "max_title_length": 200,
            "max_bullets": 5,
            "requires_technical_specs": True,
            "allows_html": True,
            "requires_brand": True,
            "requires_price": True,
            "requires_category": True
        },
        
        # Flipkart
        "flipkart": {
            "name": "Flipkart",
            "title": "{brand} {product_name} ({key_features})",
            "description": """{product_description}\n\n• {features_bullets}\n\n**Specifications:**\n{specifications}\n\n{usps_bullets}\n\n{additional_notes}""",
            "max_title_length": 100,
            "max_bullets": None,
            "requires_technical_specs": True,
            "allows_html": False,
            "requires_brand": True,
            "requires_price": True,
            "requires_category": True
        },
        
        # Meesho
        "meesho": {
            "name": "Meesho",
            "title": "{brand} {product_name}",
            "description": "{product_description}\n\n{features_bullets}\n\n{usps_bullets}",
            "max_title_length": 60,
            "max_bullets": 3,
            "requires_technical_specs": False,
            "allows_html": False,
            "requires_brand": False,
            "requires_price": True,
            "requires_category": True
        },
        
        # Myntra
        "myntra": {
            "name": "Myntra",
            "title": "{brand} {product_name} | {key_features}",
            "description": """{brand} presents {product_name} - {key_features}\n\n{product_description}\n\n**Features:**\n{features}\n\n**Specifications:**\n{specifications}\n\n{usps_bullets}""",
            "max_title_length": 80,
            "max_bullets": 4,
            "requires_technical_specs": True,
            "allows_html": True,
            "requires_brand": True,
            "requires_price": True,
            "requires_category": True
        },
        
        # Ajio
        "ajio": {
            "name": "Ajio",
            "title": "{brand} {product_name}",
            "description": "{product_description}\n\n**Key Features:**\n{features}\n\n**Material & Care:**\n{material_care}\n\n{usps_bullets}",
            "max_title_length": 70,
            "max_bullets": 5,
            "requires_technical_specs": False,
            "allows_html": True,
            "requires_brand": True,
            "requires_price": True,
            "requires_category": True
        },
        
        # Nykaa
        "nykaa": {
            "name": "Nykaa",
            "title": "{brand} {product_name} - {key_features}",
            "description": """**{brand} {product_name}**\n\n{product_description}\n\n**Key Benefits:**\n{features}\n\n**How To Use:**\n{usage_instructions}\n\n**Ingredients:**\n{ingredients}\n\n{usps_bullets}""",
            "max_title_length": 120,
            "max_bullets": 5,
            "requires_technical_specs": False,
            "allows_html": True,
            "requires_brand": True,
            "requires_price": True,
            "requires_category": True
        },
        
        # Shopify
        "shopify": {
            "name": "Shopify",
            "title": "{product_name} by {brand}",
            "description": """# {product_name}\n\n{product_description}\n\n## Features\n{features}\n\n## Specifications\n{specifications}\n\n## Why Choose This Product?\n{usps}""",
            "max_title_length": 255,
            "max_bullets": None,
            "requires_technical_specs": False,
            "allows_html": True,
            "requires_brand": False,
            "requires_price": True,
            "requires_category": False
        },
        
        # Etsy
        "etsy": {
            "name": "Etsy",
            "title": "{product_name} - Handmade by {brand}",
            "description": """{product_description}\n\n✨ **Features:**\n{features}\n\n📏 **Details:**\n{specifications}\n\n💖 {usps_bullets}\n\n{additional_notes}""",
            "max_title_length": 140,
            "max_bullets": 5,
            "requires_technical_specs": False,
            "allows_html": True,
            "requires_brand": False,
            "requires_price": True,
            "requires_category": True
        }
    }
    
    def __init__(self):
        """Initialize the marketplace service."""
        self.ai_service = ai_service
    
    def _format_features(self, features: List[str], max_items: Optional[int] = None) -> str:
        """Format features as a bulleted list."""
        if not features:
            return ""
        
        if max_items and len(features) > max_items:
            features = features[:max_items]
        
        return "• " + "\n• ".join(features)
    
    def _format_specifications(self, specs: Dict[str, Any]) -> str:
        """Format product specifications."""
        if not specs:
            return ""
        
        formatted = []
        for key, value in specs.items():
            if isinstance(value, list):
                value = ", ".join(str(v) for v in value)
            formatted.append(f"- {key}: {value}")
        
        return "\n".join(formatted)
    
    def _generate_with_ai(self, prompt: str, model: str = "gpt-4-1106-preview") -> str:
        """Generate content using the AI service."""
        try:
            result = self.ai_service.generate_content(
                prompt=prompt,
                model=model,
                temperature=0.7,
                max_tokens=1000
            )
            
            if result["success"]:
                return result["text"].strip()
            else:
                logger.error(f"AI generation failed: {result.get('error')}")
                return ""
                
        except Exception as e:
            logger.exception(f"Error generating content: {str(e)}")
            return ""
    
    def _validate_product_info(self, product_info: Dict[str, Any], template: Dict[str, Any]) -> List[str]:
        """Validate product information against marketplace requirements."""
        errors = []
        basic_info = product_info.get("basic_info", {})
        
        # Check required fields
        if template.get("requires_brand") and not basic_info.get("brand_name"):
            errors.append("Brand name is required for this marketplace")
            
        if template.get("requires_price") and not basic_info.get("price"):
            errors.append("Price is required for this marketplace")
            
        if template.get("requires_category") and not basic_info.get("category"):
            errors.append("Category is required for this marketplace")
            
        # Check minimum requirements
        if not basic_info.get("product_name"):
            errors.append("Product name is required")
            
        if not basic_info.get("description"):
            errors.append("Product description is required")
            
        if not product_info.get("features"):
            errors.append("At least one feature is required")
            
        return errors
    
    def _process_template_variables(self, product_info: Dict[str, Any], template: Dict[str, Any]) -> Dict[str, str]:
        """Process and validate template variables."""
        basic_info = product_info.get("basic_info", {})
        features = product_info.get("features", [])
        usps = product_info.get("usps", [])
        
        # Format features and USPs
        formatted_features = self._format_features(features)
        formatted_features_bullets = self._format_features(features, template.get("max_bullets"))
        
        # Prepare template variables with defaults
        return {
            "brand": basic_info.get("brand_name", ""),
            "product_name": basic_info.get("product_name", ""),
            "key_features": ", ".join(features[:3]) if features else "",
            "product_description": basic_info.get("description", ""),
            "features": formatted_features,
            "features_bullets": formatted_features_bullets,
            "usps": "\n".join(usps) if usps else "",
            "usps_bullets": self._format_features(usps, 3),
            "specifications": self._format_specifications(product_info.get("specifications", {})),
            "additional_notes": basic_info.get("additional_notes", ""),
            "material_care": basic_info.get("material_care", "Not specified"),
            "usage_instructions": basic_info.get("usage_instructions", "Refer to product packaging for usage instructions"),
            "ingredients": basic_info.get("ingredients", "Refer to product packaging for full ingredient list")
        }
    
    def generate_marketplace_content(self, 
                                   product_info: Dict[str, Any], 
                                   marketplace_key: str) -> Dict[str, Any]:
        """
        Generate content for a specific marketplace.
        
        Args:
            product_info: Dictionary containing product information
            marketplace_key: Key identifying the marketplace (e.g., 'amazon_in')
            
        Returns:
            Dictionary containing the generated content or error information
        """
        # Get marketplace template
        template = self.MARKETPLACE_TEMPLATES.get(marketplace_key)
        if not template:
            error_msg = f"No template found for marketplace: {marketplace_key}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        
        try:
            # Validate product info against marketplace requirements
            validation_errors = self._validate_product_info(product_info, template)
            if validation_errors:
                error_msg = f"Validation failed: {'; '.join(validation_errors)}"
                logger.warning(f"{marketplace_key}: {error_msg}")
                return {"success": False, "error": error_msg, "validation_errors": validation_errors}
            
            # Process template variables
            template_vars = self._process_template_variables(product_info, template)
            
            # Generate title with length validation
            title = template["title"].format(**template_vars)
            if len(title) > template["max_title_length"]:
                logger.warning(f"Truncating title for {marketplace_key} (original length: {len(title)})")
                title = title[:template["max_title_length"] - 3] + "..."
            
            # Generate description with error handling for missing variables
            try:
                description = template["description"].format(**template_vars)
            except KeyError as ke:
                error_msg = f"Missing required template variable: {str(ke)}"
                logger.error(f"{marketplace_key}: {error_msg}")
                return {"success": False, "error": error_msg}
            
            # Generate bullet points if required
            bullet_points = []
            if template.get("max_bullets") and product_info.get("features"):
                bullet_points = product_info["features"][:template["max_bullets"]]
            
            # Generate SEO keywords
            try:
                keywords = self._generate_keywords(
                    product_name=template_vars["product_name"],
                    brand=template_vars["brand"],
                    category=product_info.get("basic_info", {}).get("category", ""),
                    features=product_info.get("features", [])
                )
            except Exception as e:
                logger.warning(f"Failed to generate keywords for {marketplace_key}: {str(e)}")
                keywords = []
            
            # Prepare result
            result = {
                "success": True,
                "marketplace": marketplace_key,
                "marketplace_name": template.get("name", marketplace_key),
                "title": title,
                "description": description,
                "bullet_points": bullet_points,
                "keywords": keywords,
                "specifications": product_info.get("specifications", {}) if template.get("requires_technical_specs") else {},
                "template": template
            }
            
            logger.info(f"Successfully generated content for {marketplace_key}")
            return result
            
        except Exception as e:
            error_msg = f"Unexpected error generating content for {marketplace_key}: {str(e)}"
            logger.exception(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "marketplace": marketplace_key,
                "marketplace_name": template.get("name", marketplace_key)
            }
    
    def _generate_keywords(self, 
                         product_name: str, 
                         brand: str,
                         category: str,
                         features: List[str]) -> List[str]:
        """Generate SEO keywords for the product."""
        # Start with basic keywords
        keywords = set()
        
        # Add product name and brand
        keywords.update(product_name.lower().split())
        keywords.add(brand.lower())
        
        # Add category and subcategories
        if category:
            keywords.update(category.lower().split())
        
        # Add features as keywords
        for feature in features:
            keywords.update(feature.lower().split())
        
        # Add common e-commerce keywords
        keywords.update(["buy", "sale", "discount", "best price", "online"])
        
        # Convert to list and clean up
        keywords = [k.strip() for k in keywords if len(k) > 2 and k.strip()]
        
        # Limit to top 20 keywords
        return keywords[:20]
    
    def generate_all_marketplace_content(self, 
                                       product_info: Dict[str, Any], 
                                       marketplace_keys: List[str]) -> Dict[str, Any]:
        """
        Generate content for multiple marketplaces.
        
        Args:
            product_info: Dictionary containing product information
            marketplace_keys: List of marketplace keys
            
        Returns:
            Dictionary mapping marketplace keys to their generated content
        """
        results = {}
        
        for marketplace in marketplace_keys:
            result = self.generate_marketplace_content(product_info, marketplace)
            results[marketplace] = result
        
        return {
            "success": True,
            "results": results
        }


# Singleton instance
marketplace_service = MarketplaceService()
