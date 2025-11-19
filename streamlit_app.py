import streamlit as st
import os, base64, json, requests

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def image_file_to_data_uri(path):
    with open(path, "rb") as f:
        data = f.read()
    mime = "image/jpeg"
    b64 = base64.b64encode(data).decode("utf-8")
    return f"data:{mime};base64,{b64}"

PROMPT_JSON = """
You are an image-understanding assistant. Identify the car make, model.
Respond with JSON only: { "make": "...", "model": "..." }
"""

def call_vision_api_with_image(data_uri, prompt_text=PROMPT_JSON):
    # Correct OpenAI API endpoint
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}", 
        "Content-Type": "application/json"
    }
    
    # Correct payload format for OpenAI Vision API
    payload = {
        "model": "gpt-4o",  # Use gpt-4o, gpt-4o-mini, or gpt-4-turbo
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt_text
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": data_uri
                        }
                    }
                ]
            }
        ],
        "max_tokens": 300
    }
    
    r = requests.post(url, headers=headers, data=json.dumps(payload))
    r.raise_for_status()
    return r.json()

def extract_json_from_response(resp_json):
    try:
        text = resp_json["choices"][0]["message"]["content"]
        # Remove markdown code blocks if present
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        return json.loads(text)
    except Exception as e:
        st.error(f"Error parsing response: {e}")
        return {"error": "Could not parse response", "raw": text}

st.title("Car Image Analyzer")

uploaded = st.file_uploader("Upload an image of a car", type=["jpg","jpeg","png"])
if uploaded:
    temp_path = "/tmp/upload.jpg"
    with open(temp_path, "wb") as f:
        f.write(uploaded.read())
    data_uri = image_file_to_data_uri(temp_path)
    st.image(uploaded, caption="Uploaded Image")

    if st.button("Analyze"):
        if not OPENAI_API_KEY:
            st.error("OPENAI_API_KEY environment variable is not set!")
        else:
            with st.spinner("Analyzing..."):
                try:
                    resp = call_vision_api_with_image(data_uri)
                    result = extract_json_from_response(resp)
                    st.json(result)
                except requests.exceptions.HTTPError as e:
                    st.error(f"API Error: {e.response.status_code}")
                    if e.response.status_code == 401:
                        st.error("Invalid API key. Check your OPENAI_API_KEY.")
                    elif e.response.status_code == 429:
                        st.error("Rate limit exceeded or quota reached.")
                    else:
                        st.error(f"Response: {e.response.text}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
