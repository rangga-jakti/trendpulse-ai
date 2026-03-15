"""
TrendPulse AI - LLM Service
Uses Groq API for AI-powered trend analysis and content generation
"""
import json
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class LLMService:
    """Service for interacting with LLM APIs (Groq/OpenAI compatible)"""
    
    def __init__(self):
        self.groq_api_key = settings.GROQ_API_KEY
        self.model = settings.LLM_MODEL
        self.max_tokens = settings.LLM_MAX_TOKENS
    
    def _call_groq(self, messages, temperature=0.7):
        """Make a call to Groq API"""
        try:
            from groq import Groq
            client = Groq(api_key=self.groq_api_key)
            
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=temperature,
            )
            
            return {
                'content': response.choices[0].message.content,
                'tokens': response.usage.total_tokens,
                'model': self.model,
            }
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            return None
    
    def _call_openai(self, messages, temperature=0.7):
        """Fallback: Make a call to OpenAI API"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            
            response = client.chat.completions.create(
                model='gpt-4o-mini',
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=temperature,
            )
            
            return {
                'content': response.choices[0].message.content,
                'tokens': response.usage.total_tokens,
                'model': 'gpt-4o-mini',
            }
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return None
    
    def call_llm(self, messages, temperature=0.7):
        """Call LLM with fallback - Groq first, then OpenAI"""
        if self.groq_api_key:
            result = self._call_groq(messages, temperature)
            if result:
                return result
        
        if settings.OPENAI_API_KEY:
            return self._call_openai(messages, temperature)
        
        logger.error("No LLM API keys configured!")
        return None
    
    def analyze_trend(self, topic, virality_score=None, news_articles=None):
        """Generate AI analysis for a trending topic"""
        
        # Build context
        news_context = ""
        if news_articles:
            headlines = [a.title for a in news_articles[:5]]
            news_context = f"\n\nHeadline berita terkait:\n" + "\n".join(f"- {h}" for h in headlines)
        
        virality_context = ""
        if virality_score:
            virality_context = f"\nSkor viralitas: {virality_score:.1f}/100"
        
        messages = [
            {
                "role": "system",
                "content": """Kamu adalah analis tren digital senior yang ahli dalam memahami tren internet Indonesia dan global. 
                Berikan analisis yang mendalam, akurat, dan bermanfaat dalam Bahasa Indonesia.
                Selalu berikan respons dalam format JSON yang valid tanpa markdown atau kode blok."""
            },
            {
                "role": "user",
                "content": f"""Analisis tren berikut secara mendalam:

Topik: "{topic.keyword}"
Kategori: {topic.get_category_display()}
Interest saat ini: {topic.current_interest:.1f}/100
Growth rate: {topic.growth_rate:.1f}%{virality_context}{news_context}

Berikan analisis dalam format JSON berikut (HANYA JSON, tanpa penjelasan lain):
{{
    "why_trending": "penjelasan lengkap mengapa topik ini trending (2-3 paragraf)",
    "potential_impact": "analisis dampak potensial terhadap industri, masyarakat, atau pasar (1-2 paragraf)",
    "target_audience": "siapa yang paling tertarik dengan tren ini",
    "predicted_longevity": "hours|days|weeks|months|permanent",
    "overall_sentiment": "positive|neutral|negative",
    "key_drivers": ["faktor 1", "faktor 2", "faktor 3"],
    "risks": ["risiko 1", "risiko 2"],
    "opportunities": ["peluang 1", "peluang 2", "peluang 3"]
}}"""
            }
        ]
        
        result = self.call_llm(messages, temperature=0.6)
        
        if not result:
            return None
        
        try:
            # Parse JSON response
            content = result['content'].strip()
            # Remove any markdown code blocks if present
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
            
            data = json.loads(content)
            data['tokens_used'] = result['tokens']
            data['model_used'] = result['model']
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}\nContent: {result['content'][:200]}")
            # Return a structured response from raw text
            return {
                'why_trending': result['content'][:500],
                'potential_impact': 'Analisis tidak tersedia saat ini.',
                'target_audience': 'Umum',
                'predicted_longevity': 'days',
                'overall_sentiment': 'neutral',
                'key_drivers': [],
                'risks': [],
                'opportunities': [],
                'tokens_used': result['tokens'],
                'model_used': result['model'],
            }
    
    def generate_content_ideas(self, topic, insight_data=None):
        """Generate content ideas for multiple platforms"""
        
        context = ""
        if insight_data:
            context = f"\nMengapa trending: {insight_data.get('why_trending', '')[:200]}"
            context += f"\nTarget audience: {insight_data.get('target_audience', '')}"
        
        messages = [
            {
                "role": "system",
                "content": """Kamu adalah content strategist dan digital marketing expert Indonesia.
                Buat ide konten yang kreatif, viral-worthy, dan relevan dengan pasar Indonesia.
                Respons HANYA dalam format JSON valid."""
            },
            {
                "role": "user",
                "content": f"""Buat ide konten lengkap untuk topik trending: "{topic.keyword}"{context}

Format JSON yang diperlukan:
{{
    "youtube": [
        {{
            "title": "judul video yang menarik",
            "description": "deskripsi singkat konsep video",
            "hooks": ["opening hook 1", "opening hook 2"],
            "estimated_reach": "estimasi jangkauan",
            "difficulty": "easy|medium|hard"
        }}
    ],
    "tiktok": [
        {{
            "title": "ide konten TikTok",
            "description": "format dan konsep video pendek",
            "hooks": ["hook viral 1", "hook viral 2"],
            "estimated_reach": "estimasi jangkauan",
            "difficulty": "easy|medium|hard"
        }}
    ],
    "blog": [
        {{
            "title": "judul artikel blog/SEO friendly",
            "description": "struktur dan angle artikel",
            "hooks": ["angle 1", "angle 2"],
            "estimated_reach": "estimasi pembaca",
            "difficulty": "easy|medium|hard"
        }}
    ],
    "business": [
        {{
            "title": "peluang bisnis atau monetisasi",
            "description": "cara memanfaatkan tren untuk bisnis",
            "hooks": ["model bisnis 1", "model bisnis 2"],
            "estimated_reach": "potensi pasar",
            "difficulty": "easy|medium|hard"
        }}
    ]
}}

Buat MASING-MASING 2 ide untuk setiap platform."""
            }
        ]
        
        result = self.call_llm(messages, temperature=0.8)
        
        if not result:
            return {}
        
        try:
            content = result['content'].strip()
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
            
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse content ideas JSON: {e}")
            return {}
    
    def generate_quick_summary(self, topic):
        """Generate a quick 2-3 sentence summary for dashboard cards"""
        messages = [
            {
                "role": "system", 
                "content": "Kamu analis tren digital. Berikan ringkasan singkat dalam 2 kalimat Bahasa Indonesia yang jelas dan informatif. Hanya teks biasa, tanpa format apapun."
            },
            {
                "role": "user",
                "content": f'Mengapa "{topic.keyword}" sedang trending di Indonesia dengan growth rate {topic.growth_rate:.0f}%? Jelaskan dalam 2 kalimat singkat.'
            }
        ]
        
        result = self.call_llm(messages, temperature=0.5)
        if result:
            return result['content'].strip()
        return f"Topik '{topic.keyword}' sedang mendapat perhatian besar di Indonesia."
