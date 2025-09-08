# Advanced Usage Guide

## Overview

This guide covers advanced Convoscope usage patterns, customization techniques, and integration strategies for power users and developers who want to extend the application's capabilities.

## Custom LLM Provider Integration

### Creating Custom Provider Adapters

Extend Convoscope to work with new LLM providers by implementing the provider interface:

```python
# src/providers/custom_provider.py
from typing import List, Dict, Optional, AsyncGenerator
import aiohttp
from src.services.llm_service import ILLMProvider, LLMServiceError

class CustomLLMProvider(ILLMProvider):
    """Custom LLM provider implementation for XYZ AI service."""
    
    def __init__(self, api_key: str, base_url: str, timeout: int = 30):
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self.session = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    def get_completion(self, model: str, messages: List[Dict], **kwargs) -> Optional[str]:
        """Synchronous completion method."""
        import asyncio
        return asyncio.run(self._async_get_completion(model, messages, **kwargs))
    
    async def _async_get_completion(self, model: str, messages: List[Dict], **kwargs) -> Optional[str]:
        """Asynchronous completion implementation."""
        
        # Transform messages to provider format
        provider_messages = self._transform_messages(messages)
        
        payload = {
            "model": model,
            "messages": provider_messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 2000),
            "stream": False
        }
        
        try:
            async with self.session.post(f"{self.base_url}/completions", json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("choices", [{}])[0].get("message", {}).get("content")
                elif response.status == 429:
                    raise LLMServiceError("Rate limit exceeded")
                elif response.status == 401:
                    raise LLMServiceError("Invalid API key")
                else:
                    error_text = await response.text()
                    raise LLMServiceError(f"API error: {response.status} - {error_text}")
                    
        except aiohttp.ClientError as e:
            raise LLMServiceError(f"Network error: {e}")
    
    def _transform_messages(self, messages: List[Dict]) -> List[Dict]:
        """Transform OpenAI format messages to provider format."""
        transformed = []
        for msg in messages:
            # Example transformation - adapt to your provider's format
            transformed.append({
                "role": msg["role"],
                "text": msg["content"],  # Different field name
                "timestamp": msg.get("timestamp")
            })
        return transformed
    
    def validate_api_key(self) -> bool:
        """Validate API key with provider."""
        try:
            # Make a test call to validate
            test_messages = [{"role": "user", "content": "test"}]
            result = self.get_completion("default-model", test_messages)
            return result is not None
        except LLMServiceError:
            return False
    
    def get_available_models(self) -> List[str]:
        """Get list of available models from provider."""
        # Implementation depends on provider's model listing API
        return ["custom-model-1", "custom-model-2", "custom-model-3"]
    
    def supports_streaming(self) -> bool:
        """Check if provider supports streaming responses."""
        return True
    
    async def stream_completion(self, model: str, messages: List[Dict], **kwargs) -> AsyncGenerator[str, None]:
        """Stream completion responses."""
        payload = {
            "model": model,
            "messages": self._transform_messages(messages),
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 2000),
            "stream": True
        }
        
        async with self.session.post(f"{self.base_url}/completions", json=payload) as response:
            if response.status != 200:
                raise LLMServiceError(f"Streaming failed: {response.status}")
            
            async for line in response.content:
                line = line.decode('utf-8').strip()
                if line.startswith('data: '):
                    data = line[6:]  # Remove 'data: ' prefix
                    if data == '[DONE]':
                        break
                    
                    try:
                        import json
                        chunk = json.loads(data)
                        content = chunk.get("choices", [{}])[0].get("delta", {}).get("content")
                        if content:
                            yield content
                    except json.JSONDecodeError:
                        continue

# Register the custom provider
def register_custom_provider(llm_service):
    """Register custom provider with LLM service."""
    import os
    
    api_key = os.getenv("CUSTOM_API_KEY")
    base_url = os.getenv("CUSTOM_BASE_URL", "https://api.customai.com/v1")
    
    if api_key:
        custom_provider = CustomLLMProvider(api_key, base_url)
        llm_service.add_provider("custom", custom_provider)
        return True
    return False
```

### Multi-Model Ensemble

Implement ensemble methods that combine responses from multiple models:

```python
# src/services/ensemble_service.py
from typing import List, Dict, Optional, Tuple
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.services.llm_service import LLMService

class EnsembleLLMService:
    """Ensemble service that combines multiple LLM responses."""
    
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.executor = ThreadPoolExecutor(max_workers=5)
    
    def get_ensemble_completion(self, 
                               messages: List[Dict],
                               providers: List[str] = None,
                               strategy: str = "vote",
                               **kwargs) -> Dict[str, any]:
        """Get completion using ensemble of providers."""
        
        if providers is None:
            providers = list(self.llm_service.get_available_providers().keys())[:3]
        
        # Get responses from multiple providers
        responses = self._get_multiple_responses(messages, providers, **kwargs)
        
        # Apply ensemble strategy
        if strategy == "vote":
            return self._majority_vote(responses)
        elif strategy == "weighted":
            return self._weighted_average(responses)
        elif strategy == "best":
            return self._select_best(responses)
        else:
            return self._simple_average(responses)
    
    def _get_multiple_responses(self, messages: List[Dict], providers: List[str], **kwargs) -> List[Dict]:
        """Get responses from multiple providers concurrently."""
        futures = []
        
        for provider in providers:
            future = self.executor.submit(
                self._get_single_response, 
                provider, 
                messages, 
                **kwargs
            )
            futures.append((provider, future))
        
        responses = []
        for provider, future in futures:
            try:
                response = future.result(timeout=30)
                responses.append({
                    "provider": provider,
                    "response": response,
                    "success": response is not None
                })
            except Exception as e:
                responses.append({
                    "provider": provider,
                    "response": None,
                    "success": False,
                    "error": str(e)
                })
        
        return responses
    
    def _get_single_response(self, provider: str, messages: List[Dict], **kwargs) -> Optional[str]:
        """Get response from single provider."""
        available_providers = self.llm_service.get_available_providers()
        
        if provider in available_providers:
            models = available_providers[provider].models
            if models:
                return self.llm_service.get_completion(
                    provider=provider,
                    model=models[0],
                    messages=messages,
                    **kwargs
                )
        return None
    
    def _majority_vote(self, responses: List[Dict]) -> Dict[str, any]:
        """Select response by majority vote (similarity-based)."""
        successful_responses = [r for r in responses if r["success"]]
        
        if not successful_responses:
            return {"response": None, "confidence": 0.0, "strategy": "vote"}
        
        if len(successful_responses) == 1:
            return {
                "response": successful_responses[0]["response"],
                "confidence": 0.5,
                "strategy": "vote",
                "providers_used": [successful_responses[0]["provider"]]
            }
        
        # Simple implementation - in practice, use semantic similarity
        response_counts = {}
        for resp in successful_responses:
            text = resp["response"]
            response_counts[text] = response_counts.get(text, 0) + 1
        
        best_response = max(response_counts, key=response_counts.get)
        confidence = response_counts[best_response] / len(successful_responses)
        
        return {
            "response": best_response,
            "confidence": confidence,
            "strategy": "vote",
            "providers_used": [r["provider"] for r in successful_responses],
            "vote_counts": response_counts
        }
    
    def _weighted_average(self, responses: List[Dict]) -> Dict[str, any]:
        """Weighted average based on provider reliability."""
        provider_weights = {
            "openai": 1.0,
            "anthropic": 0.9,
            "google": 0.8,
            "custom": 0.7
        }
        
        successful_responses = [r for r in responses if r["success"]]
        if not successful_responses:
            return {"response": None, "confidence": 0.0, "strategy": "weighted"}
        
        # Simple weighted selection (in practice, might blend responses)
        weighted_responses = []
        for resp in successful_responses:
            weight = provider_weights.get(resp["provider"], 0.5)
            weighted_responses.append((resp, weight))
        
        best_response = max(weighted_responses, key=lambda x: x[1])
        
        return {
            "response": best_response[0]["response"],
            "confidence": best_response[1],
            "strategy": "weighted",
            "providers_used": [r["provider"] for r in successful_responses]
        }
    
    def _select_best(self, responses: List[Dict]) -> Dict[str, any]:
        """Select best response based on quality metrics."""
        successful_responses = [r for r in responses if r["success"]]
        
        if not successful_responses:
            return {"response": None, "confidence": 0.0, "strategy": "best"}
        
        # Quality scoring (length, coherence, etc.)
        scored_responses = []
        for resp in successful_responses:
            score = self._quality_score(resp["response"])
            scored_responses.append((resp, score))
        
        best_response = max(scored_responses, key=lambda x: x[1])
        
        return {
            "response": best_response[0]["response"],
            "confidence": best_response[1] / 100,  # Normalize score
            "strategy": "best",
            "quality_score": best_response[1],
            "providers_used": [r["provider"] for r in successful_responses]
        }
    
    def _quality_score(self, response: str) -> float:
        """Calculate response quality score."""
        if not response:
            return 0.0
        
        score = 0.0
        
        # Length scoring (moderate length preferred)
        length = len(response)
        if 50 <= length <= 1000:
            score += 30
        elif length > 1000:
            score += 20
        else:
            score += 10
        
        # Coherence indicators
        if '. ' in response:  # Sentence structure
            score += 20
        if '?' in response or '!' in response:  # Engagement
            score += 10
        if response[0].isupper():  # Proper capitalization
            score += 10
        
        # Avoid repetition
        words = response.lower().split()
        unique_words = len(set(words))
        if len(words) > 0:
            diversity = unique_words / len(words)
            score += diversity * 30
        
        return min(score, 100.0)
```

## Advanced Conversation Management

### Conversation Analytics

Implement comprehensive conversation analysis:

```python
# src/services/conversation_analytics.py
from typing import List, Dict, Any, Optional
import json
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import re

class ConversationAnalytics:
    """Advanced conversation analysis and metrics."""
    
    def __init__(self, conversation_manager):
        self.conversation_manager = conversation_manager
    
    def analyze_conversation(self, conversation: List[Dict]) -> Dict[str, Any]:
        """Comprehensive conversation analysis."""
        
        analysis = {
            "basic_stats": self._basic_statistics(conversation),
            "temporal_analysis": self._temporal_analysis(conversation),
            "content_analysis": self._content_analysis(conversation),
            "interaction_patterns": self._interaction_patterns(conversation),
            "quality_metrics": self._quality_metrics(conversation)
        }
        
        return analysis
    
    def _basic_statistics(self, conversation: List[Dict]) -> Dict[str, Any]:
        """Basic conversation statistics."""
        role_counts = Counter(msg["role"] for msg in conversation)
        
        return {
            "total_messages": len(conversation),
            "user_messages": role_counts.get("user", 0),
            "assistant_messages": role_counts.get("assistant", 0),
            "system_messages": role_counts.get("system", 0),
            "total_characters": sum(len(msg["content"]) for msg in conversation),
            "average_message_length": sum(len(msg["content"]) for msg in conversation) / len(conversation) if conversation else 0,
            "message_length_distribution": self._length_distribution(conversation)
        }
    
    def _temporal_analysis(self, conversation: List[Dict]) -> Dict[str, Any]:
        """Analyze temporal patterns in conversation."""
        timestamps = [msg.get("timestamp") for msg in conversation if msg.get("timestamp")]
        
        if not timestamps:
            return {"error": "No timestamps available"}
        
        # Convert to datetime objects
        dt_timestamps = []
        for ts in timestamps:
            try:
                if isinstance(ts, str):
                    dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                else:
                    dt = ts
                dt_timestamps.append(dt)
            except ValueError:
                continue
        
        if len(dt_timestamps) < 2:
            return {"error": "Insufficient timestamp data"}
        
        # Calculate intervals
        intervals = []
        for i in range(1, len(dt_timestamps)):
            interval = (dt_timestamps[i] - dt_timestamps[i-1]).total_seconds()
            intervals.append(interval)
        
        return {
            "conversation_duration_minutes": (dt_timestamps[-1] - dt_timestamps[0]).total_seconds() / 60,
            "average_response_time_seconds": sum(intervals) / len(intervals) if intervals else 0,
            "response_time_distribution": self._time_distribution(intervals),
            "conversation_pace": "fast" if sum(intervals) / len(intervals) < 30 else "moderate" if sum(intervals) / len(intervals) < 120 else "slow"
        }
    
    def _content_analysis(self, conversation: List[Dict]) -> Dict[str, Any]:
        """Analyze conversation content patterns."""
        all_content = " ".join(msg["content"] for msg in conversation)
        
        # Word frequency analysis
        words = re.findall(r'\b\w+\b', all_content.lower())
        word_freq = Counter(words)
        
        # Question patterns
        questions = sum(1 for msg in conversation if '?' in msg["content"])
        
        # Sentiment indicators (simple heuristic)
        positive_words = ['good', 'great', 'excellent', 'perfect', 'amazing', 'wonderful', 'fantastic']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'disappointing', 'frustrating']
        
        positive_count = sum(all_content.lower().count(word) for word in positive_words)
        negative_count = sum(all_content.lower().count(word) for word in negative_words)
        
        return {
            "total_words": len(words),
            "unique_words": len(set(words)),
            "vocabulary_diversity": len(set(words)) / len(words) if words else 0,
            "most_common_words": word_freq.most_common(10),
            "question_count": questions,
            "exclamation_count": all_content.count('!'),
            "sentiment_indicators": {
                "positive_signals": positive_count,
                "negative_signals": negative_count,
                "sentiment_ratio": positive_count / (positive_count + negative_count + 1)
            },
            "topic_keywords": self._extract_topic_keywords(words)
        }
    
    def _interaction_patterns(self, conversation: List[Dict]) -> Dict[str, Any]:
        """Analyze user-assistant interaction patterns."""
        patterns = {
            "turn_taking": [],
            "response_lengths": {"user": [], "assistant": []},
            "conversation_flow": []
        }
        
        for i, msg in enumerate(conversation):
            if msg["role"] in ["user", "assistant"]:
                # Track turn-taking
                if i > 0 and conversation[i-1]["role"] != msg["role"]:
                    patterns["turn_taking"].append("switch")
                else:
                    patterns["turn_taking"].append("continue")
                
                # Track response lengths by role
                patterns["response_lengths"][msg["role"]].append(len(msg["content"]))
                
                # Conversation flow analysis
                if msg["role"] == "user":
                    if '?' in msg["content"]:
                        patterns["conversation_flow"].append("question")
                    elif any(word in msg["content"].lower() for word in ['thanks', 'thank you']):
                        patterns["conversation_flow"].append("gratitude")
                    else:
                        patterns["conversation_flow"].append("statement")
                elif msg["role"] == "assistant":
                    if len(msg["content"]) > 500:
                        patterns["conversation_flow"].append("detailed_response")
                    else:
                        patterns["conversation_flow"].append("brief_response")
        
        # Analysis of patterns
        flow_analysis = Counter(patterns["conversation_flow"])
        
        return {
            "conversation_style": self._determine_conversation_style(flow_analysis),
            "user_engagement_level": self._calculate_engagement(patterns),
            "response_balance": {
                "avg_user_length": sum(patterns["response_lengths"]["user"]) / len(patterns["response_lengths"]["user"]) if patterns["response_lengths"]["user"] else 0,
                "avg_assistant_length": sum(patterns["response_lengths"]["assistant"]) / len(patterns["response_lengths"]["assistant"]) if patterns["response_lengths"]["assistant"] else 0
            },
            "interaction_flow": flow_analysis
        }
    
    def _quality_metrics(self, conversation: List[Dict]) -> Dict[str, Any]:
        """Calculate conversation quality metrics."""
        assistant_messages = [msg for msg in conversation if msg["role"] == "assistant"]
        
        if not assistant_messages:
            return {"error": "No assistant messages to analyze"}
        
        # Helpfulness indicators
        helpful_phrases = ['i can help', 'here\'s how', 'try this', 'solution', 'answer']
        helpfulness_score = sum(
            sum(1 for phrase in helpful_phrases if phrase in msg["content"].lower())
            for msg in assistant_messages
        ) / len(assistant_messages)
        
        # Clarity indicators
        clarity_indicators = ['.', ':', 'first', 'second', 'then', 'finally']
        clarity_score = sum(
            sum(1 for indicator in clarity_indicators if indicator in msg["content"].lower())
            for msg in assistant_messages
        ) / len(assistant_messages)
        
        # Error/confusion indicators
        error_phrases = ['sorry', 'apologize', 'mistake', 'unclear', 'confusion']
        error_score = sum(
            sum(1 for phrase in error_phrases if phrase in msg["content"].lower())
            for msg in assistant_messages
        ) / len(assistant_messages)
        
        return {
            "helpfulness_score": min(helpfulness_score, 5.0),  # Cap at 5
            "clarity_score": min(clarity_score, 5.0),
            "error_rate": min(error_score, 1.0),
            "overall_quality": (helpfulness_score + clarity_score - error_score) / 2,
            "response_completeness": self._calculate_completeness(assistant_messages)
        }
    
    def _extract_topic_keywords(self, words: List[str]) -> List[str]:
        """Extract likely topic keywords."""
        # Filter out common words
        common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'can', 'may', 'might', 'must', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their', 'this', 'that', 'these', 'those', 'a', 'an'}
        
        # Get words longer than 3 characters that aren't common words
        topic_candidates = [word for word in words if len(word) > 3 and word not in common_words]
        
        # Count frequency and return top candidates
        word_freq = Counter(topic_candidates)
        return [word for word, count in word_freq.most_common(10) if count > 1]
    
    def get_conversation_insights(self, filename: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive insights for a specific conversation."""
        success, conversation = self.conversation_manager.load_conversation(filename)
        
        if not success:
            return None
        
        insights = self.analyze_conversation(conversation)
        insights["filename"] = filename
        insights["analysis_timestamp"] = datetime.now().isoformat()
        
        return insights
    
    def batch_analyze_conversations(self, limit: Optional[int] = None) -> Dict[str, Any]:
        """Analyze multiple conversations and provide aggregated insights."""
        conversation_list = self.conversation_manager.get_conversation_list()
        
        if limit:
            conversation_list = conversation_list[:limit]
        
        all_insights = []
        successful_analyses = 0
        
        for filename in conversation_list:
            insights = self.get_conversation_insights(filename)
            if insights:
                all_insights.append(insights)
                successful_analyses += 1
        
        # Aggregate statistics
        if not all_insights:
            return {"error": "No conversations could be analyzed"}
        
        aggregate_stats = self._aggregate_insights(all_insights)
        
        return {
            "total_conversations": len(conversation_list),
            "analyzed_conversations": successful_analyses,
            "aggregate_statistics": aggregate_stats,
            "top_conversations": self._rank_conversations(all_insights),
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    def _aggregate_insights(self, insights_list: List[Dict]) -> Dict[str, Any]:
        """Aggregate insights from multiple conversations."""
        total_messages = sum(insight["basic_stats"]["total_messages"] for insight in insights_list)
        total_words = sum(insight["content_analysis"]["total_words"] for insight in insights_list)
        
        avg_quality = sum(insight["quality_metrics"].get("overall_quality", 0) for insight in insights_list) / len(insights_list)
        
        # Collect all topic keywords
        all_topics = []
        for insight in insights_list:
            all_topics.extend(insight["content_analysis"]["topic_keywords"])
        
        return {
            "total_messages_across_all": total_messages,
            "total_words_across_all": total_words,
            "average_conversation_length": total_messages / len(insights_list),
            "average_quality_score": avg_quality,
            "most_common_topics": Counter(all_topics).most_common(20),
            "conversation_count": len(insights_list)
        }
```

## Custom UI Components

### Advanced Streamlit Components

Create reusable UI components for enhanced functionality:

```python
# src/ui/components.py
import streamlit as st
from typing import List, Dict, Any, Optional, Callable
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

class ConversationDashboard:
    """Advanced conversation dashboard with analytics."""
    
    @staticmethod
    def render_provider_status(llm_service) -> None:
        """Render provider status dashboard."""
        st.subheader("🔌 Provider Status")
        
        available_providers = llm_service.get_available_providers()
        
        if not available_providers:
            st.error("❌ No providers available")
            return
        
        # Create columns for provider status
        cols = st.columns(len(available_providers))
        
        for i, (name, provider) in enumerate(available_providers.items()):
            with cols[i]:
                # Provider status card
                st.markdown(f"""
                <div style="
                    border: 2px solid #28a745;
                    border-radius: 8px;
                    padding: 1rem;
                    text-align: center;
                    background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                    color: white;
                    margin-bottom: 1rem;
                ">
                    <h4 style="margin: 0; color: white;">{name.title()}</h4>
                    <p style="margin: 0.5rem 0; font-size: 0.9rem;">✅ Available</p>
                    <p style="margin: 0; font-size: 0.8rem;">{len(provider.models)} models</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Models dropdown
                with st.expander(f"{name.title()} Models"):
                    for model in provider.models:
                        st.text(f"• {model}")
    
    @staticmethod
    def render_conversation_metrics(analytics_service, conversation: List[Dict]) -> None:
        """Render conversation metrics dashboard."""
        if not conversation:
            st.info("No conversation data to analyze")
            return
        
        # Get analysis
        analysis = analytics_service.analyze_conversation(conversation)
        
        # Key metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Messages",
                analysis["basic_stats"]["total_messages"],
                delta=None
            )
        
        with col2:
            st.metric(
                "Avg Message Length",
                f"{analysis['basic_stats']['average_message_length']:.0f} chars"
            )
        
        with col3:
            quality_score = analysis["quality_metrics"].get("overall_quality", 0)
            st.metric(
                "Quality Score",
                f"{quality_score:.2f}/5.0",
                delta=quality_score - 2.5  # Relative to neutral
            )
        
        with col4:
            vocab_diversity = analysis["content_analysis"]["vocabulary_diversity"]
            st.metric(
                "Vocabulary Diversity",
                f"{vocab_diversity:.3f}",
                delta=vocab_diversity - 0.5  # Relative to average
            )
        
        # Detailed metrics
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Message Distribution")
            role_counts = {
                "User": analysis["basic_stats"]["user_messages"],
                "Assistant": analysis["basic_stats"]["assistant_messages"],
                "System": analysis["basic_stats"]["system_messages"]
            }
            
            fig = px.pie(
                values=list(role_counts.values()),
                names=list(role_counts.keys()),
                title="Messages by Role"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("🎯 Content Analysis")
            
            # Top words
            top_words = analysis["content_analysis"]["most_common_words"][:5]
            if top_words:
                words, counts = zip(*top_words)
                
                fig = px.bar(
                    x=list(words),
                    y=list(counts),
                    title="Most Common Words",
                    labels={"x": "Words", "y": "Count"}
                )
                st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def render_conversation_timeline(conversation: List[Dict]) -> None:
        """Render conversation timeline visualization."""
        timestamps = [msg.get("timestamp") for msg in conversation if msg.get("timestamp")]
        
        if not timestamps:
            st.warning("No timestamp data available for timeline")
            return
        
        # Convert timestamps and create timeline data
        timeline_data = []
        for i, msg in enumerate(conversation):
            if msg.get("timestamp"):
                try:
                    dt = datetime.fromisoformat(msg["timestamp"].replace('Z', '+00:00'))
                    timeline_data.append({
                        "time": dt,
                        "message_index": i,
                        "role": msg["role"],
                        "length": len(msg["content"]),
                        "content_preview": msg["content"][:50] + "..." if len(msg["content"]) > 50 else msg["content"]
                    })
                except ValueError:
                    continue
        
        if not timeline_data:
            st.warning("Could not parse timestamp data")
            return
        
        st.subheader("⏰ Conversation Timeline")
        
        # Create timeline plot
        fig = go.Figure()
        
        for role in ["user", "assistant", "system"]:
            role_data = [d for d in timeline_data if d["role"] == role]
            if role_data:
                fig.add_trace(go.Scatter(
                    x=[d["time"] for d in role_data],
                    y=[d["length"] for d in role_data],
                    mode='markers+lines',
                    name=role.title(),
                    text=[d["content_preview"] for d in role_data],
                    hovertemplate=f"<b>{role.title()}</b><br>" +
                                  "Time: %{x}<br>" +
                                  "Length: %{y} chars<br>" +
                                  "Content: %{text}<br>" +
                                  "<extra></extra>"
                ))
        
        fig.update_layout(
            title="Message Length Over Time",
            xaxis_title="Time",
            yaxis_title="Message Length (characters)",
            hovermode="closest"
        )
        
        st.plotly_chart(fig, use_container_width=True)

class AdvancedChatInterface:
    """Enhanced chat interface with advanced features."""
    
    def __init__(self, llm_service, conversation_manager):
        self.llm_service = llm_service
        self.conversation_manager = conversation_manager
    
    def render_chat_input_with_tools(self) -> Optional[str]:
        """Render enhanced chat input with additional tools."""
        
        # Main input area
        col1, col2, col3 = st.columns([6, 1, 1])
        
        with col1:
            user_input = st.chat_input("Type your message...")
        
        with col2:
            # Voice input placeholder (would integrate with speech-to-text)
            if st.button("🎤", help="Voice input"):
                st.info("Voice input would be implemented here")
        
        with col3:
            # File upload for context
            uploaded_file = st.file_uploader(
                "📎", 
                type=['txt', 'md', 'json'],
                label_visibility="collapsed",
                help="Upload file for context"
            )
            
            if uploaded_file:
                content = uploaded_file.read().decode()
                if content:
                    return f"Context from {uploaded_file.name}:\n\n{content}\n\nUser question: {user_input}" if user_input else f"Please analyze this file content:\n\n{content}"
        
        return user_input
    
    def render_response_options(self) -> Dict[str, Any]:
        """Render response customization options."""
        st.sidebar.subheader("🎛️ Response Options")
        
        options = {}
        
        # Provider selection
        available_providers = list(self.llm_service.get_available_providers().keys())
        options["provider"] = st.sidebar.selectbox(
            "Provider",
            available_providers,
            help="Select LLM provider"
        )
        
        # Model selection
        if options["provider"]:
            models = self.llm_service.get_available_models(options["provider"])
            options["model"] = st.sidebar.selectbox(
                "Model",
                models,
                help="Select specific model"
            )
        
        # Response parameters
        options["temperature"] = st.sidebar.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
            help="Response creativity (0=focused, 1=creative)"
        )
        
        options["max_tokens"] = st.sidebar.slider(
            "Max Tokens",
            min_value=100,
            max_value=4000,
            value=2000,
            step=100,
            help="Maximum response length"
        )
        
        # Advanced options
        with st.sidebar.expander("Advanced Options"):
            options["use_ensemble"] = st.checkbox(
                "Use Ensemble",
                help="Get responses from multiple providers"
            )
            
            if options["use_ensemble"]:
                options["ensemble_strategy"] = st.selectbox(
                    "Ensemble Strategy",
                    ["vote", "weighted", "best"],
                    help="How to combine multiple responses"
                )
            
            options["system_prompt"] = st.text_area(
                "System Prompt",
                value="You are a helpful assistant.",
                help="Custom system prompt"
            )
        
        return options
    
    def render_conversation_export(self) -> None:
        """Render conversation export options."""
        st.sidebar.subheader("💾 Export Options")
        
        if 'conversation' in st.session_state and st.session_state.conversation:
            export_format = st.sidebar.selectbox(
                "Export Format",
                ["JSON", "Markdown", "PDF", "HTML"]
            )
            
            if st.sidebar.button("Export Conversation"):
                conversation = st.session_state.conversation
                
                if export_format == "JSON":
                    self._export_as_json(conversation)
                elif export_format == "Markdown":
                    self._export_as_markdown(conversation)
                elif export_format == "PDF":
                    st.info("PDF export would be implemented here")
                elif export_format == "HTML":
                    st.info("HTML export would be implemented here")
        else:
            st.sidebar.info("No conversation to export")
    
    def _export_as_json(self, conversation: List[Dict]) -> None:
        """Export conversation as JSON."""
        import json
        
        export_data = {
            "conversation": conversation,
            "export_timestamp": datetime.now().isoformat(),
            "total_messages": len(conversation)
        }
        
        json_string = json.dumps(export_data, indent=2)
        
        st.sidebar.download_button(
            label="Download JSON",
            data=json_string,
            file_name=f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    def _export_as_markdown(self, conversation: List[Dict]) -> None:
        """Export conversation as Markdown."""
        markdown_content = f"# Conversation Export\n\n"
        markdown_content += f"**Exported:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        markdown_content += f"**Total Messages:** {len(conversation)}\n\n"
        markdown_content += "---\n\n"
        
        for i, msg in enumerate(conversation, 1):
            role_icon = {"user": "👤", "assistant": "🤖", "system": "⚙️"}.get(msg["role"], "❓")
            markdown_content += f"## {role_icon} {msg['role'].title()} - Message {i}\n\n"
            markdown_content += f"{msg['content']}\n\n"
            
            if msg.get("timestamp"):
                markdown_content += f"*Timestamp: {msg['timestamp']}*\n\n"
            
            markdown_content += "---\n\n"
        
        st.sidebar.download_button(
            label="Download Markdown",
            data=markdown_content,
            file_name=f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown"
        )
```

This advanced usage guide demonstrates how to extend Convoscope with custom providers, analytics, and enhanced UI components for power users and developers who need more sophisticated functionality.

---

*Next: [Testing Guide](testing.md) - Comprehensive testing strategies and test development*