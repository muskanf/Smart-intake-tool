#!/usr/bin/env python3
"""
Fine-tune microsoft/trocr-small-handwritten on master_labels.csv.
Logs one line every 50 steps and saves weights to
ocr_training/trocr-prescription-ft/.
"""
import torch, pathlib, pandas as pd
from datasets import Dataset, Features, Image, Value
from transformers import (TrOCRProcessor, VisionEncoderDecoderModel,
                          TrainingArguments, Trainer)

ROOT = pathlib.Path(__file__).resolve().parents[1]
CSV  = ROOT / "data/handwritten_rx/master_labels.csv"
OUT  = ROOT / "trocr-prescription-ft"

print("Loading CSV:", CSV)
df = pd.read_csv(CSV)
print("Rows:", len(df))

features = Features({"image": Image(), "text": Value("string")})
ds = Dataset.from_pandas(df, features=features).shuffle(seed=42)

proc  = TrOCRProcessor.from_pretrained("microsoft/trocr-small-handwritten")
model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-small-handwritten")

def preprocess(batch):
    batch["pixel_values"] = proc(
        images=[img.convert("RGB") for img in batch["image"]],
        return_tensors="pt"
    ).pixel_values.squeeze(1)
    batch["labels"] = proc.tokenizer(
        batch["text"], padding="max_length", truncation=True
    ).input_ids
    return batch

ds = ds.map(preprocess, remove_columns=["image", "text"], batched=True, batch_size=16)

def collate(batch):
    return {
        "pixel_values": torch.stack([b["pixel_values"] for b in batch]),
        "labels":       torch.tensor([b["labels"] for b in batch])
    }

args = TrainingArguments(
    output_dir=str(OUT),
    per_device_train_batch_size=8,
    num_train_epochs=5,
    logging_steps=50,
    save_strategy="epoch",
    fp16=torch.cuda.is_available(),
)

trainer = Trainer(model=model, args=args, train_dataset=ds, data_collator=collate)
trainer.train()
trainer.save_model(str(OUT))
proc.save_pretrained(str(OUT))
print("✅  Weights saved to", OUT)
