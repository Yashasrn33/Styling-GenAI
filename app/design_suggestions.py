"""
Generative Design Suggestions Module
Handles creative design suggestions based on user preferences and style inputs.
"""

import random
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from config import config, PROMPT_TEMPLATES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DesignElement:
    """Represents a design element with properties"""
    name: str
    colors: List[str]
    patterns: List[str]
    styles: List[str]
    description: str


class DesignDatabase:
    """Database of design elements and inspiration"""
    
    def __init__(self):
        self.color_palettes = {
            "minimalist": ["white", "black", "gray", "beige", "cream"],
            "vibrant": ["red", "orange", "yellow", "pink", "purple", "turquoise"],
            "earth": ["brown", "forest green", "tan", "rust", "olive"],
            "ocean": ["navy", "teal", "aqua", "white", "sandy beige"],
            "sunset": ["orange", "pink", "purple", "gold", "deep red"],
            "monochrome": ["black", "white", "gray"],
            "pastel": ["light pink", "lavender", "mint green", "baby blue", "peach"],
            "neon": ["electric blue", "hot pink", "lime green", "bright yellow", "orange"],
            "autumn": ["burgundy", "burnt orange", "golden yellow", "brown", "dark green"],
            "spring": ["light green", "yellow", "pink", "light blue", "white"]
        }
        
        self.art_styles = {
            "geometric": {
                "patterns": ["triangles", "hexagons", "diamonds", "stripes", "chevrons"],
                "description": "clean lines and mathematical shapes"
            },
            "organic": {
                "patterns": ["flowing curves", "leaf patterns", "wave designs", "cloud shapes"],
                "description": "natural, flowing forms inspired by nature"
            },
            "abstract": {
                "patterns": ["paint splatters", "brush strokes", "color blocks", "gradients"],
                "description": "non-representational artistic expressions"
            },
            "vintage": {
                "patterns": ["damask", "paisley", "florals", "art deco patterns"],
                "description": "classic patterns with nostalgic appeal"
            },
            "modern": {
                "patterns": ["clean lines", "minimalist graphics", "typography", "logos"],
                "description": "contemporary and sleek design elements"
            },
            "grunge": {
                "patterns": ["distressed textures", "torn edges", "splatter effects", "rough brushes"],
                "description": "raw, edgy aesthetic with weathered appearance"
            },
            "pop_art": {
                "patterns": ["bold graphics", "comic book style", "halftone dots", "bright colors"],
                "description": "bold, commercial art inspired designs"
            },
            "japanese": {
                "patterns": ["cherry blossoms", "waves", "mountains", "traditional motifs"],
                "description": "elegant Japanese-inspired designs"
            },
            "street_art": {
                "patterns": ["graffiti style", "urban elements", "spray paint effects", "stencils"],
                "description": "urban-inspired street art aesthetics"
            },
            "nature": {
                "patterns": ["trees", "flowers", "animals", "landscapes"],
                "description": "designs inspired by the natural world"
            }
        }
        
        self.themes = {
            "space": ["stars", "planets", "galaxies", "astronauts", "rockets"],
            "music": ["instruments", "sound waves", "musical notes", "vinyl records"],
            "travel": ["maps", "landmarks", "airplanes", "compasses", "vintage postcards"],
            "sports": ["geometric sports graphics", "team logos", "equipment silhouettes"],
            "technology": ["circuit patterns", "digital glitch", "code snippets", "pixel art"],
            "food": ["coffee cups", "pizza slices", "fruits", "cooking utensils"],
            "animals": ["cats", "dogs", "wild animals", "birds", "marine life"],
            "flowers": ["roses", "sunflowers", "tropical flowers", "botanical illustrations"],
            "typography": ["motivational quotes", "single words", "artistic lettering"],
            "celestial": ["moon phases", "constellations", "sun and moon", "cosmic elements"]
        }
        
        self.placement_options = {
            "front_center": "centered on the front chest",
            "front_large": "large design across the entire front",
            "back_large": "statement design on the back",
            "chest_small": "small design on the left chest",
            "sleeve": "design running down the sleeve",
            "all_over": "pattern covering the entire garment",
            "pocket": "small design in the pocket area",
            "collar": "design around the collar or neckline"
        }


class DesignSuggestionEngine:
    """Generates creative design suggestions based on user input"""
    
    def __init__(self):
        self.design_db = DesignDatabase()
        self.preference_history = []
    
    def analyze_preferences(self, user_input: str) -> Dict[str, Any]:
        """Analyze user input to extract design preferences"""
        user_input_lower = user_input.lower()
        
        preferences = {
            "styles": [],
            "colors": [],
            "themes": [],
            "complexity": "medium",
            "vibe": "casual"
        }
        
        # Detect art styles
        for style, data in self.design_db.art_styles.items():
            if style in user_input_lower or any(pattern in user_input_lower for pattern in data["patterns"]):
                preferences["styles"].append(style)
        
        # Detect color preferences
        for palette_name, colors in self.design_db.color_palettes.items():
            if palette_name in user_input_lower or any(color in user_input_lower for color in colors):
                preferences["colors"].extend(colors[:3])  # Take first 3 colors
                break
        
        # Detect themes
        for theme, elements in self.design_db.themes.items():
            if theme in user_input_lower or any(element in user_input_lower for element in elements):
                preferences["themes"].append(theme)
        
        # Detect complexity
        if any(word in user_input_lower for word in ["simple", "minimal", "clean", "subtle"]):
            preferences["complexity"] = "low"
        elif any(word in user_input_lower for word in ["complex", "detailed", "intricate", "elaborate"]):
            preferences["complexity"] = "high"
        
        # Detect vibe
        if any(word in user_input_lower for word in ["bold", "loud", "striking", "dramatic"]):
            preferences["vibe"] = "bold"
        elif any(word in user_input_lower for word in ["elegant", "sophisticated", "classy", "refined"]):
            preferences["vibe"] = "elegant"
        elif any(word in user_input_lower for word in ["fun", "playful", "cute", "whimsical"]):
            preferences["vibe"] = "playful"
        
        return preferences
    
    def generate_suggestions(self, user_input: str, garment_type: str = "t-shirt", 
                           num_suggestions: int = None) -> List[Dict[str, Any]]:
        """Generate design suggestions based on user input"""
        num_suggestions = num_suggestions or config.design_max_suggestions
        preferences = self.analyze_preferences(user_input)
        
        suggestions = []
        
        for i in range(num_suggestions):
            suggestion = self._create_single_suggestion(preferences, garment_type, i)
            suggestions.append(suggestion)
        
        return suggestions
    
    def _create_single_suggestion(self, preferences: Dict[str, Any], 
                                garment_type: str, variation: int) -> Dict[str, Any]:
        """Create a single design suggestion"""
        
        # Select style
        if preferences["styles"]:
            style = random.choice(preferences["styles"])
        else:
            style = random.choice(list(self.design_db.art_styles.keys()))
        
        style_data = self.design_db.art_styles[style]
        
        # Select colors
        if preferences["colors"]:
            colors = random.sample(preferences["colors"], 
                                 min(len(preferences["colors"]), 3))
        else:
            palette = random.choice(list(self.design_db.color_palettes.values()))
            colors = random.sample(palette, min(len(palette), 3))
        
        # Select theme
        if preferences["themes"]:
            theme = random.choice(preferences["themes"])
            theme_elements = self.design_db.themes[theme]
        else:
            theme = random.choice(list(self.design_db.themes.keys()))
            theme_elements = self.design_db.themes[theme]
        
        # Select pattern
        pattern = random.choice(style_data["patterns"])
        
        # Select placement
        placement_key = random.choice(list(self.design_db.placement_options.keys()))
        placement = self.design_db.placement_options[placement_key]
        
        # Select theme element
        theme_element = random.choice(theme_elements)
        
        # Create description
        description = self._create_description(
            style, colors, pattern, theme_element, placement, 
            preferences["vibe"], preferences["complexity"]
        )
        
        # Create detailed suggestion
        suggestion = {
            "id": f"design_{variation + 1}",
            "title": f"{style.title()} {theme.title()} Design",
            "style": style,
            "colors": colors,
            "pattern": pattern,
            "theme": theme,
            "theme_element": theme_element,
            "placement": placement,
            "placement_key": placement_key,
            "description": description,
            "vibe": preferences["vibe"],
            "complexity": preferences["complexity"],
            "garment_type": garment_type,
            "estimated_colors": len(colors),
            "print_method": self._suggest_print_method(style, len(colors), preferences["complexity"])
        }
        
        return suggestion
    
    def _create_description(self, style: str, colors: List[str], pattern: str, 
                          theme_element: str, placement: str, vibe: str, 
                          complexity: str) -> str:
        """Create a detailed description of the design"""
        
        color_desc = self._format_colors(colors)
        
        base_descriptions = [
            f"A {vibe} {style} design featuring {theme_element} in {color_desc}",
            f"Picture a {style}-inspired {theme_element} design using {color_desc}",
            f"Imagine a {vibe} {pattern} pattern incorporating {theme_element} in {color_desc}",
            f"A {complexity}-complexity {style} design with {theme_element} elements in {color_desc}"
        ]
        
        base = random.choice(base_descriptions)
        
        # Add placement
        placement_desc = f", positioned {placement}"
        
        # Add style details
        if style == "geometric":
            style_detail = " with clean, mathematical precision"
        elif style == "organic":
            style_detail = " with flowing, natural curves"
        elif style == "vintage":
            style_detail = " with classic, timeless appeal"
        elif style == "grunge":
            style_detail = " with a raw, edgy aesthetic"
        elif style == "japanese":
            style_detail = " with elegant Eastern influences"
        else:
            style_detail = f" with {self.design_db.art_styles[style]['description']}"
        
        # Add finishing touches
        finishing_options = [
            ". This design would work beautifully with screen printing.",
            ". Perfect for digital printing to capture all the color nuances.",
            ". The design would look stunning with a subtle texture overlay.",
            ". Consider adding a slight vintage wash effect for extra character.",
            ". The design could be enhanced with metallic accents for special occasions."
        ]
        
        finishing = random.choice(finishing_options)
        
        return base + placement_desc + style_detail + finishing
    
    def _format_colors(self, colors: List[str]) -> str:
        """Format color list into natural language"""
        if len(colors) == 1:
            return colors[0]
        elif len(colors) == 2:
            return f"{colors[0]} and {colors[1]}"
        else:
            return f"{', '.join(colors[:-1])}, and {colors[-1]}"
    
    def _suggest_print_method(self, style: str, num_colors: int, complexity: str) -> str:
        """Suggest the best printing method for the design"""
        if num_colors <= 2 and complexity == "low":
            return "screen printing"
        elif num_colors > 4 or complexity == "high":
            return "digital printing"
        elif style in ["vintage", "grunge"]:
            return "heat transfer"
        else:
            return "screen printing"
    
    def refine_suggestion(self, suggestion: Dict[str, Any], 
                         feedback: str) -> Dict[str, Any]:
        """Refine a suggestion based on user feedback"""
        feedback_lower = feedback.lower()
        
        # Create a copy of the suggestion
        refined = suggestion.copy()
        
        # Color refinements
        if "brighter" in feedback_lower or "more vibrant" in feedback_lower:
            vibrant_colors = self.design_db.color_palettes["vibrant"]
            refined["colors"] = random.sample(vibrant_colors, 
                                            min(len(vibrant_colors), 3))
        elif "darker" in feedback_lower or "muted" in feedback_lower:
            earth_colors = self.design_db.color_palettes["earth"]
            refined["colors"] = random.sample(earth_colors, 
                                            min(len(earth_colors), 3))
        elif "pastel" in feedback_lower or "softer" in feedback_lower:
            refined["colors"] = self.design_db.color_palettes["pastel"][:3]
        
        # Style refinements
        if "simpler" in feedback_lower or "cleaner" in feedback_lower:
            refined["style"] = "minimalist"
            refined["complexity"] = "low"
        elif "more complex" in feedback_lower or "detailed" in feedback_lower:
            refined["complexity"] = "high"
        
        # Size/placement refinements
        if "smaller" in feedback_lower:
            refined["placement_key"] = "chest_small"
            refined["placement"] = "small design on the left chest"
        elif "larger" in feedback_lower or "bigger" in feedback_lower:
            refined["placement_key"] = "front_large"
            refined["placement"] = "large design across the entire front"
        
        # Regenerate description
        refined["description"] = self._create_description(
            refined["style"], refined["colors"], refined["pattern"],
            refined["theme_element"], refined["placement"],
            refined["vibe"], refined["complexity"]
        )
        
        return refined
    
    def get_trending_suggestions(self, garment_type: str = "t-shirt") -> List[Dict[str, Any]]:
        """Get trending design suggestions"""
        trending_themes = ["minimalist", "nature", "geometric", "vintage", "space"]
        suggestions = []
        
        for theme in trending_themes[:3]:
            fake_input = f"I want a {theme} design"
            suggestion = self.generate_suggestions(fake_input, garment_type, 1)[0]
            suggestion["trending"] = True
            suggestions.append(suggestion)
        
        return suggestions
    
    def save_preferences(self, user_input: str, selected_suggestion: Dict[str, Any]) -> None:
        """Save user preferences for future suggestions"""
        preferences = self.analyze_preferences(user_input)
        preferences["selected_suggestion"] = selected_suggestion
        self.preference_history.append(preferences)
        
        # Keep only last 10 preferences
        if len(self.preference_history) > 10:
            self.preference_history = self.preference_history[-10:]


# Singleton instance
design_engine = DesignSuggestionEngine() 