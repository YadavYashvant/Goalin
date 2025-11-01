#!/usr/bin/env python3
"""
AI Assistant for Goalin using Google Gemini API
Handles app categorization and productivity analysis
"""

import json
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import subprocess
import google.generativeai as genai

from .config import CONFIG_DIR, DATA_DIR

logger = logging.getLogger(__name__)

# AI configuration paths
AI_CONFIG_FILE = CONFIG_DIR / 'ai_config.json'
APP_CATEGORIES_FILE = DATA_DIR / 'app_categories.json'
AI_INSIGHTS_CACHE_FILE = DATA_DIR / 'ai_insights_cache.json'


class AIAssistant:
    """AI-powered assistant for smart categorization and productivity analysis"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize AI Assistant
        
        Args:
            api_key: Gemini API key (if None, loads from config)
        """
        self.api_key = api_key or self._load_api_key()
        self.model = None
        self.app_categories: Dict[str, str] = {}
        self.category_definitions: Dict[str, str] = {}
        self.insights_cache: Dict[str, Dict] = {}
        
        if self.api_key:
            self._initialize_model()
            self._load_app_categories()
            self._load_insights_cache()
    
    def _load_api_key(self) -> Optional[str]:
        """Load API key from config file"""
        try:
            if AI_CONFIG_FILE.exists():
                with open(AI_CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    return config.get('gemini_api_key')
        except Exception as e:
            logger.error(f"Failed to load API key: {e}")
        return None
    
    def save_api_key(self, api_key: str) -> bool:
        """
        Save API key to config file
        
        Args:
            api_key: Gemini API key
            
        Returns:
            True if successful
        """
        try:
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            config = {'gemini_api_key': api_key}
            with open(AI_CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)
            self.api_key = api_key
            self._initialize_model()
            logger.info("API key saved successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to save API key: {e}")
            return False
    
    def _initialize_model(self):
        """Initialize Gemini model"""
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
            logger.info("Gemini model initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {e}")
            self.model = None
    
    def _load_app_categories(self):
        """Load previously categorized apps from file"""
        try:
            if APP_CATEGORIES_FILE.exists():
                with open(APP_CATEGORIES_FILE, 'r') as f:
                    data = json.load(f)
                    self.app_categories = data.get('apps', {})
                    self.category_definitions = data.get('categories', {})
                logger.info(f"Loaded {len(self.app_categories)} app categories")
        except Exception as e:
            logger.error(f"Failed to load app categories: {e}")
    
    def _save_app_categories(self):
        """Save app categories to file"""
        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            data = {
                'apps': self.app_categories,
                'categories': self.category_definitions
            }
            with open(APP_CATEGORIES_FILE, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved {len(self.app_categories)} app categories")
        except Exception as e:
            logger.error(f"Failed to save app categories: {e}")
    
    def _load_insights_cache(self):
        """Load cached AI insights from file"""
        try:
            if AI_INSIGHTS_CACHE_FILE.exists():
                with open(AI_INSIGHTS_CACHE_FILE, 'r') as f:
                    self.insights_cache = json.load(f)
                logger.info(f"Loaded {len(self.insights_cache)} cached insights")
        except Exception as e:
            logger.error(f"Failed to load insights cache: {e}")
            self.insights_cache = {}
    
    def _save_insights_cache(self):
        """Save AI insights cache to file"""
        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            with open(AI_INSIGHTS_CACHE_FILE, 'w') as f:
                json.dump(self.insights_cache, f, indent=2)
            logger.info(f"Saved {len(self.insights_cache)} insights to cache")
        except Exception as e:
            logger.error(f"Failed to save insights cache: {e}")
    
    def get_cached_insights(self, date_key: str) -> Optional[Dict]:
        """
        Get cached insights for a specific date
        
        Args:
            date_key: Date in YYYY-MM-DD format
            
        Returns:
            Cached insights dictionary or None
        """
        return self.insights_cache.get(date_key)
    
    def cache_insights(self, date_key: str, insights: Dict):
        """
        Cache insights for a specific date
        
        Args:
            date_key: Date in YYYY-MM-DD format
            insights: Insights dictionary to cache
        """
        self.insights_cache[date_key] = insights
        self._save_insights_cache()
    
    def detect_installed_apps(self) -> List[str]:
        """
        Detect all installed applications on the system
        
        Returns:
            List of application names
        """
        apps = set()
        
        try:
            # Method 1: Check desktop files
            desktop_dirs = [
                Path('/usr/share/applications'),
                Path('/usr/local/share/applications'),
                Path.home() / '.local/share/applications'
            ]
            
            for desktop_dir in desktop_dirs:
                if desktop_dir.exists():
                    for desktop_file in desktop_dir.glob('*.desktop'):
                        # Parse desktop file to get app name
                        try:
                            with open(desktop_file, 'r') as f:
                                for line in f:
                                    if line.startswith('Name='):
                                        app_name = line.split('=', 1)[1].strip()
                                        apps.add(app_name)
                                        break
                        except:
                            continue
            
            # Method 2: Check common binary directories
            bin_dirs = ['/usr/bin', '/usr/local/bin', str(Path.home() / '.local/bin')]
            for bin_dir in bin_dirs:
                bin_path = Path(bin_dir)
                if bin_path.exists():
                    for binary in bin_path.iterdir():
                        if binary.is_file() and binary.stat().st_mode & 0o111:
                            apps.add(binary.name)
            
            logger.info(f"Detected {len(apps)} installed applications")
            return sorted(list(apps))
            
        except Exception as e:
            logger.error(f"Failed to detect installed apps: {e}")
            return []
    
    def categorize_apps(self, apps: List[str], progress_callback=None) -> Dict[str, str]:
        """
        Categorize a list of applications using AI
        
        Args:
            apps: List of application names
            progress_callback: Optional callback function(current, total, app_name)
            
        Returns:
            Dictionary mapping app names to categories
        """
        if not self.model:
            logger.error("AI model not initialized")
            return {}
        
        # Filter out apps that are already categorized
        uncategorized_apps = [app for app in apps if app not in self.app_categories]
        
        if not uncategorized_apps:
            logger.info("All apps already categorized")
            return self.app_categories
        
        logger.info(f"Categorizing {len(uncategorized_apps)} applications...")
        
        # Process apps in batches for efficiency
        batch_size = 20
        for i in range(0, len(uncategorized_apps), batch_size):
            batch = uncategorized_apps[i:i + batch_size]
            
            prompt = f"""You are an expert at categorizing software applications. 
Analyze the following application names and categorize each one into the most appropriate category.

Application names:
{json.dumps(batch, indent=2)}

Categories to choose from:
- Development: IDEs, code editors, terminals, version control, debugging tools
- Browser: Web browsers and related tools
- Communication: Email, chat, video conferencing, social media clients
- Media: Video/audio players, image editors, video editors, music production
- Office: Document editors, spreadsheets, presentations, PDF readers, note-taking
- Gaming: Games and gaming platforms
- Productivity: Task managers, calendars, time tracking, project management
- Design: Graphic design, 3D modeling, CAD, UI/UX tools
- System: File managers, system settings, utilities, package managers
- Education: Learning platforms, educational software, reference tools
- Other: Anything that doesn't fit above categories

Respond with ONLY a valid JSON object mapping each app name to its category. Example:
{{"app1": "Development", "app2": "Browser", "app3": "Media"}}

Important: Return ONLY the JSON object, no explanations or additional text."""

            try:
                response = self.model.generate_content(prompt)
                result_text = response.text.strip()
                
                # Extract JSON from response (sometimes AI adds markdown code blocks)
                if '```json' in result_text:
                    result_text = result_text.split('```json')[1].split('```')[0].strip()
                elif '```' in result_text:
                    result_text = result_text.split('```')[1].split('```')[0].strip()
                
                categorizations = json.loads(result_text)
                
                # Update app categories
                for app, category in categorizations.items():
                    self.app_categories[app] = category
                    if progress_callback:
                        current = min(i + batch.index(app) + 1, len(uncategorized_apps))
                        progress_callback(current, len(uncategorized_apps), app)
                
                logger.info(f"Categorized batch of {len(categorizations)} apps")
                
            except Exception as e:
                logger.error(f"Failed to categorize batch: {e}")
                # Fallback: categorize as "Other"
                for app in batch:
                    self.app_categories[app] = "Other"
        
        # Save updated categories
        self._save_app_categories()
        
        return self.app_categories
    
    def get_app_category(self, app_name: str) -> str:
        """
        Get category for a specific app
        
        Args:
            app_name: Application name
            
        Returns:
            Category name
        """
        # Check if already categorized
        if app_name in self.app_categories:
            return self.app_categories[app_name]
        
        # Try to categorize this single app
        if self.model:
            try:
                prompt = f"""Categorize this application: "{app_name}"

Choose ONE category from: Development, Browser, Communication, Media, Office, Gaming, Productivity, Design, System, Education, Other

Respond with ONLY the category name, nothing else."""
                
                response = self.model.generate_content(prompt)
                category = response.text.strip()
                
                # Validate category
                valid_categories = ['Development', 'Browser', 'Communication', 'Media', 'Office', 
                                  'Gaming', 'Productivity', 'Design', 'System', 'Education', 'Other']
                if category in valid_categories:
                    self.app_categories[app_name] = category
                    self._save_app_categories()
                    return category
            except Exception as e:
                logger.error(f"Failed to categorize app {app_name}: {e}")
        
        return 'Other'
    
    def analyze_productivity(self, day_data: Dict, date_key: str = None) -> Dict:
        """
        Analyze productivity for a day using AI (with caching)
        
        Args:
            day_data: Dictionary containing:
                - total_active_time: seconds
                - categories: dict of category -> time
                - apps: dict of app -> time
                - hourly_pattern: dict of hour -> activity
            date_key: Date in YYYY-MM-DD format for caching
                
        Returns:
            Dictionary with:
                - productivity_score: 0-100
                - productivity_level: 'High', 'Medium', 'Low'
                - insights: list of insights
                - recommendations: list of recommendations
        """
        # Check cache first if date_key provided
        if date_key:
            cached = self.get_cached_insights(date_key)
            if cached:
                logger.info(f"Using cached insights for {date_key}")
                return cached
        
        if not self.model:
            logger.error("AI model not initialized")
            return self._fallback_productivity_analysis(day_data)
        
        try:
            # Format the data for AI analysis
            total_hours = day_data.get('total_active_time', 0) / 3600
            categories_summary = {k: round(v / 3600, 1) for k, v in day_data.get('categories', {}).items()}
            top_apps = dict(sorted(day_data.get('apps', {}).items(), 
                                 key=lambda x: x[1], reverse=True)[:10])
            top_apps_hours = {k: round(v / 3600, 1) for k, v in top_apps.items()}
            
            hourly_pattern = day_data.get('hourly_pattern', {})
            active_hours = [h for h, duration in hourly_pattern.items() if duration > 1800]  # > 30 min
            
            prompt = f"""You are an expert productivity analyst. Analyze this user's daily computer activity and provide insights.

Activity Summary:
- Total Active Time: {total_hours:.1f} hours
- Time by Category: {json.dumps(categories_summary, indent=2)}
- Top Applications: {json.dumps(top_apps_hours, indent=2)}
- Active Hours: {len(active_hours)} hours with significant activity
- Most Active Hours: {sorted(active_hours)[:5] if active_hours else 'None'}

Based on this data:
1. Calculate a productivity score (0-100) considering:
   - Time spent in productive categories (Development, Office, Education, Productivity)
   - Balance between different types of work
   - Consistency of work patterns
   - Deep focus sessions (concentrated time in productive apps)

2. Identify the productivity level: High (80-100), Medium (50-79), or Low (0-49)

3. Provide 3-5 specific insights about the user's work patterns

4. Give 3-5 actionable recommendations to improve productivity

Respond with ONLY a valid JSON object in this format:
{{
  "productivity_score": 75,
  "productivity_level": "Medium",
  "insights": [
    "Insight 1",
    "Insight 2",
    "Insight 3"
  ],
  "recommendations": [
    "Recommendation 1",
    "Recommendation 2",
    "Recommendation 3"
  ]
}}"""

            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Extract JSON from response
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0].strip()
            elif '```' in result_text:
                result_text = result_text.split('```')[1].split('```')[0].strip()
            
            analysis = json.loads(result_text)
            logger.info(f"AI productivity analysis completed: {analysis['productivity_score']}%")
            
            # Cache the result if date_key provided
            if date_key:
                self.cache_insights(date_key, analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze productivity with AI: {e}")
            return self._fallback_productivity_analysis(day_data)
    
    def _fallback_productivity_analysis(self, day_data: Dict) -> Dict:
        """Fallback productivity analysis without AI"""
        total_active = day_data.get('total_active_time', 0)
        categories = day_data.get('categories', {})
        
        # Calculate score based on productive categories
        productive_categories = ['Development', 'Office', 'Education', 'Productivity', 'Design']
        productive_time = sum(categories.get(cat, 0) for cat in productive_categories)
        
        score = (productive_time / total_active * 100) if total_active > 0 else 0
        
        if score >= 80:
            level = 'High'
        elif score >= 50:
            level = 'Medium'
        else:
            level = 'Low'
        
        return {
            'productivity_score': round(score, 1),
            'productivity_level': level,
            'insights': [
                f'Total active time: {total_active / 3600:.1f} hours',
                f'Productive time: {productive_time / 3600:.1f} hours',
                f'Top category: {max(categories, key=categories.get) if categories else "None"}'
            ],
            'recommendations': [
                'Enable AI analysis for detailed insights',
                'Track more activities for better analysis',
                'Review your app categories'
            ]
        }
    
    def is_configured(self) -> bool:
        """Check if AI is properly configured"""
        return self.api_key is not None and self.model is not None
