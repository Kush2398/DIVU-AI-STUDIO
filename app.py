# =========================================================
# DIVU AI IMAGE GENERATOR
# PERFECT CLEAN WEBSITE VERSION
# =========================================================

from flask import (
    Flask,
    request,
    jsonify,
    send_from_directory
)

from flask_cors import CORS

from huggingface_hub import InferenceClient

import requests
import urllib.parse
import random
import os
import time

# =========================================================
# FLASK
# =========================================================

app = Flask(__name__)

CORS(app)

# =========================================================
# TOKENS
# =========================================================

HF_TOKEN = os.getenv("HF_TOKEN")

# =========================================================
# HUGGINGFACE CLIENT
# =========================================================

client = InferenceClient(

    token=HF_TOKEN
)

# =========================================================
# SERVER URL
# =========================================================

SERVER_URL = "http://127.0.0.1:5000"

# =========================================================
# PATHS
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

OUTPUT_FOLDER = os.path.join(
    BASE_DIR,
    "static",
    "op"
)

os.makedirs(
    OUTPUT_FOLDER,
    exist_ok=True
)

# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return send_from_directory(

        BASE_DIR,

        "index.html"
    )

# =========================================================
# CLEAN PROMPT
# =========================================================

def clean_image_prompt(prompt):

    prompt = prompt.lower()

    remove_words = [

        "generate image of",
        "generate image",
        "create image",
        "make image",
        "draw",
        "picture of",
        "photo of"
    ]

    for word in remove_words:

        prompt = prompt.replace(
            word,
            ""
        )

    return prompt.strip()

# =========================================================
# DETECT STYLE
# =========================================================

def detect_style(prompt):

    prompt = prompt.lower()

    if "anime" in prompt:

        return """
        anime masterpiece,
        studio ghibli style,
        vibrant anime colors,
        detailed anime art
        """

    elif "cyberpunk" in prompt:

        return """
        cyberpunk,
        futuristic neon city,
        blade runner style,
        neon lights
        """

    elif "realistic" in prompt:

        return """
        ultra realistic,
        DSLR photography,
        cinematic lighting
        """

    elif any(word in prompt for word in [

        "space",
        "galaxy",
        "nebula",
        "cosmic",
        "universe"

    ]):

        return """
        deep space,
        galaxy,
        nebula,
        stars,
        cosmic universe,
        NASA photography
        """

    return """
    ultra realistic,
    cinematic lighting,
    masterpiece,
    8k
    """

# =========================================================
# ENHANCE PROMPT
# =========================================================

def enhance_prompt(user_prompt):

    cleaned_prompt = clean_image_prompt(
        user_prompt
    )

    style = detect_style(
        cleaned_prompt
    )

    final_prompt = f"""
    {style}

    MASTERPIECE,
    BEST QUALITY,
    ULTRA DETAILED,
    8K,
    ULTRA REALISTIC,
    CINEMATIC LIGHTING,
    VOLUMETRIC LIGHTING,
    SHARP FOCUS,

    SUBJECT:
    {cleaned_prompt}
    """

    return final_prompt

# =========================================================
# GENERATE IMAGE
# =========================================================

def generate_ai_image(prompt):

    try:

        seed = random.randint(
            1000,
            999999
        )

        enhanced_prompt = enhance_prompt(
            prompt
        )

        print("\nFINAL PROMPT:\n")
        print(enhanced_prompt)

        # =====================================
        # TRY HUGGING FACE FIRST
        # =====================================

        try:

            print("\nUSING HUGGING FACE...\n")

            image = client.text_to_image(

                enhanced_prompt,

                model=
                "black-forest-labs/FLUX.1-schnell"
            )

            filename = (
                f"divu_"
                f"{int(time.time())}_"
                f"{seed}.png"
            )

            output_path = os.path.join(
                OUTPUT_FOLDER,
                filename
            )

            image.save(output_path)

            return (
                f"{SERVER_URL}/static/op/{filename}"
            )

        except Exception as hf_error:

            print("\nHF FAILED:\n")
            print(hf_error)

        # =====================================
        # FALLBACK TO POLLINATIONS
        # =====================================

        print("\nUSING POLLINATIONS...\n")

        encoded_prompt = urllib.parse.quote(
            enhanced_prompt
        )

        image_url = (

            "https://image.pollinations.ai/prompt/"
            + encoded_prompt
            + f"?width=1024"
            + f"&height=1024"
            + f"&seed={seed}"
            + "&model=flux"
            + "&enhance=true"
            + "&private=true"
            + "&safe=false"
            + "&nologo=true"
        )

        response = requests.get(

            image_url,

            timeout=120
        )

        if response.status_code != 200:

            return None

        filename = (
            f"divu_"
            f"{int(time.time())}_"
            f"{seed}.jpg"
        )

        output_path = os.path.join(
            OUTPUT_FOLDER,
            filename
        )

        with open(output_path, "wb") as f:

            f.write(response.content)

        return (
            f"{SERVER_URL}/static/op/{filename}"
        )

    except Exception as e:

        print("\nIMAGE ERROR:\n")
        print(e)

        return None

# =========================================================
# GENERATE IMAGE ROUTE
# =========================================================

@app.route(
    "/generate-image",
    methods=["POST"]
)
def generate_image():

    try:

        data = request.get_json()

        if not data:

            return jsonify({

                "success": False,

                "message":
                "No data received"
            })

        prompt = data.get(
            "prompt",
            ""
        ).strip()

        if not prompt:

            return jsonify({

                "success": False,

                "message":
                "Please enter prompt"
            })

        image_path = generate_ai_image(
            prompt
        )

        if image_path:

            return jsonify({

                "success": True,

                "image": image_path
            })

        return jsonify({

            "success": False,

            "message":
            "Failed to generate image"
        })

    except Exception as e:

        print("\nROUTE ERROR:\n")
        print(e)

        return jsonify({

            "success": False,

            "message":
            str(e)
        })

# =========================================================
# IMAGE HISTORY
# =========================================================

@app.route("/history")
def history():

    try:

        images = []

        for file in os.listdir(
            OUTPUT_FOLDER
        ):

            if file.endswith((
                ".jpg",
                ".jpeg",
                ".png",
                ".webp"
            )):

                images.append(

                    f"{SERVER_URL}/static/op/{file}"
                )

        images.sort(
            reverse=True
        )

        return jsonify({

            "success": True,

            "images": images[:50]
        })

    except Exception as e:

        print(e)

        return jsonify({

            "success": False,

            "images": []
        })

# =========================================================
# SERVE IMAGES
# =========================================================

@app.route("/static/op/<filename>")
def serve_image(filename):

    return send_from_directory(

        OUTPUT_FOLDER,

        filename
    )

# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    print("\nDIVU AI SERVER STARTING...\n")

    app.run(

        host="0.0.0.0",

        port=5000,

        debug=True
    )
