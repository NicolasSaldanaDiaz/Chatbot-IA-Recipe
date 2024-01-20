from django.shortcuts import render
import json
from django.http import HttpResponse
import spacy

# Create your views here.
nlp = spacy.load("es_core_news_lg")

TRAINING_FILE = 'training.json'

def load_recetas(file_path: str) -> dict:
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def save_recetas(file_path: str, data: dict):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

""" def find_best_match(user_question: str, questions: list[str]) -> str:
    best_match = None
    best_score = 0
    
    user_question_doc = nlp(user_question.lower())  # Convertir a minúsculas para comparación insensible a mayúsculas
    
    for question in questions:
        question_doc = nlp(question.lower())  # Convertir a minúsculas para comparación insensible a mayúsculas
        similarity_score = user_question_doc.similarity(question_doc)
        
        if similarity_score > best_score:
            best_match = question
            best_score = similarity_score
    
    return best_match if best_score >= 0.6 else None """
def find_best_match(user_question: str, questions: list[str]) -> str:
    best_match = None
    best_score = 0

    user_question_doc = nlp(user_question.lower())  # Convertir a minúsculas para comparación insensible a mayúsculas
    
    for question in questions:
        question_doc = nlp(question.lower())  # Convertir a minúsculas para comparación insensible a mayúsculas
        #print(f"User question tokens: {[token.text for token in user_question_doc]}")
        #print(f"Current question tokens: {[token.text for token in question_doc]}")
        # Verificar si alguna palabra clave está presente en la pregunta del usuario
        keyword_match = any(keyword.text.lower() in user_question_doc.text for keyword in question_doc)
        #print(f"Keyword match: {keyword_match}")
        # Calcular la similitud solo si hay una coincidencia de palabra clave y ambos documentos tienen contenido
        if keyword_match and user_question_doc.has_vector and question_doc.has_vector:
            similarity_score = user_question_doc.similarity(question_doc)
           # print(f"Similarity score: {similarity_score}")
            if similarity_score > best_score:
                best_match = question
                best_score = similarity_score
    
    return best_match if best_score >= 0.4 else None

def get_answer_for_question(question: str, knowledge_base: dict) -> str:
    # Buscar mejor coincidencia en el JSON
    best_match_json = find_best_match(question, [q["question"] for q in knowledge_base["questions"]])
    
    # Obtener respuestas del JSON
    if best_match_json:
        for q in knowledge_base["questions"]:
            if q["question"] == best_match_json:
                return q["answer"]

    return "No se encontró una respuesta. ¿Quieres entrenarme?"

def chat_bot_view(request):
    if request.method == 'POST':
        user_input = request.POST.get('userMessage', '')
        knowledge_base = load_recetas(TRAINING_FILE)

        # Obtener todas las preguntas del JSON
        json_questions = [q["question"] for q in knowledge_base["questions"]]

        # Método ajustado
        best_match = find_best_match(user_input, json_questions)

        if best_match:
            # La mejor coincidencia está en el JSON
            answer = get_answer_for_question(best_match, knowledge_base)
        else:
            answer = "No se encontró una respuesta. ¿Quieres entrenarme?"
            new_answer_confirmation = request.POST.get('newAnswerConfirmation', '')

            if new_answer_confirmation == 'Si':
                new_answer = request.POST.get('newAnswer', '')

                if new_answer:
                    # Añade la nueva pregunta y respuesta al JSON
                    knowledge_base["questions"].append({"question": user_input, "answer": new_answer})
                    save_recetas(TRAINING_FILE, knowledge_base)
                    answer = 'Gracias, aprendí una nueva respuesta.'
                else:
                    # Si no se proporciona una nueva respuesta, guarda la pregunta original
                    knowledge_base["questions"].append({"question": user_input, "answer": ""})
                    save_recetas(TRAINING_FILE, knowledge_base)

        return HttpResponse(answer)

def index(request):
    return render(request,'index.html')
