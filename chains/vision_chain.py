"""Vision chain for extracting product information from images."""
from typing import Dict, Any, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import base64
from PIL import Image
import io

class VisionChain:
    """Chain for extracting product information from images using GPT-4 Vision."""
    
    def __init__(self, api_key: str):
        """Initialize the vision chain."""
        self.llm = ChatOpenAI(
            model="gpt-4-vision-preview",
            max_tokens=1000,
            temperature=0.1,
            api_key=api_key
        )
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert product information extractor. 
            Analyze the product image and extract the following details:
            - Product name
            - Brand name (if visible)
            - Key features (materials, colors, size, etc.)
            - Any visible text or labels
            - Product category (if identifiable)
            - Any unique selling points visible in the image
            
            Format your response as a JSON object with these fields:
            {{
                "product_name": "...",
                "brand_name": "...",
                "features": ["...", "..."],
                "visible_text": "...",
                "category": "...",
                "usps": ["...", "..."]
            }}"""),
            ("human", [{"type": "text", "text": "Extract product information from this image."},
                      {"type": "image_url", "image_url": {"url": "{image_url}"}}])
        ])
        
        self.chain = self.prompt | self.llm | StrOutputParser()
    
    def process_image(self, image_data: bytes) -> Dict[str, Any]:
        """Process an image and extract product information."""
        try:
            # Convert image to base64
            base64_image = base64.b64encode(image_data).decode('utf-8')
            image_url = f"data:image/jpeg;base64,{base64_image}"
            
            # Get response from the model
            response = self.chain.invoke({"image_url": image_url})
            
            # Parse the response (assuming it's in JSON format)
            import json
            return json.loads(response.strip())
            
        except Exception as e:
            return {"error": f"Error processing image: {str(e)}"}
    
    def __call__(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Process the image from the input dictionary."""
        if 'image' not in inputs or inputs['image'] is None:
            return {"vision_data": None}
            
        try:
            # Read the uploaded file
            image_data = inputs['image'].read()
            result = self.process_image(image_data)
            return {"vision_data": result}
        except Exception as e:
            return {"vision_data": {"error": str(e)}}
