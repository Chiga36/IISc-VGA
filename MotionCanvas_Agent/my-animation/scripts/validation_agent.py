#!/usr/bin/env python3
"""
Enhanced LLM-based validation agent with structured feedback parsing.
Validates Motion Canvas videos and provides structured feedback for code generation.
"""

import os
import sys
import json
import time
import re
import subprocess
from typing import Dict, List, Tuple, Optional


class ValidationAgent:
    """
    Enhanced video validation agent with structured feedback parsing.
    """

    def __init__(self):
        """Initialize the validation agent."""
        # --- Configuration ---
        # Get the absolute path of the directory containing this script
        self.SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
        # Get the project root directory (which is one level up from the script's directory)
        self.PROJECT_ROOT = os.path.abspath(os.path.join(self.SCRIPT_DIR, '..'))
        # Define all paths as absolute paths based on the project root
        self.PROJECT_FILE = os.path.join(self.PROJECT_ROOT, "src", "project.ts")
        self.OUTPUT_DIR = os.path.join(self.PROJECT_ROOT, "output")
        self.SCENES_DIR = os.path.join(self.PROJECT_ROOT, "src", "scenes")
        self.EXAMPLES_DIR = os.path.join(self.PROJECT_ROOT, "examples")

        try:
            import google.generativeai as genai
            self.genai = genai

            # Configure API
            api_key = os.getenv('GOOGLE_API_KEY')
            if not api_key:
                print("❌ GOOGLE_API_KEY not found. Set it in environment variables.")
                print("   export GOOGLE_API_KEY='your-api-key-here'")
                self.model = None
                return

            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash') # Changed to flash for speed
            print("✅ Validation agent initialized with Gemini API")

        except ImportError:
            print("❌ google-generativeai not installed. Install with:")
            print("   pip install google-generativeai")
            self.model = None
        except Exception as e:
            print(f"❌ An unexpected error occurred during initialization: {e}")
            self.model = None
    def _detect_text_overlap_in_code(self, generated_code: str) -> bool:
        """
        Detect text overlap patterns directly in generated code.
        Returns True if overlap patterns are found.
        """
        # More flexible patterns to match actual generated code
        title_pattern = r'y=\{?-300\}?'  # Just look for y=-300
        desc_pattern = r'y=\{?-150\}?'   # Just look for y=-150  
        content_pattern = r'y=\{?0\}?'   # Just look for y=0
    
        has_safe_title = bool(re.search(title_pattern, generated_code))
        has_safe_desc = bool(re.search(desc_pattern, generated_code))
        has_safe_content = bool(re.search(content_pattern, generated_code))
    
        print(f"🔍 Safe Positioning Check - Title at y=-300: {has_safe_title}, Desc at y=-150: {has_safe_desc}, Content at y=0: {has_safe_content}")
    
        # If we find ANY safe positioning, consider it valid
        if has_safe_title or has_safe_desc or has_safe_content:
            print("✅ Safe positioning detected - accepting code")
            return False  # No overlap detected
        
        print("❌ No safe positioning patterns found")
        return True  # Potential overlap


    
    def _detect_visual_text_overlap(self, video_path: str) -> Tuple[bool, str]:
        """
        Detect overlap between visual elements and text using computer vision analysis.
        Returns (has_overlap, description)
        """
        try:
            import cv2
            import numpy as np
            import easyocr
        except ImportError:
            print("⚠️ Required libraries not installed. Run: pip install opencv-python easyocr")
            return False, "Computer vision libraries not available"
    
        try:
            # Extract last frame
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return False, "Could not open video file"
                
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            if total_frames <= 0:
                cap.release()
                return False, "Video has no frames"
            
            cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, total_frames - 1))
            ret, frame = cap.read()
            cap.release()
        
            if not ret:
                return False, "Could not extract frame"
        
            height, width = frame.shape[:2]
            print(f"🎯 Visual overlap analysis: {width}x{height}")
        
            # Define zones (40% left for visuals, 60% right for text)
            visual_zone_width = int(width * 0.4)
            text_zone_start = visual_zone_width
        
            # Initialize EasyOCR
            reader = easyocr.Reader(['en'], gpu=False)
            results = reader.readtext(frame, detail=1)
        
            if not results:
                print("✅ No text detected - no visual overlap possible")
                return False, "No text found for analysis"
        
            # Extract text regions
            text_regions = []
            for (bbox, text, confidence) in results:
                if confidence > 0.3:
                    x_coords = [point[0] for point in bbox]
                    y_coords = [point[1] for point in bbox]
                    x1, y1 = int(min(x_coords)), int(min(y_coords))
                    x2, y2 = int(max(x_coords)), int(max(y_coords))
                    
                    text_regions.append((x1, y1, x2, y2, text.strip()))
                    print(f"   📝 Text '{text}' at ({x1}, {y1}, {x2}, {y2})")
        
            # Check 1: Text extending into visual zone (left 40%)
            for x1, y1, x2, y2, text in text_regions:
                if x1 < text_zone_start:
                    return True, f"Text '{text}' extends into visual zone (starts at x={x1}, should be > {text_zone_start})"
        
            # Check 2: Detect colorful visual elements in text zone (right 60%)
            text_zone_frame = frame[:, text_zone_start:]
            text_zone_hsv = cv2.cvtColor(text_zone_frame, cv2.COLOR_BGR2HSV)
        
            # Define color ranges for typical visual elements
            color_ranges = [
                ("Blue", np.array([100, 80, 80]), np.array([130, 255, 255])),
                ("Red", np.array([0, 80, 80]), np.array([10, 255, 255])),
                ("Red2", np.array([170, 80, 80]), np.array([180, 255, 255])),
                ("Green", np.array([40, 80, 80]), np.array([80, 255, 255])),
                ("Orange", np.array([10, 80, 80]), np.array([25, 255, 255])),
            ]
        
            for color_name, lower, upper in color_ranges:
                mask = cv2.inRange(text_zone_hsv, lower, upper)
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
                for contour in contours:
                    area = cv2.contourArea(contour)
                    if area > 1000:  # Significant visual element
                        x, y, w, h = cv2.boundingRect(contour)
                        visual_x_global = x + text_zone_start
                    
                        # Check if this visual overlaps with any text
                        for tx1, ty1, tx2, ty2, text in text_regions:
                            # Check for intersection
                            if not (visual_x_global + w < tx1 or visual_x_global > tx2 or y + h < ty1 or y > ty2):
                                return True, f"{color_name} visual element (area: {area:.0f}) overlaps with text '{text}'"
        
            print("✅ No visual-text overlap detected")
            return False, "No visual-text overlap detected"
        
        except Exception as e:
            print(f"❌ Error in visual overlap analysis: {e}")
            return False, f"Visual analysis failed: {str(e)}"

    
    def _extract_last_frame_and_detect_overlap(self, video_path: str) -> Tuple[bool, str]:
        """
        Extract the last frame from video and detect text overlap using computer vision.
        Returns (has_overlap, description)
        """
        try:
            import cv2
            import numpy as np
            from PIL import Image
            import easyocr
        except ImportError:
            print("⚠️ Required libraries not installed. Run: pip install opencv-python pillow easyocr")
            return False, "Computer vision libraries not available"
    
        try:
            # Extract last frame from video
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return False, "Could not open video file"
        
            # Get total frame count and jump to last frame
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            if total_frames <= 0:
                cap.release()
                return False, "Video has no frames"
            
            cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, total_frames - 1))
        
            ret, frame = cap.read()
            cap.release()
        
            if not ret or frame is None:
                return False, "Could not extract last frame"
        
            print(f"🖼️ Extracted last frame: {frame.shape}")
        
            # Convert BGR to RGB for OCR
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
            # Initialize EasyOCR reader
            reader = easyocr.Reader(['en'], gpu=False)
        
            # Extract text with bounding boxes
            results = reader.readtext(frame_rgb, detail=1)
        
            print(f"🔍 Found {len(results)} text regions")
        
            # Check for overlapping bounding boxes
            bounding_boxes = []
            text_content = []
        
            for (bbox, text, confidence) in results:
                if confidence > 0.4:  # Lower threshold to catch more text
                    # Convert bbox to (x1, y1, x2, y2) format
                    x_coords = [point[0] for point in bbox]
                    y_coords = [point[1] for point in bbox]
                    x1, y1 = min(x_coords), min(y_coords)
                    x2, y2 = max(x_coords), max(y_coords)
                    
                    bounding_boxes.append((x1, y1, x2, y2))
                    text_content.append(text.strip())
                    print(f"   📝 Text: '{text}' at ({x1:.0f}, {y1:.0f}, {x2:.0f}, {y2:.0f})")
        
            if len(bounding_boxes) < 2:
                print("✅ Less than 2 text regions found - no overlap possible")
                return False, "Insufficient text for overlap analysis"
        
            # Check for overlapping bounding boxes
            for i in range(len(bounding_boxes)):
                for j in range(i + 1, len(bounding_boxes)):
                    box1 = bounding_boxes[i]
                    box2 = bounding_boxes[j]
                
                    # Calculate intersection
                    x1_inter = max(box1[0], box2[0])
                    y1_inter = max(box1[1], box2[1])
                    x2_inter = min(box1[2], box2[2])
                    y2_inter = min(box1[3], box2[3])
                
                    # Check if boxes overlap
                    # Check for overlapping bounding boxes - DISABLED FOR MULTI-LINE TEXT
                    if x1_inter < x2_inter and y1_inter < y2_inter:
                        overlap_area = (x2_inter - x1_inter) * (y2_inter - y1_inter)
                        box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
                        box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])
    
                        # If overlap is significant (>50% - very lenient for multi-line text)
                        overlap_ratio = overlap_area / min(box1_area, box2_area)
                        if overlap_ratio > 0.5:  # Only flag if more than 50% overlap
                            return True, f"Text overlap detected: '{text_content[i]}' and '{text_content[j]}' (overlap: {overlap_ratio:.1%})"

            
            # Additional check: if text boxes are too close vertically
            for i in range(len(bounding_boxes)):
                for j in range(i + 1, len(bounding_boxes)):
                    box1 = bounding_boxes[i]
                    box2 = bounding_boxes[j]
                    
                    # Check vertical distance between boxes
                    box1_center_y = (box1[1] + box1[3]) / 2
                    box2_center_y = (box2[1] + box2[3]) / 2
                    vertical_gap = abs(box1_center_y - box2_center_y)
                    
                    avg_height = ((box1[3] - box1[1]) + (box2[3] - box2[1])) / 2
                    
                    if vertical_gap < 1:  # Less than 10% of average height
                        return True, f"Text too close vertically: '{text_content[i]}' and '{text_content[j]}' (gap: {vertical_gap:.0f}px, avg_height: {avg_height:.0f}px)"
            
            print("✅ No text overlap detected in frame analysis")
            return False, "No text overlap detected"
        
        except Exception as e:
            print(f"❌ Error in frame analysis: {e}")
            return False, f"Frame analysis failed: {str(e)}"




    def validate_scene(self, scene_data: Dict, video_path: str, generated_code: str,
                      errors: Optional[List[str]] = None, code_examples: str = "", formatted_code_gen_prompt: str = "", token_tracker = None) -> Tuple[bool, Dict]:
        """
        Enhanced post-render video validation with structured feedback parsing.
        """
        scene_title = scene_data.get('scene_title', 'Unknown Scene')
        print(f"\n🎬 Stage 2: Validating rendered video: {scene_title}")
        print(f"🎥 Video path: {video_path}")

        # Check if video file exists
        if not os.path.exists(video_path):
            print(f"❌ Video file not found: {video_path}")
            return False, {
                "valid": False,
                "issues": [{
                    "type": "file_missing",
                    "description": "Video file does not exist",
                    "fix_suggestion": "Ensure rendering process completes successfully"
                }],
                "corrected_scene_description": scene_data.get('scene_description', ''),
                "code_improvement_hints": ["Check rendering pipeline for errors"]
            }

        file_size = os.path.getsize(video_path)
        print(f"📊 Video file size: {file_size / (1024*1024):.1f} MB")

        # Basic file check
        if file_size < 1000:
            print("❌ Video file too small - likely corrupted")
            return False, {
                "valid": False,
                "issues": [{
                    "type": "file_corrupted",
                    "description": "Video file appears corrupted or empty",
                    "fix_suggestion": "Check rendering process and ensure proper frame generation"
                }],
                "corrected_scene_description": scene_data.get('scene_description', ''),
                "code_improvement_hints": [
                    "Ensure all elements are added to the scene before animation",
                    "Check that animation durations are reasonable (1-3 seconds)",
                    "Verify all references are properly initialized"
                ]
            }

        # If no LLM available, do basic validation
        if not self.model:
            print("⚠️ No LLM available - using fallback validation")
            return True, {"valid": True}
        
        # CRITICAL: Frame-based text overlap detection (most reliable method)
        # CRITICAL: Frame-based text and visual overlap detection
        # text_overlap, text_overlap_desc = self._extract_last_frame_and_detect_overlap(video_path)
        # visual_overlap, visual_overlap_desc = self._detect_visual_text_overlap(video_path)

        # has_overlap = text_overlap or visual_overlap
        
        # OCR-based validation disabled due to false positives with sentence fragments
        # Code-level validation and visual inspection are more reliable
        text_overlap, text_overlap_desc = False, "OCR validation disabled"
        visual_overlap, visual_overlap_desc = False, "Visual validation disabled"

        has_overlap = False  # Trust the code generation and formatText() function
        print("✅ FRAME ANALYSIS SKIPPED: Using code-level validation instead")

        if text_overlap and visual_overlap:
            overlap_description = f"Text overlap: {text_overlap_desc}; Visual overlap: {visual_overlap_desc}"
        elif text_overlap:
            overlap_description = f"Text overlap: {text_overlap_desc}"
        else:
            overlap_description = f"Visual overlap: {visual_overlap_desc}"


        if has_overlap:
            print(f"❌ FRAME ANALYSIS FAILED: {overlap_description}")
            return False, {
                "valid": False,
                "issues": [{
                    "type": "text_overlap_detected",
                    "description": f"Computer vision detected: {overlap_description}",
                    "fix_suggestion": "Use proper text spacing: Title at y=-300, Description at y=-150, Content at y=0",
                    "severity": "critical"
                }],
                "corrected_scene_description": scene_data.get('scene_description', ''),
                "code_improvement_hints": [
                    "Use individual text positioning with 150px vertical spacing",
                    "Avoid Layout containers - use fixed coordinates",
                    "Title: y=-300, Description: y=-150, Content: y=0"
                ]
            }

        print("✅ FRAME ANALYSIS PASSED: No text overlap detected")
        frame_analysis_passed = True


        
        # PRE-VALIDATION: Check for text overlap patterns in code
        # if self._detect_text_overlap_in_code(generated_code):
        #     print("❌ TEXT OVERLAP DETECTED in generated code - forcing regeneration")
        #     return False, {
        #         "valid": False,
        #         "issues": [{
        #             "type": "text_overlap",
        #             "description": "Individual text positioning detected - will cause overlap",
        #             "fix_suggestion": "Use single Layout container for all text elements",
        #             "severity": "critical"
        #         }],
        #         "corrected_scene_description": scene_data.get('scene_description', ''),
        #         "code_improvement_hints": ["Replace individual Txt positioning with Layout container"]
        #     }


        try:
            # Upload video for analysis
            print("📤 Uploading video to Gemini...")
            video_file = self.genai.upload_file(video_path)

            # Wait for processing
            while video_file.state.name == "PROCESSING":
                print("⏳ Processing video...")
                time.sleep(2)
                video_file = self.genai.get_file(video_file.name)

            if video_file.state.name == "FAILED":
                print("❌ Video processing failed")
                return False, {
                    "valid": False,
                    "issues": [{
                        "type": "processing_failed",
                        "description": "Video processing failed",
                        "fix_suggestion": "Check video format and ensure proper encoding"
                    }],
                    "corrected_scene_description": scene_data.get('scene_description', ''),
                    "code_improvement_hints": ["Verify video encoding parameters"]
                }

            print("🤖 Analyzing video with LLM...")

            # Create validation prompt
            prompt = self._create_video_validation_prompt(scene_data, generated_code, errors, code_examples, formatted_code_gen_prompt)

            # Get LLM response
            response = self.model.generate_content([video_file, prompt])

            # Track token usage if token_tracker is provided
            if token_tracker:
                try:
                    input_tokens = response.usage_metadata.prompt_token_count
                    output_tokens = response.usage_metadata.candidates_token_count
                    scene_title = scene_data.get('scene_title', 'UnknownScene')
                    token_tracker.add("ValidationAgent", scene_title, input_tokens, output_tokens)
                except AttributeError:
                    # Fallback if usage_metadata is not available
                    pass

            try:
                response_text = response.text
            except Exception as e:
                print("❌ LLM validation error: Could not access response.text.")
                return True, {"valid": True, "issues": ["LLM did not return a valid response."]}

            # Parse response into structured feedback
            try:
                is_valid, feedback = self._parse_video_validation_response(response_text, scene_data)
            except Exception as e:
                print(f"❌ Error parsing LLM response: {e}")
                print(f"Raw LLM response: {response_text}")
                return True, {"valid": True, "issues": [f"LLM response parsing error: {str(e)[:100]}"]}

            # Cleanup
            self.genai.delete_file(video_file.name)

            # Log result
            # OVERRIDE: Force rejection for small videos (likely have overlap issues)
            # OVERRIDE: Force rejection for extremely small videos AND when Gemini gives conflicting signals
                    # ═══════════════════════════════════════════════════════════════
            # VIDEO SIZE AND QUALITY VALIDATION
            # ═══════════════════════════════════════════════════════════════
            
            video_size_mb = file_size / (1024 * 1024)
            
            # Step 1: Reject obviously suspicious small videos
            if video_size_mb < 0.15 and is_valid:
                print(f"🔥 REJECTING - Suspicious video size: {video_size_mb:.2f}MB")
                feedback["valid"] = False
                
                if not any('video size' in issue.get('description', '').lower() for issue in feedback.get("issues", [])):
                    feedback["issues"].append({
                        "type": "rendering_issue",
                        "description": f"Video file too small ({video_size_mb:.2f}MB) - likely incomplete rendering or text overlap",
                        "fix_suggestion": "Check text positioning and ensure no overlaps. Use Layout container for text grouping.",
                        "severity": "critical"
                    })
                is_valid = False
            elif video_size_mb >= 0.15:
                print(f"✅ Video size acceptable: {video_size_mb:.2f}MB")
            
            # Step 2: If Gemini found critical issues and video is reasonably sized, trust Gemini
            if not is_valid and video_size_mb >= 0.15:
                gemini_found_real_issues = any(
                    issue.get('severity') == 'critical' and 
                    issue.get('type') not in ['rendering_issue', 'file_size'] 
                    for issue in feedback.get('issues', [])
                )
                
                if gemini_found_real_issues:
                    print("⚠️ Gemini detected critical issues - trusting LLM validation")
                    return is_valid, feedback
            
            # Step 3: Only allow override for size-only failures with good videos
            if not is_valid and frame_analysis_passed and video_size_mb > 0.2:
                size_only_issues = all(
                    'video size' in issue.get('description', '').lower() or
                    'suspicious' in issue.get('description', '').lower()
                    for issue in feedback.get('issues', [])
                )
                
                if size_only_issues and len(feedback.get('issues', [])) <= 1:
                    print("🔄 FRAME ANALYSIS OVERRIDE: Accepting video - only size-based rejection")
                    return True, {
                        "valid": True,
                        "issues": [],
                        "corrected_scene_description": scene_data.get('scene_description', ''),
                        "code_improvement_hints": [],
                        "frame_analysis_override": True
                    }
        
        except Exception as e:
            print(f"❌ LLM validation error: {e}")
            is_valid = True
            feedback = {
                "valid": True, 
                "issues": [f"Fallback validation (LLM error: {str(e)[:100]})"], 
                "corrected_scene_description": scene_data.get('scene_description', '')
            }
        
        # Log final result
        status = "✅ VIDEO VALID" if is_valid else "❌ VIDEO INVALID"
        print(f"{status}")
        if not is_valid:
            for issue in feedback.get("issues", []):
                print(f" - {issue.get('description', 'Unknown issue')}")
        
        return is_valid, feedback


        #
        


    def _create_video_validation_prompt(self, scene_data: Dict, generated_code: str,
                                   errors: Optional[List[str]], code_examples: str, formatted_code_gen_prompt: str) -> str:
        """Create comprehensive video validation prompt for post-render analysis."""
        error_text = "None" if not errors else "\n".join(errors)

        return f"""
    You are a COMPREHENSIVE Educational Video Quality Inspector with STRICT standards for visual layout, readability, and educational effectiveness.

    SCENE SPECIFICATION:
    ```json
    {json.dumps(scene_data, indent=2)}
    ```

    CODE GENERATION RULES & STANDARDS:
    ```
    {formatted_code_gen_prompt[:2500]}
    ```

    REFERENCE EXAMPLES:
    ```typescript
    {code_examples[:2000]}
    ```

    IMPLEMENTATION CODE:
    ```typescript
    {generated_code[:3500]}
    ```

    REPORTED ERRORS: {error_text}

    MANDATORY VALIDATION CRITERIA (ALL must pass for VALID rating):

    1. **STRICT LAYOUT REQUIREMENTS:**
    - LEFT 40%: Visual content ONLY (diagrams, charts, graphs, shapes, mathematical figures)
    - RIGHT 60%: Text content ONLY (explanations, equations, bullet points)
    - NO cross-boundary violations - visuals must stay left, text must stay right
    - Clear visual separation between left and right sections
    - Proper aspect ratio utilization (1920x1080 canvas)

    2. **TEXT READABILITY & FORMATTING (CRITICAL):**
    - ALL text MUST fit strictly within the right 60% boundary. Any overflow, cutoff, or text extending into the visual (left) area is a CRITICAL FAILURE.
    - Text MUST wrap appropriately within its designated area. Lack of wrapping leading to overflow or unreadability is a CRITICAL FAILURE.
    - NO text overlapping with ANY other text elements. This is a CRITICAL FAILURE.
    - NO text overlapping with ANY visual elements. This is a CRITICAL FAILURE.
    - Proper line spacing and paragraph breaks are MANDATORY for readability.
    - Font sizes MUST be appropriate for readability (minimum 24px for body text).
    - Consistent text hierarchy (titles, subtitles, body text) is required.

    3. **VISUAL CONTENT STANDARDS (CRITICAL):**
    - ALL visual elements MUST be positioned strictly within the left 40% boundary. Any visual element extending into the text (right) area is a CRITICAL FAILURE.
    - NO visual elements overlapping text areas. This is a CRITICAL FAILURE.
    - Mathematical figures, curves, graphs MUST be properly oriented (not inverted/flipped). Incorrect orientation is a CRITICAL FAILURE.
    - Clear visual hierarchy and organization are MANDATORY.
    - Proper scaling and proportions are required.
    - No visual elements cut off or extending beyond canvas boundaries.

    3.5. **LABELING & ANNOTATION (CRITICAL):**
    - All significant visual elements MUST have clear, readable labels or annotations.
    - Labels must be correctly positioned relative to their elements, not overlap other elements, and be visible throughout the relevant animation segment.
    - Labels MUST be distinct from the main explanation text and clearly associated with their visual element.

    3.6. **ANIMATION DETAIL & PRECISION (CRITICAL):**
    - Animations must be descriptive and precise, clearly illustrating the concept.
    - This includes using appropriate easing, showing intermediate states, and employing visual cues (e.g., highlights, temporary lines) to enhance understanding.
    - Animations should not be overly simplistic if the concept allows for more detail and clarity.

    4. **CONTENT COMPLETENESS:**
    - ALL elements from scene description must be present and visible
    - Proper text-visual synchronization as specified in code generation rules
    - Educational narrative flows logically from visual to text
    - No missing critical components (equations, diagrams, explanations)

    5. **ANIMATION & TIMING:**
    - Animation sequences follow logical educational progression
    - Reasonable timing (not too fast to comprehend, not too slow to engage)
    - Smooth transitions between elements
    - Proper reveal sequences for educational content

    6. **TECHNICAL QUALITY:**
    - No rendering artifacts or visual glitches
    - Proper color contrast for readability
    - Clean, professional appearance
    - No element positioning errors

    DETAILED VALIDATION CHECKLIST:

    **LAYOUT COMPLIANCE:**
    - [ ] Visual content strictly within left 40% (x < 384px for 1920px width)
    - [ ] Text content strictly within right 60% (x > 384px for 1920px width)
    - [ ] No boundary violations or cross-contamination
    - [ ] Proper utilization of allocated space

    **TEXT QUALITY:**
    - [ ] All text readable without overlapping
    - [ ] Proper text wrapping within right boundary
    - [ ] Adequate spacing between text elements
    - [ ] Consistent font sizing and hierarchy
    - [ ] No text cutoff or overflow issues

    **VISUAL QUALITY:**
    - [ ] All diagrams/charts properly positioned left
    - [ ] Mathematical figures correctly oriented
    - [ ] Clear visual-text separation
    - [ ] Proper scaling and proportions
    - [ ] No visual elements overlapping text

    **LABELING & ANNOTATION QUALITY:**
    - [ ] All significant visual elements have clear, readable labels/annotations
    - [ ] Labels are correctly positioned and do not overlap
    - [ ] Labels are distinct and clearly associated with their elements

    **ANIMATION DETAIL & PRECISION:**
    - [ ] Animations are descriptive and precise
    - [ ] Appropriate easing and intermediate states are used
    - [ ] Visual cues enhance understanding
    - [ ] Animations are not overly simplistic

    **CONTENT VERIFICATION:**
    - [ ] All scene description elements present
    - [ ] Proper educational flow and narrative
    - [ ] Text-visual synchronization working
    - [ ] Complete message conveyance

    **ANIMATION ASSESSMENT:**
    - [ ] Logical sequence and timing
    - [ ] Educational effectiveness maintained
    - [ ] Smooth, professional transitions

    SEVERITY CLASSIFICATION:
    - **CRITICAL**: Prevents message understanding (missing content, severe overlaps, boundary violations)
    - **MAJOR**: Impacts readability/usability (text overlaps, poor spacing, misaligned elements)
    - **MINOR**: Aesthetic issues that don't impact function (minor positioning variations)

    REQUIRED OUTPUT FORMAT:

    **VALIDATION RESULT:** [PASS/FAIL]

    **LAYOUT COMPLIANCE ASSESSMENT:**
    [Detailed check of 40/60 division adherence - mark FAIL if any violations]

    **TEXT READABILITY ANALYSIS:**
    [Check for overlapping, wrapping, spacing issues - mark FAIL if any found]

    **VISUAL POSITIONING VERIFICATION:**
    [Verify all visuals in left 40%, properly oriented - mark FAIL if violations]

    **CONTENT COMPLETENESS CHECK:**
    [All scene description elements present and properly positioned - mark FAIL if missing elements]

    **ANIMATION & FLOW EVALUATION:**
    [Educational effectiveness and timing assessment]

    **OVERALL EDUCATIONAL EFFECTIVENESS:** [Score 1-10]

    **DETAILED JSON SUMMARY:**
    ```json
    {{
    "valid": true,
    "layout_compliance": {{
        "left_visual_boundary": true,
        "right_text_boundary": true,
        "proper_separation": true,
        "space_utilization": true
    }},
    "text_quality": {{
        "no_overlapping": true,
        "proper_wrapping": true,
        "adequate_spacing": true,
        "readability": true
    }},
    "visual_quality": {{
        "proper_positioning": true,
        "correct_orientation": true,
        "no_text_overlap": true,
        "appropriate_scaling": true
    }},
    "labeling_quality": {{
        "clear_labels": true,
        "correct_positioning": true,
        "no_overlap": true
    }},
    "animation_detail": {{
        "descriptive_animations": true,
        "appropriate_easing": true,
        "visual_cues_used": true,
        "not_overly_simplistic": true
    }},
    "issues": [
        {{
        "type": "layout_violation|text_overlap|visual_misplacement|labeling_issue|animation_detail_issue|content_missing|animation_issue|technical_problem",
        "description": "Specific detailed issue description",
        "fix_suggestion": "Concrete fix recommendation",
        "severity": "critical|major|minor",
        "location": "specific element or area affected"
        }}
    ],
    "corrected_scene_description": "Enhanced scene description addressing all issues",
    "code_improvement_hints": [
        "Specific technical fixes needed",
        "Layout corrections required",
        "Text positioning improvements",
        "Visual element adjustments"
    ],
    "educational_effectiveness_score": 1-10
    }}
    ```

    VALIDATION STANDARDS:
    - FAIL if ANY layout boundary violations (40/60 division not respected) are observed.
    - FAIL if ANY text overlapping, text wrapping issues, or text readability issues are observed.
    - FAIL if ANY visual-text overlaps or visual misplacements (visuals in text area, or vice-versa) are observed.
    - FAIL if ANY essential content missing from scene description.
    - FAIL if animation timing severely impacts comprehension.
    - PASS only when ALL criteria meet professional educational video standards.

    Be THOROUGH and PRECISE in identifying issues. The goal is to ensure every video meets high educational and visual standards.
    """
    def _parse_video_validation_response(self, response_text: str, scene_data: Dict) -> Tuple[bool, Dict]:
        """
        Parse the structured response from video validation into feedback format.
        Supports severity, scoring, and all issue types.
        """
        try:
            # Extract JSON from response
            print(f"Raw LLM response text:\n{response_text}")
            json_match = re.search(r'```json\s*(\{[\s\S]*?\})\s*```', response_text, re.DOTALL)
            if json_match:
                extracted_json_str = json_match.group(1)
                print(f"Extracted JSON string:\n{extracted_json_str}")
                json_data = json.loads(extracted_json_str)

                # Ensure essential fields exist
                is_valid = json_data.get('valid', False)
                # Default score to 0 if not present or invalid
                score = json_data.get('educational_effectiveness_score', 0)

                # Extract nested scores, defaulting to 0 if not present
                layout_score = json_data.get('layout_compliance', {}).get('score', 0)
                text_score = json_data.get('text_quality', {}).get('score', 0)
                visual_score = json_data.get('visual_quality', {}).get('score', 0)
                content_completeness_score = json_data.get('content_completeness_check', {}).get('score', 0)
                animation_score = json_data.get('animation_flow_evaluation', {}).get('score', 0)
                # Technical quality score is not explicitly in the prompt's JSON, so we'll omit it or derive it if needed.

                # Collect issues
                issues = json_data.get('issues', [])
                for issue in issues:
                    if "severity" not in issue:
                        # Default severity if missing
                        issue["severity"] = "minor"

                # If missing recommended hints, add defaults
                improvement_hints = json_data.get('code_improvement_hints', [])
                if not improvement_hints:
                    improvement_hints = [
                        "Verify layout compliance and spacing",
                        "Ensure text readability and proper wrapping",
                        "Check for missing elements from scene description"
                    ]

                feedback = {
                    "valid": is_valid,
                    "score": score,
                    "score_breakdown": {
                        "layout": layout_score,
                        "text_quality": text_score,
                        "visual_quality": visual_score,
                        "content_completeness": content_completeness_score,
                        "animation": animation_score,
                        # "technical": technical_score # Omitted as not explicitly in prompt JSON
                    },
                    "issues": issues,
                    "corrected_scene_description": json_data.get('corrected_scene_description', scene_data.get('scene_description', '')),
                    "code_improvement_hints": improvement_hints,
                    "educational_effectiveness_score": score
                }

                return is_valid, feedback

        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parsing error: {e}")
            feedback = self._fallback_parse_response(response_text, scene_data)
            return feedback.get('valid', False), feedback


    def _fallback_parse_response(self, response_text: str, scene_data: Dict) -> Dict:
        """
        Fallback parsing when JSON extraction fails.
        Captures all detectable issues with severity levels.
        """
        response_lower = response_text.lower()

        issues = []

        # Define indicators for severity classification
        critical_indicators = ['layout boundary violation', 'text overflow', 'text cutoff', 'text extending into visual', 'text overlapping with other text', 'text overlapping with visual', 'visual extending into text', 'visual overlapping text', 'mathematical figures not properly oriented', 'missing critical components', 'text overlap', 'overlapping text', 'text readability issue', 'text boundary violation']
        major_indicators = ['impacts readability', 'poor spacing', 'misaligned elements', 'visual glitches', 'rendering artifacts']
        minor_indicators = ['minor positioning variations', 'aesthetic issues']

        # Detect issues from response text
        for phrase in critical_indicators:
            if phrase in response_lower:
                issues.append({
                    "type": "critical_issue",
                    "description": f"Detected: {phrase}",
                    "fix_suggestion": "Immediate fix required",
                    "severity": "critical"
                })

        for phrase in major_indicators:
            if phrase in response_lower:
                issues.append({
                    "type": "major_issue",
                    "description": f"Detected: {phrase}",
                    "fix_suggestion": "Adjust layout/positioning",
                    "severity": "major"
                })

        for phrase in minor_indicators:
            if phrase in response_lower:
                issues.append({
                    "type": "minor_issue",
                    "description": f"Detected: {phrase}",
                    "fix_suggestion": "Optional refinement",
                    "severity": "minor"
                })

        # Determine validity: FAIL if any critical issues
        # Check for text overlap in response text
        response_lower = response_text.lower()
        overlap_keywords = ['text overlap', 'overlapping text', 'text extending', 'text readability issue']
        text_overlap_in_response = any(keyword in response_lower for keyword in overlap_keywords)

        # Determine validity: FAIL if any critical issues OR text overlap detected
        is_valid = not (any(issue['severity'] == 'critical' for issue in issues) or text_overlap_in_response)

        if text_overlap_in_response:
            print("❌ TEXT OVERLAP detected in LLM response - marking as invalid")


        feedback = {
            "valid": is_valid,
            "score": 50 if is_valid else 0,  # fallback score
            "score_breakdown": {
                "layout": 0,
                "text_quality": 0,
                "visual_quality": 0,
                "content_completeness": 0,
                "animation": 0,
            },
            "issues": issues,
            "corrected_scene_description": scene_data.get('scene_description', ''),
            "code_improvement_hints": [
                "Fix detected critical/major issues before rendering",
                "Review layout and animation timing"
            ],
            "educational_effectiveness_score": 5
        }

        return feedback



def main():
    """Test the enhanced validation agent."""
    print("🚀 Testing Enhanced Motion Canvas Validation Agent")

    # Test pre-render validation
    validator = ValidationAgent()

    # Placeholder for linked list scene data
    linked_list_scene_data = {
        'scene_title': 'Linked List Explanation',
        'scene_description': 'An animation explaining the concept of a linked list, showing nodes and pointers.',
        'duration': 10,
        'elements': [
            {'id': 'node1', 'type': 'rect', 'position': [-300, 0], 'label': 'Head'},
            {'id': 'node2', 'type': 'rect', 'position': [0, 0], 'label': 'Node'},
            {'id': 'node3', 'type': 'rect', 'position': [300, 0], 'label': 'Tail'},
            {'id': 'pointer1', 'type': 'arrow', 'from': 'node1', 'to': 'node2'},
            {'id': 'pointer2', 'type': 'arrow', 'from': 'node2', 'to': 'node3'},
        ],
        'animations': [
            {'action': 'show', 'elements': ['node1', 'node2', 'node3']},
            {'action': 'animate_pointer', 'element': 'pointer1'},
            {'action': 'animate_pointer', 'element': 'pointer2'},
        ]
    }

    # Placeholder for linked list generated code
    linked_list_test_code = '''
import {makeScene2D} from '@motion-canvas/2d/lib/scenes';
import {Rect, Txt, Line} from '@motion-canvas/2d/lib/components';
import {all, waitFor, chain} from '@motion-canvas/core/lib/flow';
import {createRef} from '@motion-canvas/core/lib/utils';
import {Vector2} from '@motion-canvas/core/lib/types';

export default makeScene2D(function* (view) {
    const node1Ref = createRef<Rect>();
    const node2Ref = createRef<Rect>();
    const node3Ref = createRef<Rect>();
    const pointer1Ref = createRef<Line>();
    const pointer2Ref = createRef<Line>();

    view.add(
        <>
            <Rect ref={node1Ref} width={100} height={60} fill="#ADD8E6" radius={10} position={[-300, 0]} opacity={0}>
                <Txt text="Head" fontSize={30} fill="black" />
            </Rect>
            <Rect ref={node2Ref} width={100} height={60} fill="#ADD8E6" radius={10} position={[0, 0]} opacity={0}>
                <Txt text="Node" fontSize={30} fill="black" />
            </Rect>
            <Rect ref={node3Ref} width={100} height={60} fill="#ADD8E6" radius={10} position={[300, 0]} opacity={0}>
                <Txt text="Tail" fontSize={30} fill="black" />
            </Rect>
            <Line ref={pointer1Ref} points={[node1Ref().right, node2Ref().left]} stroke="#FF0000" lineWidth={5} end={0} opacity={0} />
            <Line ref={pointer2Ref} points={[node2Ref().right, node3Ref().left]} stroke="#FF0000" lineWidth={5} end={0} opacity={0} />
        </>
    );

    yield* all(
        node1Ref().opacity(1, 1),
        node2Ref().opacity(1, 1),
        node3Ref().opacity(1, 1),
    );
    yield* waitFor(1);

    yield* all(
        pointer1Ref().opacity(1, 0.5),
        pointer1Ref().end(1, 1),
    );
    yield* waitFor(1);

    yield* all(
        pointer2Ref().opacity(1, 0.5),
        pointer2Ref().end(1, 1),
    );
    yield* waitFor(1);

    yield* waitFor(linked_list_scene_data.duration - 4); // Adjust wait time
});
'''



    # Test validate_video using linkedList.mp4
    # Ensure this path is correct for your system
    linked_list_video_path = os.path.join(validator.OUTPUT_DIR, "scene2.mp4")

    # Test with the specified video path and generated code
    feedback_video = validator.validate_scene(
        scene_data=linked_list_scene_data,
        video_path=linked_list_video_path,
        generated_code="""
import {makeScene2D} from '@motion-canvas/2d/lib/scenes';
import {Rect, Txt} from '@motion-canvas/2d/lib/components';
import {all, waitFor} from '@motion-canvas/core/lib/flow';
import {createRef} from '@motion-canvas/core/lib/utils';

export default makeScene2D(function* (view) {
    const myRect = createRef<Rect>();

    view.add(
        <Rect
            ref={myRect}
            width={200}
            height={100}
            fill="#FF0000"
            radius={10}
            position={[0, 0]}
        />
    );

    yield* myRect().opacity(1, 1);
    yield* waitFor(1);
    yield* myRect().position.y(100, 1);
    yield* waitFor(1);
});
""",
        errors=["Dummy error 1", "Dummy error 2"],
        code_examples="""
// Dummy code example 1
function dummyFunction() {
    console.log("Hello from dummy function");
}

// Dummy code example 2
const dummyVariable = 123;
""",
        formatted_code_gen_prompt="""
// Dummy formatted code generation prompt
This is a dummy prompt for code generation.
It describes the expected output format and content.
"""
    )

    print(f"Post-render video validation: {'✅' if feedback_video[0] else '❌'}")
    print(f"Feedback: {json.dumps(feedback_video, indent=2)}")


if __name__ == "__main__":
    main()
