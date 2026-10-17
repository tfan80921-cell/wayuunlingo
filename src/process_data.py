import json
import os

def load_translation_pairs(file_path):
    """
    Carga y estructura un archivo JSON con pares de traducción  
    Español <-> Wayuunaiki para entrenamiento de modelos de lenguaje.
    """
    if not os.path.exists(file_path):
        print(f"El archivo {file_path} no existe.")
        return []

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
      
    formatted_dataset = []
    for item in data:
        entry = {
            "instruction": "Traduce el siguiente texto de español a Wayuunaiki o viceversa.",
            "input": item.get("spanish"),
            "output": item.get("wayuunaiki")
        }
        formatted_dataset.append(entry)
          
    return formatted_dataset

if __name__ == "__main__":
    print("Iniciando pipeline de procesamiento de datos para Wayuunlingo...")
    sample_path = "data/corpus_sample.json"
    dataset = load_translation_pairs(sample_path)
    print(f"Total de pares cargados: {len(dataset)}")
    print(json.dumps(dataset, indent=2, ensure_ascii=False))
