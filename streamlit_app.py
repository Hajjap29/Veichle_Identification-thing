import streamlit as st
import os, base64, json, requests
from PIL import Image
import io

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def resize_image(image_path, max_size=2048):
    """Resize image to meet OpenAI requirements"""
    img = Image.open(image_path)
    
    # Convert RGBA to RGB if needed
    if img.mode == 'RGBA':
        img = img.convert('RGB')
    
    # Resize if too large
    if max(img.size) > max_size:
        img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
    
    # Save to bytes
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=85)
    buffer.seek(0)
    return buffer.getvalue()

def image_to_data_uri(image_bytes):
    """Convert image bytes to data URI"""
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:image/jpeg;base64,{b64}"

PROMPT_JSON = """
You are an image-understanding assistant. Identify the car make and model.
Respond with JSON only: { "make": "...", "model": "..." }
"""

def call_vision_api_with_image(data_uri, prompt_text=PROMPT_JSON):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}", 
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "gpt-4o-mini",
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
                            "url": data_uri,
                            "detail": "auto"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 300
    }
    
    r = requests.post(url, headers=headers, json=payload, timeout=30)
    
    # Show detailed error before raising
    if r.status_code != 200:
        st.error(f"❌ API Error: {r.status_code}")
        try:
            error_data = r.json()
            st.error(f"Error details: {error_data}")
        except:
            st.error(f"Response text: {r.text[:500]}")
    
    r.raise_for_status()
    return r.json()

def extract_json_from_response(resp_json):
    try:
        text = resp_json["choices"][0]["message"]["content"]
        text = text.strip()
        
        # Remove markdown code blocks
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        
        text = text.strip()
        return json.loads(text)
    except Exception as e:
        return {
            "error": f"Parse error: {str(e)}", 
            "raw_response": text if 'text' in locals() else str(resp_json)
        }

# Main UI
st.title("🚗 Car Image Analyzer")

# API Key Status
if OPENAI_API_KEY:
    key_preview = OPENAI_API_KEY[:10] + "..." if len(OPENAI_API_KEY) > 10 else "***"
    st.success(f"✓ API Key loaded: {key_preview}")
else:
    st.error("❌ OPENAI_API_KEY not found!")
    st.info("""
    **To fix this:**
    1. Go to your Streamlit Cloud app
    2. Click Settings (⚙️) → Secrets
    3. Add: `OPENAI_API_KEY = "sk-proj-your-key"`
    4. Save and restart
    """)
    st.stop()

uploaded = st.file_uploader("Upload an image of a car", type=["jpg", "jpeg", "png", "webp"])

if uploaded:
    # Save and resize image
    temp_path = "/tmp/upload.jpg"
    with open(temp_path, "wb") as f:
        f.write(uploaded.read())
    
    try:
        # Resize image to meet OpenAI requirements
        resized_bytes = resize_image(temp_path)
        data_uri = image_to_data_uri(resized_bytes)
        
        # Show image
        st.image(resized_bytes, caption="Uploaded Image", use_column_width=True)
        
        # Show image size info
        img_size_kb = len(resized_bytes) / 1024
        st.caption(f"Image size: {img_size_kb:.1f} KB")
        
    except Exception as e:
        st.error(f"Error processing image: {e}")
        st.stop()

    if st.button("🔍 Analyze Car", type="primary"):
        with st.spinner("Analyzing image..."):
            try:
                resp = call_vision_api_with_image(data_uri)
                result = extract_json_from_response(resp)
                
                st.success("✅ Analysis complete!")
                
                # Display results
                if "make" in result and "model" in result and "error" not in result:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Make", result["make"])
                    with col2:
                        st.metric("Model", result["model"])
                else:
                    st.warning("Could not extract make/model")
                
                # Show full response
                with st.expander("View Full Response"):
                    st.json(result)
                    
            except requests.exceptions.HTTPError as e:
                st.error(f"❌ HTTP Error: {e}")
                if hasattr(e, 'response') and e.response is not None:
                    st.error(f"Status Code: {e.response.status_code}")
                    st.code(e.response.text)
            except Exception as e:
                st.error(f"❌ Unexpected Error: {type(e).__name__}")
                st.exception(e)

# Add requirements.txt info
import streamlit as st
import os, base64, json, requests
from PIL import Image
import io

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def resize_image(image_path, max_size=2048):
    """Resize image to meet OpenAI requirements"""
    img = Image.open(image_path)
    
    # Convert RGBA to RGB if needed
    if img.mode == 'RGBA':
        img = img.convert('RGB')
    
    # Resize if too large
    if max(img.size) > max_size:
        img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
    
    # Save to bytes
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=85)
    buffer.seek(0)
    return buffer.getvalue()

def image_to_data_uri(image_bytes):
    """Convert image bytes to data URI"""
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:image/jpeg;base64,{b64}"

PROMPT_JSON = """
You are an image-understanding assistant. Identify the car make and model.
Respond with JSON only: { "make": "...", "model": "..." }
"""

def call_vision_api_with_image(data_uri, prompt_text=PROMPT_JSON):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}", 
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "gpt-4o-mini",
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
                            "url": data_uri,
                            "detail": "auto"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 300
    }
    
    r = requests.post(url, headers=headers, json=payload, timeout=30)
    
    # Show detailed error before raising
    if r.status_code != 200:
        st.error(f"❌ API Error: {r.status_code}")
        try:
            error_data = r.json()
            st.error(f"Error details: {error_data}")
        except:
            st.error(f"Response text: {r.text[:500]}")
    
    r.raise_for_status()
    return r.json()

def extract_json_from_response(resp_json):
    try:
        text = resp_json["choices"][0]["message"]["content"]
        text = text.strip()
        
        # Remove markdown code blocks
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        
        text = text.strip()
        return json.loads(text)
    except Exception as e:
        return {
            "error": f"Parse error: {str(e)}", 
            "raw_response": text if 'text' in locals() else str(resp_json)
        }

# Main UI
st.title("🚗 Car Image Analyzer")

# API Key Status
if OPENAI_API_KEY:
    key_preview = OPENAI_API_KEY[:10] + "..." if len(OPENAI_API_KEY) > 10 else "***"
    st.success(f"✓ API Key loaded: {key_preview}")
else:
    st.error("❌ OPENAI_API_KEY not found!")
    st.info("""
    **To fix this:**
    1. Go to your Streamlit Cloud app
    2. Click Settings (⚙️) → Secrets
    3. Add: `OPENAI_API_KEY = "sk-proj-your-key"`
    4. Save and restart
    """)
    st.stop()

uploaded = st.file_uploader("Upload an image of a car", type=["jpg", "jpeg", "png", "webp"])

if uploaded:
    # Save and resize image
    temp_path = "/tmp/upload.jpg"
    with open(temp_path, "wb") as f:
        f.write(uploaded.read())
    
    try:
        # Resize image to meet OpenAI requirements
        resized_bytes = resize_image(temp_path)
        data_uri = image_to_data_uri(resized_bytes)
        
        # Show image
        st.image(resized_bytes, caption="Uploaded Image", use_column_width=True)
        
        # Show image size info
        img_size_kb = len(resized_bytes) / 1024
        st.caption(f"Image size: {img_size_kb:.1f} KB")
        
    except Exception as e:
        st.error(f"Error processing image: {e}")
        st.stop()

    if st.button("🔍 Analyze Car", type="primary"):
        with st.spinner("Analyzing image..."):
            try:
                resp = call_vision_api_with_image(data_uri)
                result = extract_json_from_response(resp)
                
                st.success("✅ Analysis complete!")
                
                # Display results
                if "make" in result and "model" in result and "error" not in result:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Make", result["make"])
                    with col2:
                        st.metric("Model", result["model"])
                else:
                    st.warning("Could not extract make/model")
                
                # Show full response
                with st.expander("View Full Response"):
                    st.json(result)
                    
            except requests.exceptions.HTTPError as e:
                st.error(f"❌ HTTP Error: {e}")
                if hasattr(e, 'response') and e.response is not None:
                    st.error(f"Status Code: {e.response.status_code}")
                    st.code(e.response.text)
            except Exception as e:
                st.error(f"❌ Unexpected Error: {type(e).__name__}")
                st.exception(e)

