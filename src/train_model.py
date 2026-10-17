import os
import torch
from datasets import load_dataset
from trl import SFTTrainer
from transformers import TrainingArguments
from unsloth import FastLanguageModel

def train_wayuunlingo_model():
    """
    Script de fine-tuning utilizando Unsloth (LoRA/QLoRA) para adaptar un modelo base
    multilingüe al par de traducción Español <-> Wayuunaiki.
    """
    max_seq_length = 2048
    dtype = None  # Auto detección (Float16 o Bfloat16)
    load_in_4bit = True  # Uso de QLoRA para reducir consumo de VRAM a < 10GB

    print("Cargando modelo base multilingüe con Unsloth...")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name = "unsloth/Qwen2.5-Coder-7B-Instruct",
        max_seq_length = max_seq_length,
        dtype = dtype,
        load_in_4bit = load_in_4bit,
    )

    # Configuración de LoRA en todos los módulos lineales para adaptación lingüística
    model = FastLanguageModel.get_peft_model(
        model,
        r = 16,  # Rango LoRA
        target_modules = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_alpha = 16,
        lora_dropout = 0,
        bias = "none",
        use_gradient_checkpointing = True,
        random_state = 3407,
    )

    # Cargar dataset de entrenamiento preparado
    dataset_path = "data/corpus_sample.json"
    if not os.path.exists(dataset_path):
        print(f"Archivo de dataset {dataset_path} no encontrado. Por favor coloca el corpus en la carpeta data/.")
        return

    dataset = load_dataset("json", data_files=dataset_path, split="train")

    def format_prompts(examples):
        texts = []
        for es, wy in zip(examples["spanish"], examples["wayuunaiki"]):
            text = f"<|im_start|>system\nEres un traductor experto entre español y Wayuunaiki.<|im_end|>\n<|im_start|>user\nTraduce al Wayuunaiki: {es}<|im_end|>\n<|im_start|>assistant\n{wy}<|im_end|>"
            texts.append(text)
        return { "text" : texts }

    dataset = dataset.map(format_prompts, batched = True)

    # Entrenamiento con SFTTrainer
    trainer = SFTTrainer(
        model = model,
        tokenizer = tokenizer,
        train_dataset = dataset,
        dataset_text_field = "text",
        max_seq_length = max_seq_length,
        dataset_num_proc = 2,
        packing = False,
        args = TrainingArguments(
            per_device_train_batch_size = 2,
            gradient_accumulation_steps = 4,
            warmup_steps = 5,
            max_steps = 60,
            learning_rate = 2e-4,
            fp16 = not torch.cuda.is_bf16_supported(),
            bf16 = torch.cuda.is_bf16_supported(),
            logging_steps = 1,
            optim = "adamw_8bit",
            weight_decay = 0.01,
            lr_scheduler_type = "linear",
            seed = 3407,
            output_dir = "outputs",
        ),
    )

    print("Iniciando entrenamiento / Fine-Tuning de Wayuunlingo...")
    trainer_stats = trainer.train()
    print("Entrenamiento completado exitosamente.")

    # Guardar modelo adaptado LoRA
    model.save_pretrained("wayuunlingo_lora_model")
    tokenizer.save_pretrained("wayuunlingo_lora_model")
    print("Modelo guardado en la carpeta wayuunlingo_lora_model/")

if __name__ == "__main__":
    train_wayuunlingo_model()
