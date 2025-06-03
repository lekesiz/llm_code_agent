#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module d'intégration avec Gemini Pro (Google) pour les suggestions avancées de refactoring.
Ce module est responsable des suggestions avancées et des idées d'amélioration du code.
"""

import os
import logging
import time
from google import genai
from .claude_agent import ClaudeAgent

logger = logging.getLogger('llm_code_agent.gemini_agent')

class GeminiAgent:
    """
    Agent de suggestions avancées de refactoring utilisant Gemini Pro de Google.
    En cas d'échec, utilise Claude comme fallback.
    """
    
    def __init__(self):
        """Initialise l'agent Gemini avec la configuration nécessaire."""
        self.api_key = os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            logger.error("Clé API Google non trouvée. Veuillez définir GOOGLE_API_KEY dans le fichier .env")
            raise ValueError("Clé API Google manquante")
        
        self.client = genai.Client(api_key=self.api_key)
        self.model = "gemini-2.0-flash"  # Güncel model adı
        self.claude_fallback = ClaudeAgent()  # Initialisation du fallback Claude
        logger.info(f"Agent Gemini initialisé avec le modèle {self.model}")
    
    def suggest_refactoring(self, code_content, claude_analysis, file_path):
        """
        Propose des suggestions avancées de refactoring et d'amélioration du code.
        En cas d'échec de Gemini, utilise Claude comme fallback.
        
        Args:
            code_content (str): Contenu du code à analyser
            claude_analysis (str): Analyse préalable réalisée par Claude
            file_path (str): Chemin du fichier analysé
            
        Returns:
            str: Rapport de suggestions avancées au format Markdown
        """
        file_name = os.path.basename(file_path)
        file_extension = os.path.splitext(file_name)[1].lower()
        
        logger.info(f"Génération de suggestions avancées pour {file_name} avec Gemini")
        
        # Détermination du langage de programmation
        language_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.tsx': 'TypeScript React',
            '.jsx': 'JavaScript React',
            '.html': 'HTML',
            '.css': 'CSS',
            '.json': 'JSON',
            '.md': 'Markdown'
        }
        
        language = language_map.get(file_extension, 'Code')
        
        # Construction du prompt pour Gemini
        prompt = f"""
# Suggestions avancées de refactoring pour {language}

Je vais te fournir le contenu d'un fichier {language} ainsi qu'une analyse préalable réalisée par Claude 3.
Ton rôle est de proposer des suggestions avancées de refactoring et d'amélioration du code.

## Fichier à analyser: `{file_name}`

## Instructions:

1. Propose des améliorations avancées pour:
   - Refactoriser le code pour une meilleure architecture
   - Améliorer la modularité et la réutilisabilité
   - Optimiser les performances
   - Moderniser le code avec les dernières pratiques et fonctionnalités du langage {language}

2. Pour chaque suggestion:
   - Explique clairement le bénéfice attendu
   - Fournis un exemple concret de code refactorisé
   - Indique le niveau d'effort requis (Faible, Moyen, Élevé)
   - Attribue une priorité (Critique, Élevée, Moyenne, Faible)

3. Propose également:
   - Des idées de nouvelles fonctionnalités pertinentes
   - Des améliorations d'architecture globale
   - Des suggestions pour améliorer la testabilité du code

## Format de sortie:
Ton analyse doit être structurée en sections claires avec des titres en Markdown.
Utilise des blocs de code pour illustrer tes suggestions.
Termine par une liste de tâches TODO au format JSON pour faciliter l'intégration.

## Voici le code à analyser:
```{language}
{code_content}
```

## Voici l'analyse préalable de Claude:
{claude_analysis[:1500]}... (analyse tronquée pour la longueur)

Merci de fournir des suggestions avancées et innovantes pour améliorer ce code.
"""

        # Appel à l'API Gemini
        max_retries = 3
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt
                )
                
                suggestions = response.text
                
                # Ajout d'un en-tête au rapport
                header = f"""# Suggestions avancées de refactoring pour {file_name} par Gemini Pro

*Ce rapport a été généré automatiquement par l'agent d'analyse de code multi-LLM.*

**Fichier analysé:** {file_path}  
**Date d'analyse:** {time.strftime('%Y-%m-%d %H:%M:%S')}  
**Modèle utilisé:** {self.model}

---

"""
                
                full_suggestions = header + suggestions
                
                logger.info(f"Suggestions avancées pour {file_name} générées avec succès")
                return full_suggestions
                
            except Exception as e:
                logger.warning(f"Tentative {attempt+1}/{max_retries} échouée: {str(e)}")
                if attempt < max_retries - 1:
                    logger.info(f"Nouvelle tentative dans {retry_delay} secondes...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Backoff exponentiel
                else:
                    logger.error(f"Échec de la génération de suggestions après {max_retries} tentatives")
                    logger.info("Utilisation de Claude comme fallback...")
                    
                    # Utilisation de Claude comme fallback
                    try:
                        fallback_prompt = f"""
                        En tant qu'expert en refactoring de code, analyse ce fichier {language} et propose des suggestions avancées d'amélioration.
                        Inclus des exemples de code, des niveaux d'effort et des priorités.
                        
                        Code à analyser:
                        ```{language}
                        {code_content}
                        ```
                        
                        Analyse préalable:
                        {claude_analysis[:1500]}... (analyse tronquée)
                        """
                        
                        fallback_suggestions = self.claude_fallback.analyze_code(fallback_prompt)
                        
                        header = f"""# Suggestions avancées de refactoring pour {file_name} par Claude (Fallback)

*Ce rapport a été généré automatiquement par l'agent d'analyse de code multi-LLM suite à un échec de Gemini.*

**Fichier analysé:** {file_path}  
**Date d'analyse:** {time.strftime('%Y-%m-%d %H:%M:%S')}  
**Modèle utilisé:** Claude (Fallback)

---

"""
                        
                        return header + fallback_suggestions
                        
                    except Exception as fallback_error:
                        logger.error(f"Échec du fallback avec Claude: {str(fallback_error)}")
                        return f"""# Erreur de génération de suggestions pour {file_name}

Une erreur s'est produite lors de la génération de suggestions avec Gemini Pro et le fallback Claude:

```
{str(e)}
```

Veuillez vérifier votre connexion internet et vos clés API, puis réessayer.
"""

    def extract_todos_from_suggestions(self, suggestions_content):
        """
        Extrait les tâches TODO à partir du rapport de suggestions.
        
        Args:
            suggestions_content (str): Contenu du rapport de suggestions
            
        Returns:
            list: Liste des tâches TODO avec leur priorité et niveau d'effort
        """
        todos = []
        
        # Recherche d'un bloc JSON contenant des TODOs
        import re
        json_pattern = r'```json\s*([\s\S]*?)\s*```'
        json_matches = re.findall(json_pattern, suggestions_content)
        
        if json_matches:
            for json_str in json_matches:
                try:
                    # Tentative de parsing du JSON
                    import json
                    todo_data = json.loads(json_str)
                    
                    # Si c'est une liste, on l'ajoute directement
                    if isinstance(todo_data, list):
                        todos.extend(todo_data)
                    # Si c'est un dictionnaire avec une clé "todos", on utilise cette liste
                    elif isinstance(todo_data, dict) and "todos" in todo_data:
                        todos.extend(todo_data["todos"])
                except json.JSONDecodeError:
                    logger.warning("Impossible de parser le JSON des TODOs")
        
        # Si aucun JSON n'est trouvé, on extrait les TODOs à partir du texte
        if not todos:
            # Analyse simple basée sur les titres et les mentions de priorité
            lines = suggestions_content.split('\n')
            current_todo = None
            
            for line in lines:
                # Détection des titres qui pourraient indiquer une tâche
                if line.startswith('##') and ('todo' in line.lower() or 'tâche' in line.lower() or 'amélioration' in line.lower()):
                    # Sauvegarder la tâche précédente si elle existe
                    if current_todo:
                        todos.append(current_todo)
                    
                    # Commencer une nouvelle tâche
                    current_todo = {
                        'description': line.lstrip('#').strip(),
                        'priority': 'Moyenne',
                        'effort': 'Moyen'
                    }
                
                # Détection de la priorité
                elif current_todo and ('priorité' in line.lower() or 'priority' in line.lower()):
                    if 'critique' in line.lower() or 'critical' in line.lower():
                        current_todo['priority'] = 'Critique'
                    elif 'élevée' in line.lower() or 'high' in line.lower():
                        current_todo['priority'] = 'Élevée'
                    elif 'moyenne' in line.lower() or 'medium' in line.lower():
                        current_todo['priority'] = 'Moyenne'
                    elif 'faible' in line.lower() or 'low' in line.lower():
                        current_todo['priority'] = 'Faible'
                
                # Détection du niveau d'effort
                elif current_todo and ('effort' in line.lower()):
                    if 'élevé' in line.lower() or 'high' in line.lower():
                        current_todo['effort'] = 'Élevé'
                    elif 'moyen' in line.lower() or 'medium' in line.lower():
                        current_todo['effort'] = 'Moyen'
                    elif 'faible' in line.lower() or 'low' in line.lower():
                        current_todo['effort'] = 'Faible'
            
            # Ajouter la dernière tâche si elle existe
            if current_todo:
                todos.append(current_todo)
        
        return todos

# Test unitaire simple si exécuté directement
if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    
    if len(sys.argv) > 1:
        test_file = sys.argv[1]
        
        if os.path.isfile(test_file):
            with open(test_file, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # Créer une analyse fictive de Claude pour le test
            mock_claude_analysis = f"# Analyse de {test_file}\n\nCe fichier présente quelques problèmes potentiels..."
            
            agent = GeminiAgent()
            suggestions = agent.suggest_refactoring(code, mock_claude_analysis, test_file)
            
            print(suggestions[:500] + "...\n[Suggestions tronquées pour l'affichage]")
        else:
            print(f"Le fichier {test_file} n'existe pas.")
    else:
        print("Usage: python gemini_agent.py <fichier_à_analyser>")
