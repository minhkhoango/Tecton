import re
import click
from typing import List, Dict
import streamlit as st
import plotly.express as px  # type: ignore
from .analysis import AnalysisResult, RetrievedChunk

def _get_status_color(status: str) -> str:
    return "green" if status == "HEALTHY" else ("orange" if status == "WARNING" else "red")

def _create_relevance_bar(score: float) -> str:
    """Creates an HTML progress bar to visualize relevance score."""
    color = "green" if score > 0.85 else ("orange" if score > 0.75 else "red")
    return f"""
    <div style="background-color: #eee; border-radius: 5px; padding: 2px;">
        <div style="width: {score*100}%; background-color: {color}; height: 20px; border-radius: 5px; text-align: center; color: white; font-weight: bold;">
            {score:.2f}
        </div>
    </div>
    """

def _highlight_text(text: str, phrases: List[str]) -> str:
    """Highlights a list of phrases in a block of text."""
    for phrase in phrases:
        # Use regex to find whole words/phrases only, case-insensitive
        text = re.sub(f"({re.escape(phrase)})", r'<mark style="background-color: #FFDDAA; padding: 2px 0px; border-radius: 3px;">\1</mark>', text, flags=re.IGNORECASE)
    return text

def _extract_key_phrases(chunks: List[RetrievedChunk]) -> List[str]:
    """Extract key phrases from chunks for highlighting."""
    if not chunks:
        return []
    
    # Simple approach: extract common words that appear in multiple chunks
    word_counts: Dict[str, int] = {}
    for chunk in chunks:
        words = chunk['text'].lower().split()
        for word in words:
            if len(word) > 3:  # Only consider words longer than 3 characters
                word_counts[word] = word_counts.get(word, 0) + 1
    
    # Return words that appear in at least 2 chunks
    return [word for word, count in word_counts.items() if count >= 2][:10]

def display_visual_summary(analysis: AnalysisResult) -> None:
    """Renders the main diagnostic summary with metrics."""
    report = analysis['health_report']
    status = report['status']
    color = _get_status_color(status)

    st.header(f"Context Health: :{color}[{status}]")
    st.write(f"**Diagnosis:** {report['message']}")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Key Metrics")
        st.metric("Retrieved Chunks", report['chunk_count'])
        st.metric("Avg. Relevance Score", f"{report['avg_relevance_score']:.2f}")
        st.metric("Semantic Diversity", f"{report['semantic_diversity_score']:.2f}", help="Score from 0 (repetitive) to 1 (diverse).")

    with col2:
        st.subheader("Relevance Distribution")
        chunks = analysis['retrieved_chunks']
        if chunks:
            # Create a simple bar chart of relevance scores
            scores = [chunk['score'] for chunk in chunks]
            labels = [f"Chunk {i+1}" for i in range(len(chunks))]
            
            fig = px.bar(  # type: ignore
                x=labels, y=scores,
                title="Relevance Scores by Chunk",
                labels={'x': 'Chunk', 'y': 'Relevance Score'}
            )
            fig.update_layout(yaxis_range=[0, 1])  # type: ignore
            st.plotly_chart(fig, use_container_width=True)  # type: ignore
        else:
            st.info("No chunks available for visualization.")

def display_context_details(analysis: AnalysisResult) -> None:
    """Renders the detailed, annotated context chunks."""
    st.header("Retrieved Context Details")
    chunks = analysis['retrieved_chunks']
    
    if not chunks:
        st.warning("No context was retrieved.")
        return

    # Extract key phrases for highlighting
    key_phrases = _extract_key_phrases(chunks)

    for i, chunk in enumerate(chunks):
        st.markdown(f"---")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**Chunk {i+1}**")
            highlighted_text = _highlight_text(chunk['text'], key_phrases)
            st.markdown(f'<div style="background-color:#f8f9fa; color: black; padding: 10px; border-radius: 5px;">{highlighted_text}</div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f"**Relevance**")
            st.html(_create_relevance_bar(chunk['score']))

def format_cli_report(analysis: AnalysisResult) -> str:
    """Formats the full analysis result into a string for CLI output."""
    report_parts: List[str] = []
    report = analysis['health_report']
    status = report['status']
    color = "green" if status == "HEALTHY" else ("yellow" if status == "WARNING" else "red")

    report_parts.append(f"\n--- Context Health Report ---")
    report_parts.append(f"Status: {click.style(status, fg=color, bold=True)}")
    report_parts.append(f"Diagnosis: {report['message']}")
    report_parts.append(
        f"Chunks: {report['chunk_count']} | "
        f"Avg. Relevance: {report['avg_relevance_score']:.2f} | "
        f"Diversity: {report['semantic_diversity_score']:.2f}"
    )

    report_parts.append(click.style("\n--- Retrieved Context Chunks ---", fg="cyan"))
    chunks = analysis['retrieved_chunks']
    if not chunks:
        report_parts.append("No context was retrieved.")
    else:
        for i, chunk in enumerate(chunks):
            report_parts.append(f"Chunk {i+1} | Score: {chunk['score']:.2f}")
            # Indent the text for readability
            report_parts.append(f"  > {chunk['text']}")

    report_parts.append("\n")
    return "\n".join(report_parts)