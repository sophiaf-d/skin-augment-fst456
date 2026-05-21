# Enhanced DPO Checklists — FST IV–VI
## Derived from Dermatology Simplified (Lipoff & DaSilva, 2nd Ed.)

These replace the 5-criteria checklists from the MAGIC paper (Table 14).
Each criterion is written as a visually verifiable yes/no question for GPT-4o.
FST IV–VI specific features are explicitly called out.

---

## How to use

```python
PROMPT = """Evaluate the image against the following checklist for {condition}.
Return ONLY a Python list of binary values (1=criterion satisfied, 0=not satisfied).
Expected format: [1, 0, 1, 0, 0, 0, 0]"""
```

Score aggregation (from MAGIC Appendix A.2):
- Sum scores → total T
- If max(T1, T2) ≤ 2: both lose
- If min(T1, T2) = total criteria OR T1 = T2 > 2: both win
- Otherwise: higher score wins

---

## 1. Psoriasis

**MAGIC original (5 criteria):**
Location / Lesion type / Shape-size / Color / Texture

**Enhanced (7 criteria):**

1. **Location** — Are lesions present on typical psoriasis sites: elbows, knees, scalp, lower back, palms, or soles? (NOT primarily on face or flexures)
2. **Lesion type** — Are there well-demarcated plaques or papules with a clearly defined edge that separates them from surrounding normal skin?
3. **Scale character** — Is there thick, adherent, layered scale present on top of the plaque? (On FST IV–VI this scale may appear grayish-white or silvery-grey rather than bright silver)
4. **Plaque colour (FST-aware)** — Does the plaque base show red/pink on light skin OR purple/violet/dark brown on darker skin tones (FST IV–VI)?
5. **Scale removal sign** — Is there evidence of the Auspitz sign (pinpoint bleeding or darker pigmented spots visible when scale is removed or at scale edges)?
6. **Plaque morphology** — Are individual plaques discrete and clearly raised above the skin surface, not blending gradually into surrounding skin?
7. **Post-inflammatory change** — On darker skin, is there surrounding hyperpigmentation or a hypopigmented halo (Woronoff ring) around the plaque perimeter?

**Source notes:**
- "PASI based on redness, thickness, and scaliness" → thickness and scaliness are the most visually verifiable
- "Auspitz sign = lesions bleed when scale is removed, from thinned suprapapillary plates"
- "Woronoff ring = hypopigmented halo/ring around plaques"
- "Unlike atopic dermatitis, psoriasis plaques rarely impetiginized" — helps differentiation
- Scale on FST IV–VI appears grey/ash-white, not bright silver (confirmed by MAGIC Table 14: "purple/dark brown with grayish scales")

---

## 2. Lichen Planus

**MAGIC original (5 criteria):**
Location / Lesion feature / Shape-size / Color / Texture

**Enhanced (7 criteria):**

1. **Location** — Are lesions on typical LP sites: wrists, forearms, ankles, shins, or oral/genital mucosa?
2. **Morphology** — Are the lesions flat-topped papules (not dome-shaped, not vesicular)?
3. **Shape** — Are the papules polygonal (irregular-edged, not perfectly round or oval)?
4. **Colour (FST-aware)** — On light skin: violaceous/purple. On FST IV–VI (darker skin): are lesions grey-brown, dark brown, or showing post-inflammatory hyperpigmentation rather than purple?
5. **Wickham's striae** — Is there a fine white or grey lacy/reticulated pattern (streaks) visible on the surface of the papules?
6. **Surface** — Are the lesions shiny on top when the light catches them (glossy surface)?
7. **Koebner pattern** — Are lesions arranged in lines or clusters suggesting trauma-related distribution?

**Source notes:**
- "Classic Ps: pruritic, purple, polygonal, planar, papular"
- "Wickham's striae = white/grey streaks over LP lesions"
- "LP pigmentosus = a postinflammatory hyperpigmented form of LP" — especially relevant for FST IV–VI
- "LP actinicus = photosensitive variant presenting with annular, dyschromic, or violaceous plaques" — more common in darker skin
- On FST IV–VI, LP often appears grey-brown or hyperpigmented rather than purple

---

## 3. Vitiligo

**MAGIC original (5 criteria):**
Location / Lesion feature / Shape-size / Color / Texture

**Enhanced (6 criteria):**

1. **Depigmentation** — Are there patches of complete loss of skin colour (not just lightening, but absence of pigment)?
2. **Contrast** — Is there sharp, high-contrast border between the depigmented patch and surrounding normal skin? (Contrast is most striking on FST IV–VI)
3. **Location** — Are patches on typical vitiligo sites: around eyes, mouth, hands, feet, or other perioral/periorbital areas?
4. **Border sharpness** — Is the edge of the white patch well-defined rather than gradual or blending?
5. **Texture preservation** — Does the depigmented area have normal skin texture (no scaling, no thickening, no roughness) — only the colour is lost?
6. **Symmetry** — Are patches roughly symmetric or bilateral (appearing on corresponding body parts on both sides)?

**Source notes:**
- Vitiligo chapter: depigmented patches with well-defined borders
- "Normal skin texture (no scaling or thickening), only color is lost" — key differentiator from tinea versicolor
- On FST IV–VI the stark white-on-dark contrast is a defining visual feature and the highest-yield criterion for GPT-4o evaluation

---

## 4. Lupus Erythematosus

**MAGIC original (5 criteria):**
Location / Lesion feature / Shape-size / Color / Texture

**Enhanced (7 criteria):**

1. **Facial distribution** — Is there a rash across the cheeks and nasal bridge that spares the nasolabial folds (classic malar/butterfly pattern)?
2. **Lesion type** — Is the rash flat or slightly raised (macular or papular), not nodular or vesicular?
3. **Colour (FST-aware)** — On light skin: pink-red. On FST IV–VI: darker red, violaceous, or hyperpigmented patches on the face?
4. **Discoid features** — If discoid lesions present: are they coin-shaped (1–3 cm), with central scarring or atrophy and peripheral hyperpigmentation?
5. **Scale on discoid** — If discoid: is there a rough or scaly surface with keratotic plugging (carpet-tack sign — scale has spiky horny plugs on undersurface)?
6. **Photodistribution** — Are lesions predominantly on sun-exposed areas (face, V-neck, arms)?
7. **Post-inflammatory pigment** — On FST IV–VI: is there surrounding post-inflammatory hyperpigmentation or dyschromia (darker ring around active lesion)?

**Source notes:**
- "Malar erythema should involve the nasal bridge and spare the nasolabial folds"
- "Carpet tack sign = horny plugs on undersurface when scale removed" (DLE specific)
- "Early DLE lesions can appear psoriasiform" — helps avoid false positives
- Lupus on FST IV–VI more often presents with hyperpigmented discoid lesions than the classic bright-red butterfly rash

---

## 5. Sarcoidosis

**MAGIC original (5 criteria):**
Location / Lesion feature / Shape-size / Color / Texture

**Enhanced (6 criteria):**

1. **Lesion type** — Are there firm, indurated dermal papules or plaques (not superficial, feel embedded in dermis)?
2. **Colour (FST-aware)** — On light skin: red-brown or apple-jelly coloured. On FST IV–VI: are lesions hyperpigmented, violaceous-brown, or darker than surrounding skin?
3. **Location** — Are lesions on the face (especially nose, cheeks, ears = lupus pernio pattern), scars, or tattoo sites?
4. **Scar infiltration** — Are any existing scars or old wound sites involved (appearing raised, indurated, or darker)?
5. **Surface** — Is the surface of lesions smooth and without scale (as opposed to scaly psoriasiform lesions)?
6. **Diascopy response** — Is there an "apple jelly" or yellow-brown translucent colour visible when the lesion is pressed (blanching reveals brown-orange undertone)?

**Source notes:**
- "Granulomatous dermatoses tend to be red-brown/orange dermal plaques, 'apple-jelly' colored, which may be appreciated on diascopy"
- "Most common in African-Americans, highest incidence in Sweden" — highly relevant for FST IV–VI dataset
- "Lupus pernio affects coldest areas (nose, ears, cheeks)"
- "Infiltration of scars, injection sites, tattoos" — distinctive feature

---

## 6. Prurigo Nodularis

**MAGIC original (5 criteria):**
Location / Lesion feature / Shape-size / Color / Texture

**Enhanced (6 criteria):**

1. **Lesion type** — Are there firm, raised nodules (not flat macules, not vesicles)?
2. **Location** — Are lesions on reachable scratch sites: arms, legs, upper back, shoulders?
3. **Surface** — Does the top of each nodule show crusting, excoriation, or a scabbed surface (from chronic scratching)?
4. **Multiplicity** — Are there multiple nodules present rather than a single isolated lesion?
5. **Colour (FST-aware)** — On FST IV–VI: are nodules hyperpigmented (dark brown, black) or surrounded by post-inflammatory hyperpigmentation?
6. **Shape** — Are individual nodules round (1–3 cm) with a warty or hyperkeratotic surface texture?

**Source notes:**
- "Hyperkeratotic nodules with excoriations (sometimes just secondary changes from picking)"
- "Similar to lichen simplex chronicus, but nodular"
- On FST IV–VI, nodules are often deeply hyperpigmented (may appear nearly black) — this is the most distinguishing feature
- "May be a form of chronic eczema"

---

## 7. Pityriasis Rosea

**MAGIC original (5 criteria):**
Location / Lesion feature / Shape-size / Color / Texture

**Enhanced (6 criteria):**

1. **Herald patch** — Is there one larger oval patch (2–6 cm) that appears distinct from or precedes the smaller rash?
2. **Satellite lesions** — Are there multiple smaller oval patches (1–2 cm) distributed across the trunk?
3. **Distribution pattern** — Do the smaller lesions follow a "Christmas tree" pattern along skin cleavage lines on the back or trunk?
4. **Colour (FST-aware)** — On light skin: pink/salmon. On FST IV–VI: grey, brown, or violaceous oval patches?
5. **Scale pattern** — Is there a fine scale forming a "collarette" at the inner edge of each lesion (scale points inward, not covering the whole surface)?
6. **Body area** — Are lesions primarily on the trunk/torso (NOT predominantly on face, hands, or feet)?

**Source notes:**
- "Herald patch precedes eruption"; "Tends to be in body folds, Christmas tree distribution"
- "Variant: inverse PR (involves face, axillae, inguinal areas) — may be more common in darker skin types" — important to capture both presentations
- "Trailing scale: occurs in pityriasis rosea" (collarette scale pointing inward)
- On FST IV–VI: grey/brown/hyperpigmented ovoid patches; the collarette scale is the most reliable visual criterion

---

## 8. Keloid

**MAGIC original (5 criteria):**
Location / Lesion feature / Shape-size / Color / Texture

**Enhanced (6 criteria):**

1. **Boundary** — Does the raised scar tissue extend beyond the original wound boundary (not confined to the wound site like a hypertrophic scar)?
2. **Surface** — Is the surface smooth, shiny, and hairless?
3. **Texture** — Does the lesion appear firm and rubbery in texture?
4. **Colour (FST-aware)** — On light skin: pink or red. On FST IV–VI: dark brown, purple, or hyperpigmented above surrounding skin tone?
5. **Location** — Is the lesion on a typical keloid site: chest, shoulders, earlobes, jawline, or a former wound/scar area?
6. **Shape** — Does the keloid extend irregularly beyond the wound outline with a raised, irregular border (not neatly rounded)?

**Source notes:**
- "Overgrows wound edge (beyond original site of injury), like a neoplasm"
- "Path: disordered collagen bundles... pink keloidal collagen"
- "TGF-β may induce"
- Keloids are significantly more common in FST IV–VI patients — a critical condition for this dataset
- On dark skin, keloids are often hyperpigmented (darker than surrounding skin) and may appear brown-purple

---

## 9. Melanoma

**MAGIC original (5 criteria):**
Location / Lesion feature / Shape-size / Color / Texture

**Enhanced (7 criteria):**

1. **Asymmetry** — Is the lesion asymmetric (one half does not mirror the other)?
2. **Border** — Is the border irregular, notched, scalloped, or poorly defined?
3. **Colour variation** — Are there multiple shades within the same lesion (brown, black, red, white, or blue)?
4. **Size indicator** — Does the lesion appear larger than a pencil eraser (>6 mm) or show signs of recent growth?
5. **Acral location (FST-aware)** — On FST IV–VI: is the lesion located on the palm, sole, or under/around the nail (acral lentiginous subtype is the predominant form in darker skin)?
6. **Colour on dark skin** — On FST IV–VI: is the lesion very dark brown or black with colour variation, possibly with a lighter irregular zone?
7. **Surface change** — Is there any ulceration, bleeding, crusting, or nodular elevation within the lesion?

**Source notes:**
- "Acral lentiginous: 5–10%; noted in darker skin patients, not because of increased incidence, but all other types have decreased incidence [in darker skin]"
- "Amelanotic [melanoma] may have worse prognosis, also often with delays in diagnosis" — more common on darker skin
- ABCDE criteria (asymmetry, border, colour, diameter, evolution) are the standard framework
- Key FST IV–VI adaptation: shift location emphasis to palms/soles/nails

---

## Summary: Criteria Counts by Condition

| Condition | MAGIC criteria | Enhanced criteria | Key FST IV–VI additions |
|-----------|---------------|-------------------|------------------------|
| Psoriasis | 5 | 7 | Auspitz sign, Woronoff ring, grayish scale on dark skin |
| Lichen Planus | 5 | 7 | Hyperpigmented LP pigmentosus, LP actinicus |
| Vitiligo | 5 | 6 | High contrast on dark skin, symmetry |
| Lupus | 5 | 7 | Carpet-tack sign, discoid hyperpigmentation |
| Sarcoidosis | 5 | 6 | Apple-jelly diascopy, scar infiltration |
| Prurigo Nodularis | 5 | 6 | Deep hyperpigmentation on dark skin |
| Pityriasis Rosea | 5 | 6 | Inverse PR variant, grey/brown colour on dark skin |
| Keloid | 5 | 6 | Hyperpigmented surface on dark skin |
| Melanoma | 5 | 7 | Acral lentiginous emphasis, amelanotic variant |

---

## Notes on Score Aggregation for Variable Criteria Counts

Since these checklists have 6–7 criteria instead of 5, update the MAGIC aggregation threshold:

```python
def score_to_outcome(s1: list, s2: list, threshold_ratio: float = 0.4) -> str:
    n = len(s1)  # total criteria (6 or 7)
    t1, t2 = sum(s1), sum(s2)
    low = int(n * threshold_ratio)   # e.g. 2 for 6-criteria, 3 for 7-criteria
    if max(t1, t2) <= low:
        return "both_lose"
    if min(t1, t2) == n or (t1 == t2 and t1 > low):
        return "both_win"
    return "win_0" if t1 > t2 else "win_1"
```
