"""
AI Synthesis Module

Generates business intelligence factsheets using OpenAI GPT models.
"""

import os
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
from logger import logger

load_dotenv()

class FactsheetSynthesizer:
    def __init__(self, model=None):
        self.provider = "openai"
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model or "gpt-4o-mini"
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY environment variable not set")
    
    def create_synthesis_prompt(self, company_data):
        """Create a structured prompt for factsheet generation with anti-hallucination safeguards"""
        homepage = company_data.get('homepage', {})
        about = company_data.get('about', {})
        url = company_data.get('url', '')
        
        # Load the template
        template_path = Path(__file__).parent / "factsheet_template.md"
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
        except Exception:
            logger.warning("Could not load factsheet template, using fallback")
            template_content = "# [Company Name] - Sales Intelligence Factsheet\n\n[Use template structure]"
        
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
        
        prompt = f"""Create a sales intelligence factsheet using the website content provided. Extract specific, actionable information.

Website: {url}
Content: {content_text}

Follow this template exactly:
{template_content}

CRITICAL RULES:
1. Use SPECIFIC information from the website content
2. NO placeholder text like "[Target Market]" or generic templates
3. NO generic conversation starters - make them specific to this company
4. Extract actual company details, not industry generics
5. Keep responses concise but informative
6. Target 800-900 words total only. Should not exceed this limit at any cost

SMART EXTRACTION:
- Mission: Look for taglines, "About" messaging, company purpose statements
- Business Model: Infer from pricing, products, how they operate
- Pain Points: What problems do their solutions specifically solve?
- Conversation Starters: Based on their actual products/services

EXAMPLES:
✅ GOOD: "How are you currently handling international payment processing?" (for Stripe)
✅ GOOD: "Mission: Increase the GDP of the internet" (Stripe's actual tagline)
❌ BAD: "Are you looking for [service] solutions?" (generic template)
❌ BAD: "[Target Market] companies" (placeholder)

Only use fallback phrases when information is genuinely not extractable from content."""

        return prompt
    
    def generate_factsheet(self, company_data):
        """Generate factsheet using OpenAI"""
        try:
            prompt = self.create_synthesis_prompt(company_data)
            
            logger.info(f"Generating factsheet for {company_data.get('url')} using OpenAI")
            
            return self._generate_with_openai(prompt)
                
        except Exception as e:
            logger.error(f"Error generating factsheet: {str(e)}")
            return None
    
    def _generate_with_openai(self, prompt):
        """Generate factsheet using OpenAI with evidence-based approach"""
        # GPT-5 models don't support temperature parameter
        kwargs = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a business analyst creating evidence-based sales intelligence factsheets. Only use information directly stated in the provided content."},
                {"role": "user", "content": prompt}
            ]
        }
        
        # Only add temperature for non-GPT-5 models
        if "gpt-5" not in self.model.lower():
            kwargs["temperature"] = 0.2
            
        response = self.client.chat.completions.create(**kwargs)
        
        content = response.choices[0].message.content
        factsheet = content.strip() if content else ""
        factsheet = self._clean_factsheet_output(factsheet)
        word_count = len(factsheet.split())
        logger.info(f"Generated factsheet with {word_count} words using OpenAI")
        return factsheet
    
    
    def _clean_factsheet_output(self, factsheet):
        """Clean and post-process the generated factsheet"""
        if not factsheet:
            return factsheet
            
        # Remove markdown code block markers that shouldn't be there
        factsheet = factsheet.replace('```markdown', '').replace('```', '')
        
        # Remove any leading/trailing whitespace
        factsheet = factsheet.strip()
        
        # Ensure proper title format (remove any duplicate titles)
        lines = factsheet.split('\n')
        cleaned_lines = []
        title_found = False
        
        for line in lines:
            line = line.strip()
            if not line:
                cleaned_lines.append('')
                continue
                
            # Skip duplicate titles after the first one
            if line.startswith('# ') and 'Sales Intelligence Factsheet' in line:
                if title_found:
                    continue
                title_found = True
            
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)

def create_factsheet(company_data, model=None):
    """Main function to create factsheet from company data"""
    synthesizer = FactsheetSynthesizer(model=model)
    return synthesizer.generate_factsheet(company_data)