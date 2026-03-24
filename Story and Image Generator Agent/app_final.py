from flask import Flask, jsonify, request, send_from_directory
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError
import os
import json
import re
import uuid
import sys
import time
import logging
import traceback
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import hashlib
import random

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('story_generation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logger.error("GEMINI_API_KEY not set.")
    sys.exit(1)

client = genai.Client(api_key=GEMINI_API_KEY)
IMAGE_GENERATION_MODEL_NAME = "gemini-2.0-flash-preview-image-generation"

# Configuration constants
MAX_RETRIES = 8
BASE_DELAY = 2.0
MAX_DELAY = 60.0

# --- Pydantic Models ---
class Character(BaseModel):
    name: str = Field(description="The character's full name.")
    description: str = Field(description="A detailed paragraph describing the character's physical appearance, personality traits, and backstory.")
    role: str = Field(description="The character's primary role and motivations within the storyline.")
    age: str = Field(description="The approximate age or age group of the character.")
    skin_tone: str = Field(description="The character's skin tone.")
    hair: str = Field(description="The style and color of the character's hair.")
    clothing: str = Field(description="A detailed description of the character's attire.")
    expression: str = Field(description="The character's typical facial expression or mood.")

class StoryMetadata(BaseModel):
    request_id: str
    generation_timestamp: str
    total_characters: int
    total_background_images: int
    total_scene_images: int
    total_visualization_images: int
    story_scenes: int
    explainer_scenes: int
    generation_duration: float
    api_calls_made: int
    retry_attempts: int

# --- Helper Functions ---
def generate_request_id() -> str:
    """Generate a unique request ID for tracking"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    random_id = str(uuid.uuid4())[:8]
    return f"STORY_{timestamp}_{random_id}"

def exponential_backoff(attempt: int) -> float:
    delay = BASE_DELAY * (2 ** attempt)
    delay = min(delay, MAX_DELAY)
    return delay + random.uniform(0, 1.5)  # jitter up to 1.5s

def retry_with_backoff(func, max_retries: int = MAX_RETRIES, request_id: str = ""):
    """Retry function with exponential backoff"""
    for attempt in range(max_retries + 1):
        try:
            logger.info(f"[{request_id}] Attempting operation (attempt {attempt + 1}/{max_retries + 1})")
            result = func()
            logger.info(f"[{request_id}] Operation successful on attempt {attempt + 1}")
            return result, attempt
        except Exception as e:
            logger.warning(f"[{request_id}] Attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries:
                delay = exponential_backoff(attempt)
                logger.info(f"[{request_id}] Retrying in {delay:.2f} seconds...")
                time.sleep(delay)
            else:
                logger.error(f"[{request_id}] All {max_retries + 1} attempts failed")
                raise e

def validate_and_enhance_story_data(story_data: dict, request_id: str) -> dict:
    """Validate and enhance story data"""
    logger.info(f"[{request_id}] Validating story data...")
    
    character_list = story_data.get("characterList", [])
    scenes = story_data.get("sceneWiseDescription", [])
    
    # Validate character descriptions
    char_descriptions = story_data.get("characterDescriptionForT2i", {})
    for char in character_list:
        if char not in char_descriptions:
            logger.warning(f"[{request_id}] Missing description for character: {char}")
            char_descriptions[char] = f"A character named {char} with distinctive features appropriate for the story setting"
    
    story_data["characterDescriptionForT2i"] = char_descriptions
    
    return story_data

def _generate_json_response(prompt: str, request_id: str = "") -> dict:
    """Generate JSON response with retry logic"""
    def _api_call():
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        raw_text = ""
        for part in getattr(response.candidates[0].content, "parts", []):
            if hasattr(part, "text"):
                raw_text += part.text
        
        # More robust JSON extraction
        json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON found in response")
        
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError as e:
            logger.error(f"[{request_id}] JSON decode error: {e}")
            logger.error(f"[{request_id}] Raw text: {raw_text[:500]}...")
            raise e
    
    result, attempts = retry_with_backoff(_api_call, request_id=request_id)
    return result

def _generate_image_internal(prompt_text: str, image_type: str, reference_images: list = None, request_id: str = "") -> Tuple[Optional[str], Optional[str]]:
    """Enhanced image generation with stronger quality controls"""
    def _image_generation():
        contents = [prompt_text]
        
        # Add reference images if provided with better error handling
        if reference_images:
            logger.info(f"[{request_id}] Using {len(reference_images)} reference images for {image_type}")
            valid_refs = 0
            for ref_path in reference_images:
                if os.path.exists(ref_path):
                    try:
                        # Verify image is valid before adding
                        with open(ref_path, 'rb') as f:
                            image_data = f.read()
                        
                        # Basic validation that it's actually image data
                        if len(image_data) > 1000:  # Minimum size check
                            contents.append({
                                'inline_data': {
                                    'mime_type': 'image/png',
                                    'data': image_data
                                }
                            })
                            valid_refs += 1
                            logger.debug(f"[{request_id}] Added valid reference: {os.path.basename(ref_path)}")
                        else:
                            logger.warning(f"[{request_id}] Reference image too small: {ref_path}")
                    except Exception as e:
                        logger.error(f"[{request_id}] Error loading reference image {ref_path}: {e}")
                else:
                    logger.warning(f"[{request_id}] Reference image not found: {ref_path}")
            
            logger.info(f"[{request_id}] Successfully loaded {valid_refs}/{len(reference_images)} reference images")
        
        # Generate with enhanced config
        response = client.models.generate_content(
            model=IMAGE_GENERATION_MODEL_NAME,
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"],
                # Add any additional config options for quality
            )
        )

        if not response or not response.candidates:
            logger.error(f"[{request_id}] Empty response from API for image type: {image_type}")
            raise ValueError("Empty response from image generation API")

        candidate = response.candidates[0]
        content = getattr(candidate, "content", None)
        if not content or not hasattr(content, "parts"):
            raise ValueError("Missing 'content.parts' in API response")

        for part in content.parts:
            if hasattr(part, 'inline_data') and getattr(part.inline_data, 'data', None):
                try:
                    image = Image.open(BytesIO(part.inline_data.data))
                    
                    # Verify image quality before saving
                    if image.size[0] < 512 or image.size[1] < 512:
                        logger.warning(f"[{request_id}] Generated image too small: {image.size}")
                    
                    os.makedirs("static/generated_images", exist_ok=True)
                    image_id = str(uuid.uuid4())
                    file_path = f"static/generated_images/{image_id}.png"
                    
                    # Save with maximum quality
                    image.save(file_path, "PNG", optimize=False, compress_level=1)
                    image_url = f"http://localhost:5000/static/generated_images/{image_id}.png"
                    
                    logger.info(f"[{request_id}] Generated {image_type} image: {image_url} (size: {image.size})")
                    return image_url, file_path
                    
                except Exception as e:
                    logger.error(f"[{request_id}] Failed to process image data: {e}")
                    raise

        raise ValueError("No valid image part found in response")

    try:
        result, attempts = retry_with_backoff(_image_generation, request_id=request_id)
        return result
    except Exception as e:
        logger.error(f"[{request_id}] Failed to generate {image_type} image after all retries: {e}")
        return None, None

def _generate_comprehensive_story(topics: list, general_description: str, style_description: str, request_id: str) -> dict:
    """Generate a comprehensive story with enhanced prompting for longer narratives"""
    
    story_prompt = f"""
You are an expert cinematic storyteller. Create a **simple, engaging, and coherent** feature-length story that blends educational content naturally into the plot.

INPUTS:
- Topics: {topics}
- Story description: {general_description}
- Visual style: {style_description}

STORY RULES:
- Total main characters: **3–5 only** (unique and distinctive).
- In any single scene image: **maximum 3 characters** (plus 1 background).
- Characters must have distinct personalities, looks, and roles.
- Educational moments must feel like a natural part of the story (no breaking immersion).
- Tone: Accessible, heartfelt, visually rich, with emotional and narrative clarity.
- Story should have a clear start, middle, and satisfying ending.

STRUCTURE:
- Act 1: Introduce characters, setting, and inciting incident.
- Act 2: Develop relationships, challenges, and educational moments.
- Act 3: Resolve the main conflict, show character growth, and end on a meaningful note.
- 15–20 scenes total (mix of story progression and educational moments).

OUTPUT EXACTLY in this JSON structure:
{{
  "storyPlot": "Complete longform story with emotional beats, character arcs, and integrated educational moments.",
  "characterList": ["Character1", "Character2", "Character3", ...],
  "characterDescriptionForT2i": {{
    "Character1": "Short but rich physical and personality description for consistent image generation.",
    "Character2": "...",
    ...
  }},
  "sceneWiseDescription": [
    {{
      "actLabel": "ACT 1 - Scene Title",
      "isStoryScene": true/false,
      "charactersInvolved": ["Character1", "Character2"],
      "backgroundSetting": "Specific location with mood, time of day, and atmosphere.",
      "sceneDescriptionForI2i": "What exactly is happening visually in this scene.",
      "narration": "Brief narrative text for voiceover.",
      "characterDialogues": "CharacterName: dialogue line...",
      "soundsDescription": "Key ambient and action sounds.",
      "sceneWiseDescriptionForI2v": "Video camera movement and pacing notes."
    }}
  ]
}}

CONSTRAINTS:
- Follow JSON format exactly — no extra text or explanations.
- Respect all character and scene limits strictly.
- Keep story clear, visual, and easy to follow.
"""


    logger.info(f"[{request_id}] Generating comprehensive story with enhanced prompting...")
    
    try:
        story_data = _generate_json_response(story_prompt, request_id)
        
        # Validate the generated story
        character_count = len(story_data.get("characterList", []))
        scene_count = len(story_data.get("sceneWiseDescription", []))
        story_scenes = len([scene for scene in story_data.get("sceneWiseDescription", []) if scene.get("isStoryScene", True)])
        explainer_scenes = scene_count - story_scenes
        
        logger.info(f"[{request_id}] Generated comprehensive story:")
        logger.info(f"[{request_id}] - Characters: {character_count}")
        logger.info(f"[{request_id}] - Total scenes: {scene_count}")
        logger.info(f"[{request_id}] - Story scenes: {story_scenes}")
        logger.info(f"[{request_id}] - Educational scenes: {explainer_scenes}")
        
        return validate_and_enhance_story_data(story_data, request_id)
        
    except Exception as e:
        logger.error(f"[{request_id}] Error generating story: {e}")
        return {"error": f"Failed to generate story: {str(e)}"}


def process_character_images(character_list: list, character_descriptions: dict, style_description: str, request_id: str) -> Tuple[dict, dict, int]:
    """Process all character image generation with enhanced consistency and quality"""
    logger.info(f"[{request_id}] Processing {len(character_list)} character images...")
    
    character_images = {}
    character_file_paths = {}
    api_calls = 0
    
    for idx, char_name in enumerate(character_list):
        logger.info(f"[{request_id}] Generating character {idx + 1}/{len(character_list)}: {char_name}")
        
        if char_name in character_descriptions:
            char_prompt = character_descriptions[char_name]
            
            # ROBUST CHARACTER PROMPT - Enhanced for clarity and consistency
            full_prompt = (
                f"PROFESSIONAL CHARACTER REFERENCE SHEET in {style_description} art style. "
                f"SINGLE CHARACTER ONLY: {char_prompt}. "
                
                # COMPOSITION REQUIREMENTS
                f"COMPOSITION: Full-body portrait, standing upright, facing directly forward towards camera. "
                f"Character centered in frame, complete figure visible from head to feet. "
                f"Front-facing view only, neutral relaxed expression, natural standing pose. "
                
                # BACKGROUND REQUIREMENTS  
                f"BACKGROUND: Pure white background, completely clean and empty. "
                f"No props, no scenery, no objects, no shadows, no textures on background. "
                f"Character fully isolated against plain white backdrop. "
                
                # QUALITY REQUIREMENTS
                f"VISUAL QUALITY: Sharp focus, high resolution, professional character sheet quality. "
                f"Clear definition of all facial features, clothing details, and physical characteristics. "
                f"Perfect proportions, clean linework, consistent art style throughout. "
                f"Animation reference quality with clear visual consistency markers. "
                
                # STRICT NEGATIVE CONSTRAINTS
                f"AVOID COMPLETELY: Multiple characters, multiple poses, back views, side views, profile angles, "
                f"partial body shots, cropped torso, cropped at waist or chest, background elements, "
                f"props, scenery, other people, animals, text, watermarks, logos, multiple angles, "
                f"action poses, dynamic poses, sitting, lying down, turned away from camera."
            )
            time.sleep(random.uniform(0.5, 2.0))
            image_url, file_path = _generate_image_internal(full_prompt, f"character-{char_name}", request_id=request_id)
            api_calls += 1
            
            if image_url:
                character_images[char_name] = {
                    "name": char_name,
                    "description": char_prompt,
                    "image_url": image_url
                }
                character_file_paths[char_name] = file_path
                logger.info(f"[{request_id}] Successfully generated image for {char_name}")
            else:
                logger.error(f"[{request_id}] Failed to generate image for {char_name}")
                character_images[char_name] = {
                    "name": char_name,
                    "description": char_prompt,
                    "image_url": None
                }
    
    return character_images, character_file_paths, api_calls

def process_background_images(scene_descriptions: list, style_description: str, request_id: str) -> Tuple[dict, dict, int]:
    """Process all background image generation with ZERO character contamination"""
    logger.info(f"[{request_id}] Processing background images...")
    
    background_images = {}
    background_file_paths = {}
    api_calls = 0
    
    # Extract unique backgrounds from story scenes only
    unique_backgrounds = {}
    for scene in scene_descriptions:
        if scene.get("isStoryScene", True):
            bg_setting = scene.get("backgroundSetting", "")
            if bg_setting and bg_setting not in unique_backgrounds:
                bg_hash = hashlib.md5(bg_setting.encode()).hexdigest()[:8]
                unique_backgrounds[bg_setting] = f"bg_{bg_hash}"
    
    logger.info(f"[{request_id}] Found {len(unique_backgrounds)} unique background settings")
    
    for idx, (bg_setting, bg_id) in enumerate(unique_backgrounds.items()):
        logger.info(f"[{request_id}] Generating background {idx + 1}/{len(unique_backgrounds)}: {bg_id}")
        
        # ROBUST BACKGROUND PROMPT - Zero character contamination
        bg_full_prompt = (
                f"{style_description} scenic background illustration. "
                f"Setting: {bg_setting}. "
                f"No characters present. Wide landscape view. "
                f"Detailed environment, atmospheric lighting. "
                f"Avoid: people, animals, text, watermarks."
            )
        
        time.sleep(random.uniform(0.5, 2.0))
        bg_image_url, bg_file_path = _generate_image_internal(bg_full_prompt, f"background-{bg_id}", request_id=request_id)
        api_calls += 1
        
        if bg_image_url:
            background_images[bg_setting] = {
                "id": bg_id,
                "description": bg_setting,
                "image_url": bg_image_url
            }
            background_file_paths[bg_setting] = bg_file_path
            logger.info(f"[{request_id}] Successfully generated background: {bg_id}")
        else:
            logger.error(f"[{request_id}] Failed to generate background: {bg_id}")
    
    return background_images, background_file_paths, api_calls

def process_scene_images(scene_descriptions: list, character_descriptions: dict, character_file_paths: dict, 
    background_file_paths: dict, background_images: dict, style_description: str, request_id: str) -> Tuple[list, int]:
    """Generate scene images with strict background lock, sharp faces, and no duplicates."""

    logger.info(f"[{request_id}] Processing {len(scene_descriptions)} scene images...")
    processed_scenes = []
    api_calls = 0

    for scene_idx, scene in enumerate(scene_descriptions):
        is_story_scene = scene.get("isStoryScene", True)
        characters_in_scene = scene.get("charactersInvolved", [])[:3]  # enforce max 3

        if is_story_scene:
            background_prompt = scene.get("backgroundSetting", "")
            scene_i2i_prompt = scene.get("sceneDescriptionForI2i", "")

            # Collect references: background first, then characters
            reference_images = []
            if background_prompt in background_file_paths:
                reference_images.append(background_file_paths[background_prompt])
            for char in characters_in_scene:
                if char in character_file_paths:
                    reference_images.append(character_file_paths[char])
            reference_images = reference_images[:4]  # max 4 refs total

            # Per-character consistency instructions
            char_instructions = ""
            for char_name in characters_in_scene:
                if char_name in character_descriptions:
                    char_instructions += (
                        f"CHARACTER {char_name} CONSISTENCY:\n"
                        f"- Use provided character reference for PERFECT visual consistency.\n"
                        f"- FACIAL CLARITY: Crystal clear, sharp focus, NO distortions or deformations.\n"
                        f"- Maintain exact appearance: {character_descriptions[char_name][:150]}...\n"
                        f"- Face must be clearly visible, well-lit, and perfectly detailed.\n\n"
                    )

            # Scene prompt
            scene_full_prompt = f"""
            CINEMATIC STORY SCENE — {style_description} style.

            ACTION: {scene_i2i_prompt}
            ENVIRONMENT: {background_prompt}

            BACKGROUND LOCK:
            - Use the provided background reference image EXACTLY as shown.
            - Do not replace, alter, or reinterpret it.
            - Keep identical camera angle, perspective, lighting, and colors.

            CHARACTER RULES:
            - Exactly {len(characters_in_scene)} characters: {', '.join(characters_in_scene)}.
            - Each appears only once — no duplicates or extra people.
            - Sharp focus on faces, no blur or distortion.

            CHARACTER INSTRUCTIONS:
            {char_instructions}

            STRICT PROHIBITIONS:
            - No other backgrounds or scenery beyond the provided background image.
            - No crowds, unknown people, or hidden figures.
            - No character duplication.
            - No changes to character appearance apart from pose.
            """

            # Generate image
            scene_image_url, scene_file_path = _generate_image_internal(
                scene_full_prompt,
                f"scene-{scene_idx+1}",
                reference_images=reference_images,
                request_id=request_id
            )
            api_calls += 1

            processed_scene = {
                "sceneIndex": scene_idx + 1,
                "isStoryScene": True,
                "charactersInvolved": characters_in_scene,
                "backgroundSetting": background_prompt,
                "backgroundImageUrl": background_images.get(background_prompt, {}).get("image_url", ""),
                "sceneDescriptionForI2i": scene_i2i_prompt,
                "sceneImageUrl": scene_image_url,
                "narration": scene.get("narration", ""),
                "characterDialogues": scene.get("characterDialogues", ""),
                "soundsDescription": scene.get("soundsDescription", ""),
                "sceneWiseDescriptionForI2v": scene.get("sceneWiseDescriptionForI2v", ""),
                "generationStatus": "success" if scene_image_url else "failed"
            }

            
        else:
            # Enhanced explainer scene processing with character clarity
            characters_involved = scene.get("charactersInvolved", [])
            required_visualization = scene.get("requiredVisualization", "")
            
            logger.info(f"[{request_id}] Explainer scene with visualization: {required_visualization[:50]}...")
            
            # Prepare character references for explainer scenes
            reference_images = []
            for char_name in characters_involved:
                if char_name in character_file_paths and character_file_paths[char_name]:
                    reference_images.append(character_file_paths[char_name])
            
            # ROBUST EDUCATIONAL VISUALIZATION PROMPT with character control
            viz_prompt = (
                f"EDUCATIONAL STORYTELLING ILLUSTRATION in {style_description} art style.\n"
                f"LEARNING CONTENT: {required_visualization}\n\n"
                
                f"CHARACTER COUNT CONTROL: This scene contains EXACTLY {len(characters_involved)} characters: {', '.join(characters_involved)}.\n"
                f"STRICT REQUIREMENT: Show each character ONLY ONCE. NO duplicates, NO multiple copies.\n"
                f"DO NOT add any other people, figures, or characters beyond those specified.\n\n"
                
                f"VISUALIZATION DESIGN:\n"
                f"- Create engaging, informative educational content with clear visual demonstrations.\n"
                f"- Use infographics, diagrams, or interactive visual elements as appropriate.\n"
                f"- Maintain story context while delivering educational value.\n"
                f"- Professional quality educational illustration with clear information hierarchy.\n\n"
            )
            
            # Character consistency for explainer scenes with facial clarity
            for char_name in characters_involved:
                if char_name in character_descriptions:
                    viz_prompt += (
                        f"CHARACTER {char_name} CONSISTENCY:\n"
                        f"- Use provided character reference for PERFECT visual consistency.\n"
                        f"- FACIAL CLARITY: Crystal clear, sharp focus, NO distortions or deformations.\n"
                        f"- Maintain exact appearance: {character_descriptions[char_name][:150]}...\n"
                        f"- Show character as educator, guide, or learner with clear, recognizable features.\n"
                        f"- Face must be clearly visible, well-lit, and perfectly detailed.\n\n"
                    )
            
            viz_prompt += (
                f"QUALITY REQUIREMENTS:\n"
                f"- High-resolution educational illustration with seamless artistic style integration.\n"
                f"- Perfect character facial clarity and consistency throughout.\n"
                f"- Professional educational design with engaging visual storytelling.\n"
                f"- Each specified character appearing exactly once with perfect clarity.\n\n"
                
                f"STRICT PROHIBITIONS:\n"
                f"- NO blurry faces, facial distortions, or unclear character features.\n"
                f"- NO inconsistent character appearances or poor lighting on faces.\n"
                f"- NO additional characters, people, or figures beyond those specified: {', '.join(characters_involved)}.\n"
                f"- NO duplicate characters or multiple copies of the same character.\n"
                f"- NO unknown people, strangers, or background figures.\n"
                f"- TOTAL CHARACTERS IN FINAL IMAGE: Exactly {len(characters_involved)} characters, no more, no less."
            )
            
            viz_image_url, viz_file_path = _generate_image_internal(
                viz_prompt, 
                f"explainer-{scene_idx + 1}",
                reference_images=reference_images if reference_images else None,
                request_id=request_id
            )
            api_calls += 1
            
            processed_scene = {
                "sceneIndex": scene_idx + 1,
                "isStoryScene": False,
                "charactersInvolved": characters_involved,
                "requiredVisualization": required_visualization,
                "visualizationImageUrl": viz_image_url,
                "generationStatus": "success" if viz_image_url else "failed"
            }
        
        processed_scenes.append(processed_scene)
        logger.info(f"[{request_id}] Completed scene {scene_idx + 1} processing")
    
    return processed_scenes, api_calls


@app.route("/generate_story_with_images", methods=["POST"])
def generate_story_with_images():
    start_time = time.time()
    request_id = generate_request_id()
    total_api_calls = 0
    total_retries = 0
    
    logger.info(f"[{request_id}] Starting enhanced comprehensive story generation request")
    
    try:
        data = request.get_json()
        logger.info(f"[{request_id}] Received request data: {json.dumps(data, indent=2)}")
        
        # Parse input with enhanced validation
        inputs = data.get("inputs", {})
        topics = inputs.get("topics", [])
        general_description = inputs.get("generalDescription", "")
        style_description = inputs.get("styleDescription", "Watercolor rural Indian illustration")
        
        # Backward compatibility
        if not topics and not general_description:
            topic = data.get("topic", "")
            description = data.get("description", "")
            style = data.get("style", "Watercolor rural Indian illustration")
            
            if topic:
                topics = [topic]
            if description:
                general_description = description
            if style:
                style_description = style

        # Enhanced input validation
        if not topics or not general_description:
            error_msg = "Missing required fields: 'topics' and 'generalDescription' are required"
            logger.error(f"[{request_id}] {error_msg}")
            return jsonify({"error": error_msg}), 400

        if not isinstance(topics, list):
            topics = [str(topics)]

        logger.info(f"[{request_id}] Processing topics: {topics}")
        logger.info(f"[{request_id}] Style: {style_description}")

        # Generate comprehensive story with enhanced prompting
        story_data = _generate_comprehensive_story(topics, general_description, style_description, request_id)
        total_api_calls += 1
        
        if "error" in story_data:
            logger.error(f"[{request_id}] Story generation failed: {story_data['error']}")
            return jsonify({"error": story_data["error"]}), 500

        # Extract story components
        story_plot = story_data.get("storyPlot", "")
        character_list = story_data.get("characterList", [])
        character_descriptions = story_data.get("characterDescriptionForT2i", {})
        scene_descriptions = story_data.get("sceneWiseDescription", [])

        logger.info(f"[{request_id}] Comprehensive story generated successfully:")
        logger.info(f"[{request_id}] - Plot length: {len(story_plot)} characters")
        logger.info(f"[{request_id}] - Characters: {len(character_list)}")
        logger.info(f"[{request_id}] - Total scenes: {len(scene_descriptions)}")

        # Process character images with enhanced quality
        character_images, character_file_paths, char_api_calls = process_character_images(
            character_list, character_descriptions, style_description, request_id
        )
        total_api_calls += char_api_calls

        # Process background images with enhanced quality
        background_images, background_file_paths, bg_api_calls = process_background_images(
            scene_descriptions, style_description, request_id
        )
        total_api_calls += bg_api_calls

        # Process scene images with maximum consistency
        processed_scenes, scene_api_calls = process_scene_images(
            scene_descriptions, character_descriptions, character_file_paths,
            background_file_paths, background_images, style_description, request_id
        )
        total_api_calls += scene_api_calls

        # Calculate comprehensive metadata
        generation_duration = time.time() - start_time
        story_scenes = sum(1 for scene in processed_scenes if scene.get("isStoryScene", True))
        explainer_scenes = len(processed_scenes) - story_scenes
        
        metadata = StoryMetadata(
            request_id=request_id,
            generation_timestamp=datetime.now().isoformat(),
            total_characters=len(character_images),
            total_background_images=len(background_images),
            total_scene_images=story_scenes,
            total_visualization_images=explainer_scenes,
            story_scenes=story_scenes,
            explainer_scenes=explainer_scenes,
            generation_duration=round(generation_duration, 2),
            api_calls_made=total_api_calls,
            retry_attempts=total_retries
        )

        # Build comprehensive final response
        final_response = {
            "requestId": request_id,
            "inputs": {
                "topics": topics,
                "generalDescription": general_description,
                "styleDescription": style_description
            },
            "output": {
                "storyPlot": story_plot,
                "characterList": character_list,
                "characterDescriptionForT2i": character_descriptions,
                "sceneWiseDescription": processed_scenes,
                "generatedImages": {
                    "characterImages": character_images,
                    "backgroundImages": background_images,
                    "sceneImages": [scene for scene in processed_scenes if scene.get("isStoryScene", True)],
                    "visualizationImages": [scene for scene in processed_scenes if not scene.get("isStoryScene", True)]
                }
            },
            "metadata": {
                "requestId": metadata.request_id,
                "generationTimestamp": metadata.generation_timestamp,
                "totalCharacters": metadata.total_characters,
                "totalBackgroundImages": metadata.total_background_images,
                "totalSceneImages": metadata.total_scene_images,
                "totalVisualizationImages": metadata.total_visualization_images,
                "storyScenes": metadata.story_scenes,
                "explainerScenes": metadata.explainer_scenes,
                "generationDuration": metadata.generation_duration,
                "apiCallsMade": metadata.api_calls_made,
                "retryAttempts": metadata.retry_attempts,
                "successMetrics": {
                    "charactersGenerated": len([img for img in character_images.values() if img.get("image_url")]),
                    "backgroundsGenerated": len([img for img in background_images.values() if img.get("image_url")]),
                    "scenesGenerated": len([scene for scene in processed_scenes if scene.get("sceneImageUrl") or scene.get("visualizationImageUrl")]),
                    "successRate": round(len([scene for scene in processed_scenes if scene.get("generationStatus") == "success"]) / len(processed_scenes) * 100, 2) if processed_scenes else 0
                }
            },
            "message": f"Comprehensive epic story generated successfully! Created {len(character_list)} rich characters, {len(background_images)} detailed backgrounds, and {len(processed_scenes)} cinematic scenes in {generation_duration:.2f} seconds."
        }

        # Log comprehensive success metrics
        logger.info(f"[{request_id}] Epic story generation completed successfully!")
        logger.info(f"[{request_id}] Final comprehensive metrics:")
        logger.info(f"[{request_id}] - Total characters: {metadata.total_characters}")
        logger.info(f"[{request_id}] - Total backgrounds: {metadata.total_background_images}")
        logger.info(f"[{request_id}] - Total scenes: {len(processed_scenes)}")
        logger.info(f"[{request_id}] - Story scenes: {story_scenes}")
        logger.info(f"[{request_id}] - Educational scenes: {explainer_scenes}")
        logger.info(f"[{request_id}] - API calls made: {metadata.api_calls_made}")
        logger.info(f"[{request_id}] - Generation time: {metadata.generation_duration}s")
        logger.info(f"[{request_id}] - Success rate: {final_response['metadata']['successMetrics']['successRate']}%")

        return jsonify(final_response)

    except ValidationError as e:
        logger.error(f"[{request_id}] Validation error: {e}")
        return jsonify({
            "error": "Input validation failed",
            "details": str(e),
            "requestId": request_id
        }), 400

    except Exception as e:
        generation_duration = time.time() - start_time
        logger.error(f"[{request_id}] Unexpected error after {generation_duration:.2f}s: {str(e)}")
        logger.error(f"[{request_id}] Full traceback: {traceback.format_exc()}")
        
        return jsonify({
            "error": "Internal server error during comprehensive story generation",
            "details": str(e),
            "requestId": request_id,
            "metadata": {
                "generationDuration": round(generation_duration, 2),
                "apiCallsMade": total_api_calls,
                "failurePoint": "Unknown"
            }
        }), 500

@app.route("/health", methods=["GET"])
def health_check():
    """Enhanced health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "3.0.0",
        "features": [
            "Comprehensive epic story generation",
            "Enhanced character development prompting",
            "Extended scene coverage optimization",
            "Advanced visual consistency system",
            "Professional quality image generation",
            "Robust error handling with retries",
            "Detailed logging and monitoring",
            "Cinematic storytelling focus"
        ]
    })

@app.route("/status/<request_id>", methods=["GET"])
def get_generation_status(request_id):
    """Get status of a generation request"""
    return jsonify({
        "requestId": request_id,
        "message": "Status tracking not yet implemented",
        "note": "Check logs for detailed generation progress and metrics"
    })

@app.route('/static/generated_images/<path:filename>')
def serve_static_images(filename):
    """Serve generated images with enhanced error handling"""
    try:
        return send_from_directory(os.path.join('static', 'generated_images'), filename)
    except FileNotFoundError:
        logger.error(f"Image file not found: {filename}")
        return jsonify({"error": "Image not found"}), 404
    except Exception as e:
        logger.error(f"Error serving image {filename}: {e}")
        return jsonify({"error": "Error serving image"}), 500

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

@app.before_request
def log_request_info():
    """Log incoming requests with enhanced details"""
    if request.path.startswith('/static/'):
        return  # Skip logging for static files
    
    logger.info(f"Request: {request.method} {request.path}")
    if request.is_json and request.method == 'POST':
        data = request.get_json()
        logger.info(f"Request size: {len(json.dumps(data))} characters")
        if 'inputs' in data:
            inputs = data['inputs']
            logger.info(f"Topics: {inputs.get('topics', 'N/A')}")
            logger.info(f"Description length: {len(inputs.get('generalDescription', ''))} characters")

if __name__ == "__main__":
    # Ensure directories exist
    os.makedirs('static/generated_images', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    logger.info("Starting Enhanced Comprehensive Story Generation Agent v3.0.0")
    logger.info(f"Enhanced Configuration:")
    logger.info(f"- Focus: Epic, feature-length narratives with rich character development")
    logger.info(f"- Target: Large diverse cast with extensive scene coverage")
    logger.info(f"- Quality: Professional cinematic visual storytelling")
    logger.info(f"- Consistency: Maximum character and background visual consistency")
    logger.info(f"- Max retries: {MAX_RETRIES}")
    logger.info(f"- Base delay: {BASE_DELAY}s")
    
    app.run(debug=True, port=5000, host='0.0.0.0')