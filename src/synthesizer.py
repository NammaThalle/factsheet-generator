import os
import logging
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FactsheetSynthesizer:
    def __init__(self, model="gpt-3.5-turbo"):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model
        
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY environment variable not set")
    
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
        """Generate factsheet using OpenAI"""
        try:
            prompt = self.create_synthesis_prompt(company_data)
            
            logger.info(f"Generating factsheet for {company_data.get('url')}")
            
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
            
            logger.info(f"Generated factsheet with {word_count} words")
            return factsheet
            
        except Exception as e:
            logger.error(f"Error generating factsheet: {str(e)}")
            return None

def create_factsheet(company_data, model="gpt-3.5-turbo"):
    """Main function to create factsheet from company data"""
    synthesizer = FactsheetSynthesizer(model=model)
    return synthesizer.generate_factsheet(company_data)