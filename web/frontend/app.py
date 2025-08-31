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

sys.path.append(os.path.join(os.path.dirname(__file__), "../shared"))
from utils import APIClient, wait_for_task_completion, format_file_size, validate_url, normalize_url, get_company_name_from_url
from model_utils import get_available_models

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
        st.error("**Backend API is not running!**")
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
                                st.error(f"Error deleting factsheet: {e}")
                    
                    st.divider()
        else:
            st.info("No factsheets generated yet. Use the Generator to create your first one!")
    
    except Exception as e:
        st.error(f"Error loading dashboard: {e}")

def show_generator():
    """Show the factsheet generator"""
    st.markdown('<h1 class="main-header">Generate New Factsheet</h1>', unsafe_allow_html=True)
    
    if not check_api_health():
        return
    
    with st.form("generate_form"):
        st.subheader("Company Information")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            url = st.text_input(
                "Company Website URL",
                placeholder="example.com or stripe.com",
                help="Enter company domain (https:// and www. will be added automatically)"
            )
        
        with col2:
            st.markdown("**AI Provider**")
            provider = st.selectbox(
                "Provider",
                ["openai", "gemini"],
                help="OpenAI requires API key, Gemini is free"
            )
        
        # Model selection based on provider
        st.subheader("Model Selection")
        
        # Get available models dynamically
        with st.spinner("Loading available models..."):
            try:
                all_models = get_available_models()
                available_models = all_models.get(provider, {})
            except Exception as e:
                st.error(f"Error loading models: {str(e)}")
                available_models = {}
        
        # Prepare model selection
        model_names = list(available_models.keys())
        model_labels = [available_models[name] for name in model_names]
        
        if model_names:
            selected_model_label = st.selectbox(
                "Model",
                model_labels,
                help=f"Choose a {provider.upper()} model for factsheet generation"
            )
            # Get the actual model name from the selected label
            model = model_names[model_labels.index(selected_model_label)]
        else:
            model = None
            st.warning(f"No models available for {provider}. Please check your API key.")
            if provider == "openai" and not os.getenv("OPENAI_API_KEY"):
                st.info("Set your OpenAI API key: `export OPENAI_API_KEY='your-key'`")
            elif provider == "gemini" and not os.getenv("GEMINI_API_KEY"):
                st.info("Set your Gemini API key: `export GEMINI_API_KEY='your-key'`")
        
        submitted = st.form_submit_button("Generate Factsheet", type="primary")
        
        if submitted:
            if not url:
                st.error("Please enter a company URL")
                return
            
            # Normalize the URL
            normalized_url = normalize_url(url)
            
            if not validate_url(url):
                st.error("Please enter a valid company domain")
                return
            
            try:
                # Start generation with normalized URL
                with st.spinner("Starting factsheet generation..."):
                    response = api_client.generate_factsheet(
                        url=normalized_url,
                        provider=provider,
                        model=model if model else None
                    )
                
                task_id = response['task_id']
                st.success(f"Generation started! Task ID: {task_id}")
                
                # Progress tracking
                st.subheader("Generation Progress")
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    result = wait_for_task_completion(api_client, task_id, progress_bar, status_text)
                    
                    st.success("Factsheet generated successfully!")
                    
                    # Store completion info in session state
                    st.session_state.generation_completed = True
                    st.session_state.completed_filename = result['result']['filename']
                    
                    # Show result details
                    st.subheader("Generation Complete")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Company", result['result']['company_name'])
                    
                    with col2:
                        st.metric("Word Count", result['result']['word_count'])
                    
                    with col3:
                        st.metric("Status", "Complete")
                
                except Exception as e:
                    st.error(f"Generation failed: {e}")
            
            except Exception as e:
                st.error(f"Error starting generation: {e}")
    
    # Check if we just completed generation and show view button outside form
    if 'generation_completed' in st.session_state and st.session_state.generation_completed:
        st.subheader("Next Steps")
        if st.button("View Generated Factsheet", type="secondary"):
            st.session_state.selected_factsheet = st.session_state.completed_filename
            st.session_state.page = "viewer"
            st.session_state.generation_completed = False  # Reset flag
            st.rerun()

def show_viewer():
    """Show factsheet viewer"""
    st.markdown('<h1 class="main-header">Factsheet Viewer</h1>', unsafe_allow_html=True)
    
    if not check_api_health():
        return
    
    # Get selected factsheet from session state
    selected_filename = st.session_state.get('selected_factsheet')
    
    if not selected_filename:
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
        st.error(f"Error loading factsheet: {e}")

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