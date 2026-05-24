# -*- coding: utf-8 -*-
"""
DPO Dataset Preparation Pipeline (Optimized v5)
Author: Sophia Fente-Damers & Gemini Clinical ML Pipeline

This script automates Phase 3 and bridges into Phase 4 of the MAGIC pipeline:
1. Scales up I2I translation across all 28 FST V source images.
2. Generates N candidate variations exploring different translation strengths.
3. Runs a programmatic Pixel-Difference Guardrail to prevent "identity leakage" (copying real images).
4. Automatically runs the hardened GPT-4o clinical checklist scorer on valid candidates.
5. Saves a formatted DPO JSONL dataset ready for Direct Preference Optimization (DPO) training.
"""

import os
import glob
import json
import base64
import time
import torch
import shutil
import numpy as np
from pathlib import Path
from tqdm import tqdm
from PIL import Image
from openai import OpenAI
from google.colab import userdata
from diffusers import StableDiffusionImg2ImgPipeline

# ==========================================
# CONSTANTS & DIRECTORY PATHS
# ==========================================
SOURCE_DIR = "data/flexible/5/psoriasis_padded" # Target our aspect-ratio padded images
DPO_WORK_DIR = "/content/drive/MyDrive/skin-augment-data/dpo_dataset_prep"
CANDIDATES_DIR = os.path.join(DPO_WORK_DIR, "candidates")
FINAL_DATASET_DIR = os.path.join(DPO_WORK_DIR, "dpo_preference_dataset")

# Model checkpoints
LORA_PATH = "/content/drive/MyDrive/skin-augment-data/models/lora_psoriasis_fst5_v3/checkpoint-600/pytorch_lora_weights.safetensors"
TI_PATH = "/content/drive/MyDrive/skin-augment-data/models/ti_psoriasis_fst5_v2/learned_embeds-steps-2000.safetensors"

# Quality & Visual Difference Guardrails
CHOSEN_THRESHOLD = 4 
MIN_VISUAL_SHIFT = 0.06  # Candidates must have at least a 6% pixel change to avoid "identity copy" loop

# Make directories
os.makedirs(CANDIDATES_DIR, exist_ok=True)
os.makedirs(FINAL_DATASET_DIR, exist_ok=True)

# Define the clinical evaluation checklist
PSORIASIS_CHECKLIST = """
1. Location: Are lesions on typical psoriasis sites (elbows, knees, scalp, lower back, palms, soles)?
2. Lesion type: Are there well-demarcated plaques or papules with a clearly defined edge?
3. Scale character: Is there thick adherent layered scale (grey-white or ashy on dark skin)?
4. Plaque colour: Does the plaque show red/pink on light skin OR purple/dark brown on darker skin?
5. Plaque raised: Are plaques clearly elevated above surrounding skin surface?
6. Auspitz sign: Is there evidence of pinpoint bleeding or darker spots at scale edges?
7. Post-inflammatory change: Is there surrounding hyperpigmentation or halo around plaques?
"""

# ==========================================
# RETRY LOGIC / EXPONENTIAL BACKOFF FOR API
# ==========================================
def call_openai_with_backoff(client, payload, max_retries=5):
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(**payload)
            return response
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"\n❌ API critical failure after {max_retries} attempts: {e}")
                raise e
            sleep_time = 2 ** attempt
            time.sleep(sleep_time)

# ==========================================
# SCORING & PROGRAMMATIC DIFFERENCE ENGINES
# ==========================================
def calculate_visual_difference(img_path_1, img_path_2):
    """
    Computes normalized Mean Absolute Error (MAE) between two images.
    Filters out candidates that are pixel-for-pixel clones of the source.
    """
    img1 = Image.open(img_path_1).convert("L").resize((256, 256))
    img2 = Image.open(img_path_2).convert("L").resize((256, 256))
    
    arr1 = np.array(img1, dtype=np.float32) / 255.0
    arr2 = np.array(img2, dtype=np.float32) / 255.0
    
    mae = np.mean(np.abs(arr1 - arr2))
    return float(mae)

def score_candidate(client, image_path):
    """Encodes candidate image and runs the structured GPT-4o evaluation."""
    with open(image_path, "rb") as f:
        b64_image = base64.b64encode(f.read()).decode("utf-8")
        
    payload = {
        "model": "gpt-4o",
        "response_format": { "type": "json_object" },
        "messages": [{"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}},
            {"type": "text", "text": f"""Analyze this medical imaging file against the structural criteria:
{PSORIASIS_CHECKLIST}

You must return a valid JSON object containing a single key "scores" mapping to a list of exactly 7 binary choices (1=satisfied, 0=not satisfied).
Example Output: {{"scores": [1, 0, 1, 0, 1, 0, 0]}}"""}
        ]}],
        "max_tokens": 100,
        "temperature": 0.0
    }
    
    try:
        response = call_openai_with_backoff(client, payload)
        raw_content = response.choices[0].message.content.strip()
        parsed_json = json.loads(raw_content)
        scores = parsed_json["scores"]
        assert len(scores) == 7
        return scores
    except Exception as e:
        return [0, 0, 0, 0, 0, 0, 0]

# ==========================================
# PIPELINE EXECUTION
# ==========================================
def run_dpo_preparation_pipeline(num_candidates_per_image=3):
    global SOURCE_DIR
    
    # 1. Initialize OpenAI Client
    print("🔑 Authenticating API channels...")
    api_key = userdata.get('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("Missing 'OPENAI_API_KEY' in Colab Secrets!")
    openai_client = OpenAI(api_key=api_key)
    
    # 2. Robust Source Path Resolution Engine
    candidates = [
        "data/flexible/5/psoriasis_padded",
        "/content/skin-augment-fst456/data/flexible/5/psoriasis_padded",
        "/content/data/flexible/5/psoriasis_padded"
    ]
    resolved_source = None
    for path in candidates:
        if os.path.exists(path) and len(os.listdir(path)) > 0:
            resolved_source = path
            break
            
    if resolved_source:
        SOURCE_DIR = resolved_source
        print(f"📂 Resolved source directory successfully to: {SOURCE_DIR}")
    else:
        print(f"⚠️ Warning: Could not find any valid source images in expected locations: {candidates}")
    
    # 3. Initialize Image-to-Image pipeline
    print("🧬 Loading Dual-Engine Image-to-Image Pipeline...")
    pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
        "runwayml/stable-diffusion-v1-5",
        torch_dtype=torch.float16,
        safety_checker=None
    ).to("cuda")
    
    # Load learned TI token
    if os.path.exists(TI_PATH):
        pipe.load_textual_inversion(TI_PATH, token="<psoriasis-fst5>")
        print("  ✅ Textual Inversion concept vocabulary loaded.")
    else:
        print("  ⚠️ Warning: TI checkpoint not found. Proceeding with LoRA only.")
        
    # Load LoRA detail weights
    if os.path.exists(LORA_PATH):
        pipe.load_lora_weights(LORA_PATH)
        print("  ✅ LoRA detail weights loaded.")
    else:
        raise FileNotFoundError(f" LoRA weights not found at: {LORA_PATH}")
        
    # 4. Gather Source Images
    source_images = sorted(glob.glob(os.path.join(SOURCE_DIR, "*.jpg")))
    print(f"📂 Found {len(source_images)} source images to process.")
    
    if len(source_images) == 0:
        raise ValueError(f"No source images found! Visited: {SOURCE_DIR}")
        
    # 5. Refined Clinical Prompts (Aggressively blocking nodular hallucinations)
    target_prompt = (
        "A close-up high-definition clinical photograph of severe flat plaque psoriasis <psoriasis-fst5>. "
        "Dry, heavy, multi-layered micaceous white scale buildup, dry crusty desquamating texture, "
        "flat well-demarcated plaque borders, high-contrast crisp details."
    )
    
    negative_prompt = (
        "smooth skin, healthy skin, glossy skin, shiny texture, wet look, pink skin, magenta artifacts, "
        "pus, pustules, yellow fluid, infection, wet ooze, raw tissue, bleeding, blurry, out of focus, "
        "bumpy nodules, keloids, warts, tumors, round cysts, raised circular bumps, circular blisters, "
        "shiny bumps, dark round nodules, moles, skin tags, neurofibromatosis, prurigo nodularis"
    )
    
    # 6. Candidate Generation & Scoring Loop
    print(f"🎨 Generating {num_candidates_per_image} variations for all {len(source_images)} images...")
    
    # Pushed to higher strengths to force visual modifications
    strength_range = [0.48, 0.55, 0.62] if num_candidates_per_image == 3 else [0.55] * num_candidates_per_image
    
    scored_dataset = {}
    
    for idx, img_path in enumerate(tqdm(source_images, desc="Processing Source Anatomy")):
        base_name = Path(img_path).stem
        init_image = Image.open(img_path).convert("RGB").resize((512, 512))
        
        scored_dataset[base_name] = []
        
        for cand_idx in range(num_candidates_per_image):
            cand_filename = f"{base_name}_cand_{cand_idx}.jpg"
            cand_filename_full = os.path.join(CANDIDATES_DIR, cand_filename)
            
            # Use deterministic seed offset per candidate
            seed = 1000 + idx * 10 + cand_idx
            generator = torch.Generator("cuda").manual_seed(seed)
            
            # Apply dynamic strengths across candidates to find the clinical sweet spot
            current_strength = strength_range[cand_idx % len(strength_range)]
            
            # Execute generation
            candidate_img = pipe(
                prompt=target_prompt,
                negative_prompt=negative_prompt,
                image=init_image,
                strength=current_strength,
                guidance_scale=11.0, 
                num_inference_steps=55,
                generator=generator
            ).images[0]
            
            # Save candidate locally
            candidate_img.save(cand_filename_full)
            
            # Calculate difference against the raw source
            visual_delta = calculate_visual_difference(img_path, cand_filename_full)
            
            # Evaluate using GPT-4o
            scores = score_candidate(openai_client, cand_filename_full)
            total_score = sum(scores)
            
            scored_dataset[base_name].append({
                "filepath": cand_filename_full,
                "filename": cand_filename,
                "scores": scores,
                "total_score": total_score,
                "visual_delta": visual_delta,
                "strength": current_strength,
                "seed": seed
            })
            
    # Save raw scoring history to Drive
    with open(os.path.join(DPO_WORK_DIR, "raw_scoring_history.json"), "w") as f:
        json.dump(scored_dataset, f, indent=4)
        
    # 7. Preference Pair Compilation with Quality and Leakage Filters
    print("\n⚖️ Compiling high-fidelity clinical preference pairs for DPO format...")
    dpo_pairs = []
    pair_count = 0
    rejected_quality_count = 0
    rejected_leakage_count = 0
    
    for base_name, candidates_list in scored_dataset.items():
        # Filter candidates to only those that meet the visual difference threshold
        valid_candidates = [c for c in candidates_list if c["visual_delta"] >= MIN_VISUAL_SHIFT]
        
        if len(valid_candidates) < 2:
            rejected_leakage_count += 1
            continue
            
        # Sort valid candidates by score descending
        sorted_cands = sorted(valid_candidates, key=lambda x: x["total_score"], reverse=True)
        
        best = sorted_cands[0]
        worst = sorted_cands[-1]
        
        if best["total_score"] > worst["total_score"]:
            if best["total_score"] >= CHOSEN_THRESHOLD:
                pair_count += 1
                
                # Define destination paths in the clean training directory
                chosen_dest = os.path.join(FINAL_DATASET_DIR, f"pair_{pair_count:03d}_chosen.jpg")
                rejected_dest = os.path.join(FINAL_DATASET_DIR, f"pair_{pair_count:03d}_rejected.jpg")
                
                # Copy images to final dataset folder
                shutil.copy2(best["filepath"], chosen_dest)
                shutil.copy2(worst["filepath"], rejected_dest)
                
                # Create DPO JSON entry
                dpo_pairs.append({
                    "prompt": target_prompt,
                    "chosen_image": f"pair_{pair_count:03d}_chosen.jpg",
                    "rejected_image": f"pair_{pair_count:03d}_rejected.jpg",
                    "chosen_score": best["total_score"],
                    "rejected_score": worst["total_score"],
                    "score_delta": best["total_score"] - worst["total_score"],
                    "chosen_vector": best["scores"],
                    "rejected_vector": worst["scores"]
                })
            else:
                rejected_quality_count += 1
            
    # Save the standard metadata JSONL for the HuggingFace trl trainer
    metadata_path = os.path.join(FINAL_DATASET_DIR, "metadata.jsonl")
    with open(metadata_path, "w") as jsonl_file:
        for entry in dpo_pairs:
            jsonl_file.write(json.dumps(entry) + "\n")
            
    print("\n" + "="*50)
    print("DPO PREPARATION RUN COMPLETE:")
    print(f"Total Source Images Scanned: {len(source_images)}")
    print(f"Total Candidates Generated: {len(source_images) * num_candidates_per_image}")
    print(f"Constructed Preference Pairs (Chosen Score >= {CHOSEN_THRESHOLD}): {pair_count}")
    print(f"Discarded Pairs (Below Chosen Quality Threshold): {rejected_quality_count}")
    print(f"Discarded Pairs (Identity Leaks / No Visual Change): {rejected_leakage_count}")
    print(f"DPO Preference Dataset saved to: {FINAL_DATASET_DIR}")
    print(f"Metadata Manifest written: {metadata_path}")
    print("="*50)

if __name__ == "__main__":
    run_dpo_preparation_pipeline(num_candidates_per_image=3)