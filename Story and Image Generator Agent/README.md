# Story & Character Image Generator API

This Flask-based API serves as a backend system for generating creative storylines and detailed, visually-focused character descriptions. It then leverages Google's Gemini API to generate corresponding images for these characters, ensuring style consistency.

The project demonstrates a pipeline where textual creative content is generated and then transformed into visual assets, making it suitable for applications requiring dynamic story and character visualization.

## Features

- **Storyline Generation:** Generates a 3-5 paragraph storyline based on a given topic and description.

- **Detailed Character Descriptions:** Creates character descriptions focusing exclusively on physical attributes, clothing, accessories, and visual elements within a scene, optimized for image generation.

- **Image Generation:** Utilizes the `gemini-2.0-flash-preview-image-generation` model to create images for each generated character.

- **Style Consistency:** Accepts a `style` input to ensure all generated images for a story maintain a consistent visual aesthetic.

- **Negative Prompting:** Incorporates built-in negative prompts to reduce the generation of undesirable or inconsistent image features (e.g., multiple limbs, weird eyes, non-white backgrounds for characters).

- **Orchestration Endpoint:** A single endpoint (`/generate_story_with_images`) to automate the entire process from story generation to image generation for all characters.

- **Static File Serving:** Serves generated images directly from the Flask application.

## Setup

Follow these steps to get the project up and running on your local machine.

### Prerequisites

- Python 3.8+

- `pip` (Python package installer)

- A Google AI Studio API Key.
