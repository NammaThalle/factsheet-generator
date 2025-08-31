"""
Streamlit Web Frontend

Interactive web interface for the Company Factsheet Generator.
Features dashboard, generator, and viewer pages with real-time analytics.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import sys
import os
from src.logger import logger

sys.path.append(os.path.join(os.path.dirname(__file__), "../shared"))
from utils import APIClient, wait_for_task_completion, format_file_size, validate_url, normalize_url, get_company_name_from_url

# OpenAI models for factsheet generation
OPENAI_MODELS = {
    'gpt-5-nano': 'gpt-5-nano-2025-08-07',
    'gpt-4o-mini': 'gpt-4o-mini-2024-07-18',
    'gpt-4o': 'gpt-4o-2024-11-20',
    'gpt-5-mini': 'gpt-5-mini-2025-08-07',
    'gpt-4-turbo': 'gpt-4-turbo-2024-04-09',
    'gpt-5': 'gpt-5-2025-08-07', 
}

# Page config
st.set_page_config(
    page_title="Factsheet Generator",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize API client
@st.cache_resource
def get_api_client():
    return APIClient()

api_client = get_api_client()

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #1f77b4;
    }
    
    .factsheet-card {
        border: 1px solid #ddd;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
        background-color: #fafafa;
    }
    
    .success-message {
        color: #28a745;
        font-weight: bold;
    }
    
    .error-message {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def check_api_health():
    """Check if API is running"""
    if not api_client.health_check():
        logger.error("**Backend API is not running!**")
        st.markdown("""
        Please start the FastAPI backend:
        ```bash
        cd web/backend
        python app.py
        ```
        """)
        return False
    return True

def show_dashboard():
    """Show the main dashboard"""
    st.markdown('<h1 class="main-header">Factsheet Generator Dashboard</h1>', unsafe_allow_html=True)
    
    if not check_api_health():
        return
    
    try:
        # Get factsheets data
        data = api_client.list_factsheets()
        factsheets = data['factsheets']
        total = data['total']
        
        # Metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Factsheets", total)
        
        with col2:
            if factsheets:
                avg_words = sum(f['word_count'] for f in factsheets) / len(factsheets)
                st.metric("Avg Word Count", f"{avg_words:.0f}")
            else:
                st.metric("Avg Word Count", "0")
        
        with col3:
            if factsheets:
                total_size = sum(f['file_size'] for f in factsheets)
                st.metric("Total Size", format_file_size(total_size))
            else:
                st.metric("Total Size", "0 B")
        
        with col4:
            today_count = len([f for f in factsheets if f['created_at'].startswith(datetime.now().strftime('%Y-%m-%d'))])
            st.metric("Created Today", today_count)
        
        if factsheets:
            # Charts
            st.subheader("Analytics")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Word count distribution
                word_counts = [f['word_count'] for f in factsheets]
                fig = px.histogram(
                    x=word_counts,
                    nbins=10,
                    title="Word Count Distribution",
                    labels={'x': 'Word Count', 'y': 'Number of Factsheets'}
                )
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Creation timeline
                df = pd.DataFrame(factsheets)
                df['date'] = pd.to_datetime(df['created_at']).dt.date
                daily_counts = df.groupby('date').size().reset_index(name='count')
                
                fig = px.line(
                    daily_counts,
                    x='date',
                    y='count',
                    title="Factsheets Created Over Time",
                    markers=True
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Recent factsheets
            st.subheader("Recent Factsheets")
            
            # Create a nice table display
            for factsheet in factsheets[:5]:  # Show latest 5
                with st.container():
                    col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                    
                    with col1:
                        st.markdown(f"**{factsheet['company_name']}**")
                        st.caption(factsheet['url'])
                    
                    with col2:
                        st.text(f"Words: {factsheet['word_count']}")
                        st.caption(datetime.fromisoformat(factsheet['created_at'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M'))
                    
                    with col3:
                        if st.button("View", key=f"view_{factsheet['filename']}"):
                            st.session_state.selected_factsheet = factsheet['filename']
                            st.session_state.page = "viewer"
                            st.rerun()
                    
                    with col4:
                        if st.button("Delete", key=f"delete_{factsheet['filename']}"):
                            try:
                                api_client.delete_factsheet(factsheet['filename'])
                                st.success("Factsheet deleted!")
                                st.rerun()
                            except Exception as e:
                                logger.error(f"Error deleting factsheet: {e}")
                    
                    st.divider()
        else:
            logger.info("No factsheets generated yet. Use the Generator to create your first one!")
            st.info("No factsheets generated yet. Use the Generator to create your first one!")
    
    except Exception as e:
        logger.error(f"Error loading dashboard: {e}")

def show_generator():
    st.markdown('<h1 class="main-header">Generate New Factsheet</h1>', unsafe_allow_html=True)
    logger.info("show_generator() called")
    
    if not check_api_health():
        logger.error("API health check failed")
        return
    logger.info("API health check passed")
    
    st.markdown("""
    <style>
    .generator-section {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 1px solid #e9ecef;
    }
    .form-row {
        margin-bottom: 1.5rem;
    }
    .generate-btn {
        background: linear-gradient(45deg, #007bff, #0056b3);
        color: white;
        padding: 0.75rem 2rem;
        border: none;
        border-radius: 5px;
        font-weight: 600;
        cursor: pointer;
        width: 100%;
        margin-top: 1rem;
    }
    .progress-section {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #007bff;
    }
    </style>
    """, unsafe_allow_html=True)
    
    with st.form("factsheet_generator"):
        st.subheader("Company Information")
        
        url = st.text_input(
            "Company Website URL",
            placeholder="Enter domain (e.g., stripe.com, openai.com)",
            help="Enter the company's main website domain"
        )
        
        st.subheader("Model Configuration")
        
        if OPENAI_MODELS:
            logger.info(f"Processing {len(OPENAI_MODELS)} models")
            model_display_names = list(OPENAI_MODELS.keys())
            
            selected_model_key = st.selectbox(
                "OpenAI Model",
                model_display_names,
                help="Select an OpenAI model for factsheet generation"
            )
            
            logger.info(f"Selected model key: {selected_model_key}")
            selected_model = OPENAI_MODELS[selected_model_key]
            logger.info(f"Selected model ID: {selected_model}")
        else:
            logger.error("No OpenAI models available")
            st.warning("No OpenAI models available")
            if not os.getenv("OPENAI_API_KEY"):
                logger.error("OpenAI API key not found")
            selected_model = None
        
        submitted = st.form_submit_button(
            "Generate Factsheet",
            type="primary",
            use_container_width=True
        )
        
        if submitted:
            if not url:
                logger.error("Please enter a company URL")
            elif not selected_model:
                logger.error("Please select a model")
            else:
                normalized_url = normalize_url(url)
                if not validate_url(url):
                    logger.error("Please enter a valid company domain")
                else:
                    try:
                        with st.spinner("Starting factsheet generation..."):
                            response = api_client.generate_factsheet(
                                url=normalized_url,
                                model=selected_model
                            )
                        
                        task_id = response['task_id']
                        st.success(f"Generation started! Task ID: {task_id}")
                        
                        with st.container():
                            st.subheader("Generation Progress")
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                        
                        try:
                            result = wait_for_task_completion(api_client, task_id, progress_bar, status_text)
                            
                            st.success("Factsheet generated successfully!")
                            
                            st.session_state.generation_completed = True
                            st.session_state.completed_filename = result['result']['filename']
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Company", result['result']['company_name'])
                            with col2:
                                st.metric("Word Count", result['result']['word_count'])
                            with col3:
                                st.metric("Status", "Complete")
                                
                        except Exception as e:
                            error_message = str(e)
                            logger.error(f"Generation failed: {error_message}")
                            
                            # Show user-friendly error messages
                            if "Failed to scrape" in error_message:
                                if "timed out" in error_message.lower():
                                    st.error("Website took too long to respond. This website might be blocking automated requests or experiencing issues.")
                                else:
                                    st.error("Unable to access the website. Please check the URL or try a different website.")
                            elif "Connection error" in error_message:
                                st.error("Network connection error. Please check your internet connection and try again.")
                            else:
                                st.error(f"Generation failed: {error_message}")
                                
                    except Exception as e:
                        error_message = str(e)
                        logger.error(f"Error starting generation: {error_message}")
                        st.error(f"Failed to start generation: {error_message}")
    
    if st.session_state.get('generation_completed', False):
        st.markdown("---")
        if st.button(
            "View Generated Factsheet",
            type="secondary",
            use_container_width=True
        ):
            st.session_state.selected_factsheet = st.session_state.completed_filename
            st.session_state.page = "viewer"
            st.session_state.generation_completed = False
            st.rerun()

def show_viewer():
    """Show factsheet viewer"""
    st.markdown('<h1 class="main-header">Factsheet Viewer</h1>', unsafe_allow_html=True)
    
    if not check_api_health():
        return
    
    # Get selected factsheet from session state
    selected_filename = st.session_state.get('selected_factsheet')
    
    if not selected_filename:
        logger.info("No factsheet selected. Go to Dashboard to select one.")
        st.info("No factsheet selected. Go to Dashboard to select one.")
        return
    
    try:
        # Get factsheet content
        factsheet_data = api_client.get_factsheet(selected_filename)
        metadata = factsheet_data['metadata']
        content = factsheet_data['content']
        
        # Header with metadata
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.subheader(metadata['company_name'])
            st.caption(f"Website: {metadata['url']}")
        
        with col2:
            st.metric("Word Count", metadata['word_count'])
            st.caption(f"Created: {datetime.fromisoformat(metadata['created_at'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M')}")
        
        with col3:
            # Download button
            file_content = api_client.download_factsheet(selected_filename)
            st.download_button(
                "Download",
                data=file_content,
                file_name=selected_filename,
                mime="text/markdown"
            )
        
        st.divider()
        
        # Display factsheet content
        # Remove markdown code fence if present
        display_content = content
        if display_content.startswith('```markdown\n'):
            display_content = display_content[12:]  # Remove ```markdown\n
        if display_content.endswith('\n```'):
            display_content = display_content[:-4]  # Remove \n```
            
        with st.container():
            st.markdown(display_content)
        
    except Exception as e:
        logger.error(f"Error loading factsheet: {e}")

def main():
    """Main application"""
    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = 'dashboard'
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    
    pages = {
        "Dashboard": "dashboard",
        "Generator": "generator", 
        "Viewer": "viewer"
    }
    
    for page_name, page_key in pages.items():
        if st.sidebar.button(page_name, key=f"nav_{page_key}"):
            st.session_state.page = page_key
            st.rerun()
    
    # Show API status in sidebar
    st.sidebar.divider()
    st.sidebar.subheader("System Status")
    
    if api_client.health_check():
        st.sidebar.success("API: Online")
    else:
        st.sidebar.error("API: Offline")
    
    # Main content
    if st.session_state.page == "dashboard":
        show_dashboard()
    elif st.session_state.page == "generator":
        show_generator()
    elif st.session_state.page == "viewer":
        show_viewer()

if __name__ == "__main__":
    main()