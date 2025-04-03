import os
import base64
import json
from src.utils.llm import LLMSingleton

# 1. Install the Anthropic Python library (if you haven't already)
# pip install anthropic

# 2. Set your Anthropic API key as an environment variable
# You can do this in your terminal:
# export ANTHROPIC_API_KEY="your_anthropic_api_key"
# Or in your Python script (not recommended for production):
# os.environ["ANTHROPIC_API_KEY"] = "your_anthropic_api_key"

llm = LLMSingleton.get_instance()
        
def analyze_thermal_image_for_hazards(image_path):
    """
    Uploads a thermal image to Claude and asks it to identify hazards.

    Args:
        image_path (str): The path to the thermal image file.

    Returns:
        str: Claude's response identifying potential hazards, or None if an error occurs.
    """
    try:
        # Initialize the Anthropic client

        # 3. Read the thermal image file in binary mode
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()

        # 4. Encode the image data in base64
        encoded_image = base64.b64encode(image_data).decode("utf-8")

        # Determine the media type based on the file extension (you might need more robust logic)
        media_type = "image/jpeg"

        # 5. Construct the API request payload
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": encoded_image,
                        },
                    },
                    {
                        "type": "text",
                        "text": "Identify any potential hazards visible in this thermal image. Explain what makes them a hazard based on the thermal information. return in a json response",
                    },
                ],
            }
        ]

        # 6. Make the API call to Claude
        response = llm.invoke(messages)

        print(json.dumps(response.content, indent=2))
        
        # 7. Process the response
        if response.content:
            return response.content
        else:
            return "No response received from Claude."

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def analyze_audio_for_hazards(audio_file_path):
    try:
        with open(audio_file_path, "rb") as audio_file:
            audio_content = audio_file.read()
    
        mime_type = 'audio/wav'  # Replace with the actual MIME type
        
        messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Analyze the attached audio file for any signs of distress. This includes but is not limited to cries for help, panicked language, urgent requests, and specific keywords indicating an emergency. Indicate if distress signals are present and provide a brief explanation based on the audio content."
                        },
                        {
                            "type": "audio",
                            "data": base64.b64encode(audio_content).decode("utf-8"),
                            "mime_type": mime_type
                        }
                    ]
                }
            ]
                # 6. Make the API call to Claude
        response = llm.invoke(messages)

        print(json.dumps(response.content, indent=2))
        
        # 7. Process the response
        if response.content:
            return response.content
        else:
            return "No response received from Claude."
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return None    
        
        
if __name__ == "__main__":
    # Path to the thermal image file
    image_file_path = "datasets/sensor_data_samples/thermal_images/thermal_image.jpeg"
    audio_file_path = "datasets/sensor_data_samples/audio_signals/sad_sound.mp3"
    hazards_identified = analyze_thermal_image_for_hazards(image_file_path)
    # hazards_identified = analyze_audio_for_hazards(audio_file_path)

    if hazards_identified:
        print("\nPotential hazards identified by Claude:")
        print(hazards_identified)
    else:
        print("Could not analyze the image for hazards.")