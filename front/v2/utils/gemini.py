import os
# from PIL import ImageGrab, Image
import google.generativeai as genai


class GeminiModel:
    def __init__(self, model_name="gemini-2.0-flash-exp"):
        self.model_name = model_name

        # Hardcoded API Key
        self.api_key = "AIzaSyALOzljnZ4lygbVr2Jt-QO544-UVbXwtEE"  # Replace with your actual API key
        # you can use .env for this
        if not self.api_key:
            raise ValueError("API key not found.")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)

    def call_model(self, user_prompt, system_prompt=None, image_paths=None):
        messages = []

        if system_prompt:
            messages.append({"role": "user", "parts": [system_prompt]})
            messages.append({"role": "model", "parts": ["Understood."]})

        user_message = {"role": "user", "parts": [user_prompt]}

        #    if image_paths:
        #        img_objects = [Image.open(img_path) for img_path in image_paths]
        #        user_message["parts"].extend(img_objects)

        messages.append(user_message)
        print(f"DEBUG: Sending system prompt: {system_prompt}")
        print(f"DEBUG: Sending user prompt: {user_prompt}")
        response = self.model.generate_content(messages)
        print(f"DEBUG: Answer {response.text}")

        return response.text


'''
    def send_screenshot_to_model(self, user_prompt, system_prompt=None):
        screenshot_path = "screenshot.png"
        screenshot = ImageGrab.grab()
        screenshot.save(screenshot_path, "PNG")

        response = self.call_model(user_prompt, system_prompt=system_prompt, image_paths=[screenshot_path])
        return response
if __name__ == "__main__":
    gemini_model = GeminiModel(model_name="gemini-1.5-pro")
    response = gemini_model.send_screenshot_to_model("Can you help analyze my screen?") #demonstration
    print(response)
'''