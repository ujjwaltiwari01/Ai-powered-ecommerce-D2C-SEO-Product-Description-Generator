"""Chain for merging data from multiple sources."""
from typing import Dict, Any, List, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import json

class MergeChain:
    """Chain for merging data from multiple sources into a unified format."""
    
    def __init__(self, llm):
        """Initialize the merge chain."""
        self.llm = llm
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at merging and normalizing product information from multiple sources. 
            Combine the following information into a single, coherent product brief:
            
            Product Information:
            {product_info}
            
            Vision Analysis (from product image):
            {vision_data}
            
            Audio Transcription (from voice note):
            {audio_transcript}
            
            Create a comprehensive product brief that includes:
            1. Product name (most descriptive from available sources)
            2. Brand name (from form or image)
            3. Category (most specific from available sources)
            4. Key features (consolidated list, removing duplicates)
            5. Target audience (from form or inferred)
            6. Unique selling points (from form, image, or audio)
            7. Any additional notes or specifications
            
            Format your response as a JSON object with these fields:
            {{
                "product_name": "...",
                "brand_name": "...",
                "category": "...",
                "description": "...",
                "features": ["...", "..."],
                "target_audience": "...",
                "usps": ["...", "..."],
                "specifications": {{
                    "dimensions": "...",
                    "weight": "...",
                    "materials": ["..."],
                    "colors": ["..."]
                }},
                "additional_notes": "..."
            }}""")
        ])
        
        self.chain = self.prompt | self.llm | StrOutputParser()
    
    def _format_inputs(self, inputs: Dict[str, Any]) -> Dict[str, str]:
        """Format the inputs for the prompt."""
        product_info = inputs.get('product_info', {})
        vision_data = inputs.get('vision_data', {})
        audio_transcript = inputs.get('audio_transcript', "")
        
        # Format product info
        formatted_product_info = ""
        if product_info:
            basic_info = product_info.get('basic_info', {})
            features = product_info.get('features', [])
            
            formatted_product_info = f"""
            Basic Information:
            - Brand: {basic_info.get('brand_name', 'Not provided')}
            - Product Name: {basic_info.get('product_name', 'Not provided')}
            - Category: {basic_info.get('category', 'Not provided')}
            - Target Audience: {basic_info.get('target_audience', 'Not specified')}
            - Unique Selling Proposition: {basic_info.get('usp', 'Not specified')}
            - Price: {basic_info.get('price', 'Not specified')} {basic_info.get('currency', '')}
            
            Features:
            """
            formatted_product_info += "\n".join([f"- {feature}" for feature in features])
        
        # Format vision data
        formatted_vision = "No image analysis available."
        if vision_data and not isinstance(vision_data, str) and 'error' not in vision_data:
            formatted_vision = "\n".join([f"- {k}: {v}" for k, v in vision_data.items()])
        
        # Format audio transcript
        formatted_audio = audio_transcript if audio_transcript else "No audio notes provided."
        
        return {
            "product_info": formatted_product_info,
            "vision_data": formatted_vision,
            "audio_transcript": formatted_audio
        }
    
    def _parse_output(self, output: str) -> Dict[str, Any]:
        """Parse the output from the LLM."""
        try:
            # Try to parse as JSON
            return json.loads(output.strip())
        except json.JSONDecodeError:
            # If parsing fails, try to extract JSON from the output
            try:
                # Look for JSON-like content in the output
                start = output.find('{')
                end = output.rfind('}') + 1
                if start >= 0 and end > start:
                    return json.loads(output[start:end])
                raise ValueError("Could not parse output as JSON")
            except Exception:
                # If all else fails, return the raw output with an error flag
                return {
                    "error": "Failed to parse model output",
                    "raw_output": output
                }
    
    def __call__(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Merge the inputs into a unified product brief."""
        try:
            # Format inputs for the prompt
            formatted_inputs = self._format_inputs(inputs)
            
            # Get response from the model
            response = self.chain.invoke(formatted_inputs)
            
            # Parse the response
            merged_data = self._parse_output(response)
            
            return {"merged_data": merged_data}
            
        except Exception as e:
            return {"error": f"Error in MergeChain: {str(e)}"}


def create_merge_chain(llm):
    """Create a merge chain with the given LLM."""
    return MergeChain(llm)
