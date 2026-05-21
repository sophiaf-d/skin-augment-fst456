# skin-augment-fst456

Synthetic skin disease image augmentation for Fitzpatrick skin types IV–VI.

## Pipeline
1. Textual Inversion + LoRA fine-tuning (skin-diff)
2. Image-to-image generation
3. GPT-4o checklist scoring (MAGIC)
4. DPO fine-tuning

## Dataset
Fitzpatrick17k subset — FST IV, V, VI only.

## References
- skin-diff: https://github.com/janet-sw/skin-diff
- MAGIC: https://arxiv.org/abs/2506.12323
