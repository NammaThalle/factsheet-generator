# AI Solutions Engineer Take-Home: Implementation Plan

## Project Overview
**Objective**: Build a Python pipeline that generates 600-1000 word Markdown factsheets for companies based on their web presence, optimized for sales discovery calls.

**Timeline**: ~4 focused hours  
**Budget**: $50 OpenAI API credit (5 days)  
**Target**: Working prototype with one sample factsheet

## System Architecture

### Core Components
1. **Web Scraper Module** (`scraper.py`)
   - Extract content from company homepage and About page
   - Handle common web scraping challenges (rate limits, blocked requests)
   - Fallback mechanisms for missing pages

2. **Content Synthesizer** (`synthesizer.py`)
   - OpenAI API integration for content generation
   - Cost-efficient prompt engineering
   - Structured factsheet generation

3. **Pipeline Orchestrator** (`main.py`)
   - CLI interface accepting single URL
   - End-to-end processing workflow
   - Error handling and logging

### Data Strategy

**Primary Sources**:
- Company homepage (hero section, key messaging)
- About page (mission, history, team info)
- Contact/locations page (if available)

**Key Data Points for Sales Factsheets**:
- **Company Overview**: Mission, vision, founding story
- **Products/Services**: Core offerings and value propositions
- **Target Market**: Customer segments and industries served
- **Competitive Advantages**: Unique selling points and differentiators
- **Company Details**: Size indicators, locations, contact info
- **Recent Developments**: News, growth indicators, partnerships

**Rationale**: Sales reps need actionable intelligence to personalize discovery calls. Focus on business context, market positioning, and conversation starters rather than technical specifications.

## Technical Implementation

### Technology Stack
```
Core Dependencies:
- requests: HTTP client for web scraping
- beautifulsoup4: HTML parsing and content extraction
- openai: GPT API integration
- python-dotenv: Environment variable management
- argparse: CLI interface

Development/Optional:
- lxml: Fast XML/HTML parser
- urllib3: Advanced HTTP features
- typing: Type hints for code clarity
```

### Project Structure
```
factsheet-generator/
├── README.md                 # Setup instructions & design rationale
├── requirements.txt          # Python dependencies
├── companies.csv            # Input company list
├── .env.example            # Environment template
├── src/
│   ├── __init__.py
│   ├── scraper.py          # Web scraping functionality
│   ├── synthesizer.py      # OpenAI integration
│   ├── main.py             # CLI entry point
│   └── utils.py            # Shared utilities
└── sample-company.md       # Generated factsheet example
```

### Success Metrics
- **Functional**: Generates coherent 600-1000 word factsheet
- **Quality**: Sales-relevant content with clear structure
- **Cost**: Stays within $50 OpenAI budget
- **Reliability**: Handles missing data gracefully
- **Usability**: Simple CLI with clear instructions

## Implementation Phases

### Phase 1: Foundation (30 minutes)
- Set up project structure
- Create requirements.txt and basic CLI
- Implement companies.csv with provided data
- Test basic setup and imports

### Phase 2: Web Scraping (60 minutes)
- Build robust scraper for homepage + About page
- Handle common edge cases (404s, rate limits, redirects)
- Extract structured data (text content, metadata)
- Test against sample companies

### Phase 3: AI Integration (90 minutes)
- Design cost-efficient OpenAI prompts
- Implement factsheet generation with structured output
- Add content validation and word count management
- Optimize for GPT-3.5-turbo vs GPT-4 cost/quality tradeoffs

### Phase 4: Integration & Testing (60 minutes)
- Build end-to-end pipeline
- Generate sample factsheet for one company
- Error handling and edge case management
- Final testing and refinement

### Phase 5: Documentation (30 minutes)
- Write comprehensive README
- Document design decisions and tradeoffs
- Include setup instructions and usage examples
- Prepare GitHub repository

## Risk Mitigation

**Web Scraping Challenges**:
- Rate limiting: Implement delays and respectful crawling
- Blocked requests: User-agent rotation and fallback strategies
- Missing pages: Graceful degradation with available content

**AI Cost Management**:
- Use GPT-3.5-turbo for initial processing (cheaper)
- Optimize prompts to minimize token usage
- Implement content chunking for large inputs

**Content Quality**:
- Structured prompts with clear formatting requirements
- Content validation and fallback generation
- Human-readable error messages for debugging

## Design Decisions & Tradeoffs

**Scope Prioritization**:
- **Focus**: Working end-to-end prototype over comprehensive features
- **Quality**: Sales-relevant insights over exhaustive company data
- **Efficiency**: Simple, reliable implementation over advanced optimization

**Technology Choices**:
- **BeautifulSoup vs Scrapy**: BS4 for simplicity and quick development
- **OpenAI vs Local Models**: OpenAI for reliability within budget constraints
- **CLI vs Web Interface**: CLI for simplicity and testing ease

**Content Strategy**:
- **Sales-First**: Prioritize actionable intelligence for discovery calls
- **Structured Output**: Consistent format for easy consumption
- **Graceful Degradation**: Useful output even with limited data

## Expected Challenges

1. **Website Variability**: Different site structures require flexible parsing
2. **Content Quality**: Balancing comprehensiveness with coherence
3. **API Costs**: Managing OpenAI usage within budget constraints
4. **Time Constraints**: Delivering working prototype within 4 hours

## Success Definition

**Minimum Viable Product**:
- Accepts company URL and generates factsheet
- Produces 600-1000 word Markdown output
- Includes sales-relevant business intelligence
- Runs reliably with clear error handling

**Stretch Goals**:
- Support for multiple companies in batch
- Enhanced data enrichment from additional sources
- Configurable factsheet templates
- Performance optimization and caching