import os
import logging
from openai import OpenAI
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FactsheetSynthesizer:
    def __init__(self, provider="gemini", model=None):
        self.provider = provider.lower()
        
        if self.provider == "openai":
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            self.model = model or "gpt-3.5-turbo"
            if not os.getenv("OPENAI_API_KEY"):
                raise ValueError("OPENAI_API_KEY environment variable not set")
                
        elif self.provider == "gemini":
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            self.model = model or "gemini-pro"
            if not os.getenv("GEMINI_API_KEY"):
                raise ValueError("GEMINI_API_KEY environment variable not set")
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def create_synthesis_prompt(self, company_data):
        """Create a structured prompt for factsheet generation"""
        homepage = company_data.get('homepage', {})
        about = company_data.get('about', {})
        url = company_data.get('url', '')
        
        # Combine available content
        content_parts = []
        
        if homepage.get('title'):
            content_parts.append(f"Website Title: {homepage['title']}")
        
        if homepage.get('description'):
            content_parts.append(f"Meta Description: {homepage['description']}")
        
        if homepage.get('content'):
            content_parts.append(f"Homepage Content: {homepage['content'][:1500]}")
        
        if about.get('content'):
            content_parts.append(f"About Page: {about['content'][:1500]}")
        
        content_text = "\n\n".join(content_parts)
        
        prompt = f"""Create a comprehensive business factsheet for sales representatives preparing for discovery calls.

Company Website: {url}

Available Information:
{content_text}

Create a 600-1000 word factsheet in Markdown format covering:
1. Company Overview (mission, value propositions)
2. Products & Services (offerings, target markets)  
3. Business Intelligence (size, market position)
4. Sales Insights (conversation starters, potential pain points)

Focus on actionable intelligence for sales conversations."""

        return prompt
    
    def generate_factsheet(self, company_data):
        """Generate factsheet using specified AI provider"""
        try:
            prompt = self.create_synthesis_prompt(company_data)
            
            logger.info(f"Generating factsheet for {company_data.get('url')} using {self.provider}")
            
            if self.provider == "openai":
                return self._generate_with_openai(prompt)
            elif self.provider == "gemini":
                return self._generate_with_gemini(prompt)
                
        except Exception as e:
            logger.error(f"Error generating factsheet: {str(e)}")
            return None
    
    def _generate_with_openai(self, prompt):
        """Generate factsheet using OpenAI"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a business analyst creating sales intelligence factsheets."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1200
        )
        
        factsheet = response.choices[0].message.content.strip()
        word_count = len(factsheet.split())
        logger.info(f"Generated factsheet with {word_count} words using OpenAI")
        return factsheet
    
    def _generate_with_gemini(self, prompt):
        """Generate factsheet using Gemini"""
        model = genai.GenerativeModel(self.model)
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,
                max_output_tokens=1200
            )
        )
        
        factsheet = response.text.strip()
        word_count = len(factsheet.split())
        logger.info(f"Generated factsheet with {word_count} words using Gemini")
        return factsheet

def create_factsheet(company_data, provider="gemini", model=None):
    """Main function to create factsheet from company data"""
    synthesizer = FactsheetSynthesizer(provider=provider, model=model)
    return synthesizer.generate_factsheet(company_data)