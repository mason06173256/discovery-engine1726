"""AI-powered source analysis and hypothesis generation using Groq."""

from typing import List, Optional
from .models import Source, Hypothesis
from .ai_providers import AIProvider, GroqProvider


class SourceAnalyzer:
    """Analyzes retrieved sources using Groq AI to extract insights and generate hypotheses."""

    def __init__(self, ai_provider: Optional[AIProvider] = None):
        """Initialize the analyzer with an AI provider.
        
        Args:
            ai_provider: AI provider instance (defaults to GroqProvider).
        """
        self.ai_provider = ai_provider or GroqProvider()

    def extract_key_insights(self, sources: List[Source], query: str) -> str:
        """Use Groq to extract key insights from sources relevant to the query.
        
        Args:
            sources: List of retrieved sources to analyze.
            query: The original research query context.
            
        Returns:
            A structured summary of key insights from the sources.
        """
        if not sources:
            return "No sources available for analysis."

        # Prepare source context
        source_summaries = []
        for source in sources[:5]:  # Limit to top 5 for API efficiency
            snippet = source.claims_extracted[0] if source.claims_extracted else "No claims extracted."
            source_summaries.append(f"- {source.title}\n  URL: {source.url}\n  Content: {snippet[:200]}...")

        source_context = "\n".join(source_summaries)

        prompt = f"""You are a research analyst. Analyze the following sources related to the query "{query}" and extract key insights.

Sources:
{source_context}

Provide a concise summary of:
1. Common themes across sources
2. Key findings or innovations mentioned
3. Any contradictions or different perspectives
4. Relevance of sources to the original query

Keep the response factual and grounded only in the retrieved source content."""

        try:
            insights = self.ai_provider.generate_text(prompt, max_tokens=500)
            return insights
        except Exception as e:
            return f"Analysis failed: {str(e)}"

    def generate_hypothesis_from_sources(
        self, sources: List[Source], query: str, user_objective: str
    ) -> Optional[Hypothesis]:
        """Generate an AI-informed hypothesis based on retrieved sources.
        
        Args:
            sources: List of retrieved sources.
            query: The search query used to retrieve sources.
            user_objective: The user's original research objective.
            
        Returns:
            A Hypothesis object generated from source analysis, or None if generation fails.
        """
        if not sources:
            return None

        # Prepare source context for AI analysis
        source_snippets = []
        for source in sources[:10]:
            claim = source.claims_extracted[0] if source.claims_extracted else ""
            source_snippets.append(f"{source.title}: {claim[:150]}")

        sources_text = "\n".join(source_snippets)

        prompt = f"""Based on these retrieved research sources about "{query}", generate a research hypothesis for the objective: "{user_objective}"

Sources:
{sources_text}

Generate a hypothesis that:
1. Is grounded only in the retrieved sources (no speculation)
2. Clearly states what the sources suggest
3. Identifies the confidence level based on source agreement
4. Notes any gaps or questions remaining

Format your response as:
HYPOTHESIS: [The hypothesis statement]
CONFIDENCE: [Low/Medium/High]
SUPPORTING_POINTS: [Key points from sources]
UNCERTAINTIES: [What is not yet clear]
NEXT_QUESTIONS: [What would help refine this further]"""

        try:
            response = self.ai_provider.generate_text(prompt, max_tokens=800)
            
            # Parse the response to create a structured hypothesis
            hypothesis_text = response.split("HYPOTHESIS:")[1].split("\nCONFIDENCE:")[0].strip() if "HYPOTHESIS:" in response else response
            
            confidence_map = {"Low": 0.3, "Medium": 0.65, "High": 0.85}
            confidence_str = response.split("CONFIDENCE:")[1].split("\n")[0].strip() if "CONFIDENCE:" in response else "Medium"
            confidence = confidence_map.get(confidence_str.capitalize(), 0.65)
            
            hypothesis = Hypothesis(
                description=hypothesis_text,
                supporting_sources=[source.source_id for source in sources],
                confidence=confidence,
                current_status="active",
                novelty_status="unable_to_determine",  # Will be evaluated separately
            )
            
            # Add the full analysis as part of criticism
            hypothesis.criticism = [
                f"Generated from {len(sources)} sources",
                f"Confidence: {confidence_str}",
                "This hypothesis is grounded in retrieved evidence; novelty still requires comparison against known work."
            ]
            
            return hypothesis
            
        except Exception as e:
            return None

    def compare_sources_for_novelty(self, sources: List[Source], hypothesis_description: str) -> str:
        """Use Groq to assess whether the hypothesis appears to be novel based on source comparison.
        
        Args:
            sources: Retrieved sources to compare.
            hypothesis_description: The hypothesis to evaluate.
            
        Returns:
            A novelty assessment.
        """
        if not sources:
            return "unable_to_determine"

        source_context = "\n".join([
            f"- {source.title}\n  {source.claims_extracted[0] if source.claims_extracted else ''}"
            for source in sources[:5]
        ])

        prompt = f"""Given these sources on the topic, assess whether the following hypothesis appears to be novel or already established:

Hypothesis: {hypothesis_description}

Sources found:
{source_context}

Respond with ONLY one of these labels:
- probably_known: The sources clearly discuss this idea
- modification: The sources discuss related ideas; this might be a refinement
- unable_to_determine: The sources don't provide enough context to assess novelty

Do not claim the hypothesis is "original" or "never existed before". Instead, indicate whether the sources suggest it's known, a modification of known work, or whether you cannot determine from these sources."""

        try:
            response = self.ai_provider.generate_text(prompt, max_tokens=100)
            # Extract the assessment from response
            if "probably_known" in response.lower():
                return "probably_known"
            elif "modification" in response.lower():
                return "modification"
            else:
                return "unable_to_determine"
        except Exception as e:
            return "unable_to_determine"
