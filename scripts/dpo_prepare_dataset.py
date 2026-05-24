# -*- coding: utf-8 -*-
"""
DPO Dataset Preparation Pipeline
Author: Sophia Fente-Damers & Gemini Clinical ML Pipeline
"""

import os, glob, json, base64, time, torch, shutil, re
from pathlib import Path
from tqdm import tqdm
from PIL import Image
from openai import OpenAI
from diffusers import StableDiffusionImg2ImgPipeline

SOURCE_DIR = "data/flexible/5/psoriasis"
DPO_WORK_DIR = "/content/drive/MyDrive/skin-augment-data/dpo_dataset_prep"
CANDIDATES_DIR = os.path.join(DPO_WORK_DIR, "candidates")
FINAL_DATASET_DIR = os.path.join(DPO_WORK_DIR, "dpo_preference_dataset")
LORA_PATH = "/content/drive/MyDrive/skin-augment-data/models/lora_psoriasis_fst5_v3/checkpoint-600/pytorch_lora_weights.safetensors"

os.makedirs(CANDIDATES_DIR, exist_ok=True)
os.makedirs(FINAL_DATASET_DIR, exist_ok=True)

PSORIASIS_CHECKLIST = """
1. Location: Are lesions on typical psoriasis sites (elbows, knees, scalp, lower back, palms, soles)?
2. Lesion type: Are there well-demarcated plaques or papules with a clearly defined edge?
3. Scale character: Is there thick adherent layered scale (grey-white or ashy on dark skin)?
4. Plaque colour: Does the plaque show red/pink on light skin OR purple/dark brown on darker skin?
5. Plaque raised: Are plaques clearly elevated above surrounding skin surface?
6. Auspitz sign: Is there evidence of pinpoint bleeding or darker spots at scale edges?
7. Post-inflammatory change: Is there surrounding hyperpigmentation or halo around plaques?
"""

def call_openai_with_backoff(client, payload, max_retries=5):
    for attempt in range(max_retries):
        try:
            return client.chat.completions.create(**payload)
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(2 ** attempt)

def score_candidate(client, image_path):
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    payload = {
        "model": "gpt-4o",
        "response_format": {"type": "json_object"},
        "messages": [{"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
            {"type": "text", "text": f"""Analyze this medical image against the checklist:
{PSORIASIS_CHECKLIST}
Return a valid JSON object with key "scores" mapping to a list of exactly 7 binary values.
Example: {{"scores": [1, 0, 1, 0, 1, 0, 0]}}"""}
        ]}],
        "max_tokens": 100,
        "temperature": 0.0
    }
    try:
        response = call_openai_with_backoff(client, payload)
        parsed = json.loads(response.choices[0].message.content.strip())
        scores = parsed["scores"]
        assert len(scores) == 7
        return scores
    except:
        return [0,0,0,0,0,0,0]

def run_dpo_preparation_pipeline(num_candidates_per_image=3):
    from google.colab import userdata
    api_key = userdata.get('OPENAI_API_KEY')
    client = OpenAI(api_key=api_key)

    pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
        "runwayml/stable-diffusion-v1-5",
        torch_dtype=torch.float16,
        safety_checker=None
    ).to("cuda")
    pipe.load_lora_weights(LORA_PATH)
    print("✅ Pipeline ready")

    source_images = sorted(glob.glob(os.path.join(SOURCE_DIR, "*.jpg")))
    print(f"📂 {len(source_images)} source images found")

    target_prompt = (
        "A close-up clinical photograph of severe plaque psoriasis on dark brown skin. "
        "Dry heavy multi-layered ashy-white scale, raised well-demarcated plaques, "
        "thick scaly texture, clinical lighting."
    )
    negative_prompt = (
        "smooth skin, healthy skin, glossy, shiny, wet, pink skin, magenta, "
        "pus, infection, blurry, out of focus, cartoon, drawing"
    )

    scored_dataset = {}
    for idx, img_path in enumerate(tqdm(source_images, desc="Generating candidates")):
        base_name = Path(img_path).stem
        init_image = Image.open(img_path).convert("RGB").resize((512, 512))
        scored_dataset[base_name] = []
        for cand_idx in range(num_candidates_per_image):
            seed = 1000 + idx * 10 + cand_idx
            cand_filename = f"{base_name}_cand_{cand_idx}.jpg"
            cand_filepath = os.path.join(CANDIDATES_DIR, cand_filename)
            img = pipe(
                prompt=target_prompt,
                negative_prompt=negative_prompt,
                image=init_image,
                strength=0.45,
                guidance_scale=10.0,
                num_inference_steps=50,
                generator=torch.Generator("cuda").manual_seed(seed)
            ).images[0]
            img.save(cand_filepath)
            scores = score_candidate(client, cand_filepath)
            scored_dataset[base_name].append({
                "filepath": cand_filepath,
                "filename": cand_filename,
                "scores": scores,
                "total_score": sum(scores),
                "seed": seed
            })
            print(f"  {cand_filename}: {scores} = {sum(scores)}/7")

    with open(os.path.join(DPO_WORK_DIR, "raw_scoring_history.json"), "w") as f:
        json.dump(scored_dataset, f, indent=4)

    dpo_pairs = []
    pair_count = 0
    for base_name, candidates in scored_dataset.items():
        sorted_cands = sorted(candidates, key=lambda x: x["total_score"], reverse=True)
        best, worst = sorted_cands[0], sorted_cands[-1]
        if best["total_score"] > worst["total_score"]:
            pair_count += 1
            chosen_dest = os.path.join(FINAL_DATASET_DIR, f"pair_{pair_count:03d}_chosen.jpg")
            rejected_dest = os.path.join(FINAL_DATASET_DIR, f"pair_{pair_count:03d}_rejected.jpg")
            shutil.copy2(best["filepath"], chosen_dest)
            shutil.copy2(worst["filepath"], rejected_dest)
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

    metadata_path = os.path.join(FINAL_DATASET_DIR, "metadata.jsonl")
    with open(metadata_path, "w") as f:
        for entry in dpo_pairs:
            f.write(json.dumps(entry) + "\n")

    print(f"\n✅ Done! {pair_count} preference pairs saved to {FINAL_DATASET_DIR}")

if __name__ == "__main__":
    run_dpo_preparation_pipeline(num_candidates_per_image=3)
