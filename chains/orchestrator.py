"""Main orchestrator for the product description generation pipeline."""
from typing import Dict, Any, List, Optional
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import JsonOutputParser
import json

class ProductDescriptionOrchestrator:
    """Orchestrates the product description generation pipeline."""
    
    def __init__(self, vision_chain, merge_chain, marketplace_chain, seo_chain=None):
        """Initialize the orchestrator with the required chains."""
        self.vision_chain = vision_chain
        self.merge_chain = merge_chain
        self.marketplace_chain = marketplace_chain
        self.seo_chain = seo_chain
    
    def _process_vision(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Process image data if available."""
        if 'media' in inputs and 'image' in inputs['media'] and inputs['media']['image'] is not None:
            return self.vision_chain({"image": inputs['media']['image']})
        return {"vision_data": None}
    
    def _process_audio(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Process audio data if available."""
        # Placeholder for audio processing
        # In a real implementation, this would use Whisper or similar
        return {"audio_transcript": ""}
    
    def _merge_data(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Merge data from different sources."""
        # Get results from previous steps
        vision_result = inputs.get('vision_result', {})
        audio_result = inputs.get('audio_result', {})
        
        # Prepare inputs for merge chain
        merge_inputs = {
            'product_info': inputs.get('product_info', {}),
            'vision_data': vision_result.get('vision_data'),
            'audio_transcript': audio_result.get('transcript', '')
        }
        
        # Call merge chain
        return self.merge_chain(merge_inputs)
    
    def _generate_marketplace_content(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate content for each selected marketplace."""
        merged_data = inputs.get('merged_data', {})
        marketplaces = inputs.get('marketplaces', [])
        
        results = {}
        for marketplace in marketplaces:
            marketplace_key = marketplace['key']
            
            # Prepare inputs for marketplace chain
            marketplace_inputs = {
                'marketplace_key': marketplace_key,
                'product_info': merged_data
            }
            
            # Call marketplace chain
            result = self.marketplace_chain(marketplace_inputs)
            results[marketplace_key] = result.get(marketplace_key, {})
        
        return {"marketplace_results": results}
    
    def _format_output(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Format the final output."""
        return {
            "status": "success",
            "product_info": inputs.get('product_info', {}),
            "marketplace_results": inputs.get('marketplace_results', {})
        }
    
    def get_chain(self):
        """Create and return the complete processing chain."""
        # Define the processing steps
        chain = (
            RunnablePassthrough()
            | {
                # Process image in parallel with audio
                "vision_result": self._process_vision,
                "audio_result": self._process_audio,
                # Pass through the original inputs
                "product_info": lambda x: x.get('product_info', {}),
                "marketplaces": lambda x: x.get('marketplaces', [])
            }
            | {
                # Merge the data
                "merged_data": self._merge_data,
                # Pass through the marketplaces
                "marketplaces": lambda x: x.get('marketplaces', []),
                # Pass through the original product info
                "product_info": lambda x: x.get('product_info', {})
            }
            | {
                # Generate marketplace content
                "marketplace_results": self._generate_marketplace_content,
                # Pass through the product info
                "product_info": lambda x: x.get('product_info', {})
            }
            | self._format_output
        )
        
        return chain


def create_orchestrator(vision_chain, merge_chain, marketplace_chain, seo_chain=None):
    """Create and return an instance of the orchestrator."""
    return ProductDescriptionOrchestrator(
        vision_chain=vision_chain,
        merge_chain=merge_chain,
        marketplace_chain=marketplace_chain,
        seo_chain=seo_chain
    )
