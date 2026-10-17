import json
import os
import evaluate

def run_evaluation_pipeline(predictions_file, references_file):
    """
    Pipeline de validación estadística y evaluación de calidad para Wayuunlingo.
    Calcula chrF++ (métrica clave para lenguas aglutinantes), BLEU a nivel de subpalabras
    y guarda un informe estructurado.
    """
    if not os.path.exists(predictions_file) or not os.path.exists(references_file):
        print("Archivos de evaluación no encontrados.")
        return

    with open(predictions_file, 'r', encoding='utf-8') as f:
        preds = json.load(f)

    with open(references_file, 'r', encoding='utf-8') as f:
        refs = json.load(f)

    # Cargar métricas de Hugging Face evaluate / sacrebleu
    chrf = evaluate.load("chrf")
    bleu = evaluate.load("bleu")

    # Métrica chrF++ (character n-gram F-score con word n-grams)
    chrf_result = chrf.compute(predictions=preds, references=[[r] for r in refs], word_order=2)
      
    # Métrica BLEU
    bleu_result = bleu.compute(predictions=preds, references=[[r] for r in refs])

    report = {
        "metrics": {
            "chrF++": round(chrf_result["score"], 2),
            "BLEU": round(bleu_result["bleu"] * 100, 2)
        },
        "samples_evaluated": len(preds)
    }

    print("=== INFORME DE EVALUACIÓN ESTADÍSTICA DE WAYUUNLINGO ===")
    print(json.dumps(report, indent=2, ensure_ascii=False))

    with open("evaluation_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    # Archivos de prueba
    preds_sample = ["Kee'iree sünainjee, ¿jamüsa kasa?", "Waneepia shia süpüshua'a"]
    refs_sample = ["Kee'iree sünainjee, ¿jamüsa kasa?", "Waneepia shia süpüshua'a"]

    with open("preds_temp.json", "w", encoding="utf-8") as f:
        json.dump(preds_sample, f, ensure_ascii=False)

    with open("refs_temp.json", "w", encoding="utf-8") as f:
        json.dump(refs_sample, f, ensure_ascii=False)

    run_evaluation_pipeline("preds_temp.json", "refs_temp.json")
