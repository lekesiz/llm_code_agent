#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module d'intégration avec Gemini Pro (Google) pour les suggestions avancées de refactoring.
Ce module est responsable des suggestions avancées et des idées d'amélioration du code.
"""

import os
import logging
import time
import json
import re
from typing import List, Dict, Optional
from google import genai
from .claude_agent import ClaudeAgent

logger = logging.getLogger('llm_code_agent.gemini_agent')

# Constants
LANGUAGE_MAP = {
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

MAX_RETRIES = 3
INITIAL_RETRY_DELAY = 5

class GeminiAgent:
    """
    Agent de suggestions avancées de refactoring utilisant Gemini Pro de Google.
    En cas d'échec, utilise Claude comme fallback.
    """
    
    def __init__(self):
        """Initialise l'agent Gemini avec la configuration nécessaire."""
        self.api_key = self._get_api_key()
        self.client = genai.Client(api_key=self.api_key)
        self.model = "gemini-pro"
        self.claude_fallback = ClaudeAgent()
        logger.info(f"Agent Gemini initialisé avec le modèle {self.model}")
    
    def _get_api_key(self) -> str:
        """Récupère et valide la clé API Google."""
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            logger.error("Clé API Google non trouvée. Veuillez définir GOOGLE_API_KEY dans le fichier .env")
            raise ValueError("Clé API Google manquante")
        return api_key

    def _get_language(self, file_extension: str) -> str:
        """Détermine le langage de programmation à partir de l'extension du fichier."""
        return LANGUAGE_MAP.get(file_extension.lower(), 'Code')

    def _build_prompt(self, code_content: str, claude_analysis: str, file_name: str, language: str) -> str:
        """Construit le prompt pour l'analyse de code."""
        return f"""
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

    def _handle_api_error(self, error: Exception, attempt: int, max_retries: int, retry_delay: int) -> None:
        """Gère les erreurs d'API et les tentatives de retry."""
        logger.warning(f"Tentative {attempt+1}/{max_retries} échouée: {str(error)}")
        if attempt < max_retries - 1:
            logger.info(f"Nouvelle tentative dans {retry_delay} secondes...")
            time.sleep(retry_delay)
        else:
            logger.error(f"Échec de la génération de suggestions après {max_retries} tentatives")

    def _generate_with_gemini(self, prompt: str) -> Optional[str]:
        """Génère des suggestions avec Gemini Pro."""
        for attempt in range(MAX_RETRIES):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt
                )
                return response.text
            except Exception as e:
                retry_delay = INITIAL_RETRY_DELAY * (2 ** attempt)
                self._handle_api_error(e, attempt, MAX_RETRIES, retry_delay)
        return None

    def _generate_with_claude(self, prompt: str, file_path: str) -> str:
        """Génère des suggestions avec Claude en tant que fallback."""
        try:
            return self.claude_fallback.analyze_code(prompt, file_path)
        except Exception as e:
            logger.error(f"Échec du fallback avec Claude: {str(e)}")
            raise

    def _create_report_header(self, file_name: str, file_path: str, model: str) -> str:
        """Crée l'en-tête du rapport d'analyse."""
        return f"""# Suggestions avancées de refactoring pour {file_name} par {model}

*Ce rapport a été généré automatiquement par l'agent d'analyse de code multi-LLM.*

**Fichier analysé:** {file_path}  
**Date d'analyse:** {time.strftime('%Y-%m-%d %H:%M:%S')}  
**Modèle utilisé:** {model}

---

"""

    def suggest_refactoring(self, code_content: str, claude_analysis: str, file_path: str) -> str:
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
        file_extension = os.path.splitext(file_name)[1]
        language = self._get_language(file_extension)
        
        logger.info(f"Génération de suggestions avancées pour {file_name} avec Gemini")
        
        prompt = self._build_prompt(code_content, claude_analysis, file_name, language)
        suggestions = self._generate_with_gemini(prompt)
        
        if suggestions:
            header = self._create_report_header(file_name, file_path, self.model)
            return header + suggestions
        
        logger.info("Utilisation de Claude comme fallback...")
        try:
            fallback_suggestions = self._generate_with_claude(prompt, file_path)
            header = self._create_report_header(file_name, file_path, "Claude (Fallback)")
            return header + fallback_suggestions
        except Exception as e:
            return f"""# Erreur de génération de suggestions pour {file_name}

Une erreur s'est produite lors de la génération de suggestions avec Gemini Pro et le fallback Claude:

```
{str(e)}
```

Veuillez vérifier votre connexion internet et vos clés API, puis réessayer.
"""

    def extract_todos_from_suggestions(self, suggestions_content: str) -> List[Dict]:
        """
        Extrait les tâches TODO à partir du rapport de suggestions.
        
        Args:
            suggestions_content (str): Contenu du rapport de suggestions
            
        Returns:
            list: Liste des tâches TODO avec leur priorité et niveau d'effort
        """
        todos = []
        
        # Extraction depuis JSON
        json_todos = self._extract_todos_from_json(suggestions_content)
        if json_todos:
            todos.extend(json_todos)
            return todos
        
        # Extraction depuis texte
        text_todos = self._extract_todos_from_text(suggestions_content)
        todos.extend(text_todos)
        
        return todos

    def _extract_todos_from_json(self, content: str) -> List[Dict]:
        """Extrait les TODOs depuis un bloc JSON."""
        json_pattern = r'```json\s*([\s\S]*?)\s*```'
        json_matches = re.findall(json_pattern, content)
        
        todos = []
        for json_str in json_matches:
            try:
                todo_data = json.loads(json_str)
                if isinstance(todo_data, list):
                    todos.extend(todo_data)
                elif isinstance(todo_data, dict) and "todos" in todo_data:
                    todos.extend(todo_data["todos"])
            except json.JSONDecodeError:
                logger.warning("Impossible de parser le JSON des TODOs")
        
        return todos

    def _extract_todos_from_text(self, content: str) -> List[Dict]:
        """Extrait les TODOs depuis le texte du rapport."""
        todos = []
        lines = content.split('\n')
        current_todo = None
        
        for line in lines:
            if self._is_todo_title(line):
                if current_todo:
                    todos.append(current_todo)
                current_todo = self._create_todo_from_title(line)
            elif current_todo:
                self._update_todo_priority(current_todo, line)
                self._update_todo_effort(current_todo, line)
        
        if current_todo:
            todos.append(current_todo)
        
        return todos

    def _is_todo_title(self, line: str) -> bool:
        """Vérifie si une ligne est un titre de TODO."""
        return (line.startswith('##') and 
                any(keyword in line.lower() for keyword in ['todo', 'tâche', 'amélioration']))

    def _create_todo_from_title(self, title: str) -> Dict:
        """Crée un nouveau TODO à partir d'un titre."""
        return {
            'description': title.lstrip('#').strip(),
            'priority': 'Moyenne',
            'effort': 'Moyen'
        }

    def _update_todo_priority(self, todo: Dict, line: str) -> None:
        """Met à jour la priorité d'un TODO."""
        line_lower = line.lower()
        if 'priorité' in line_lower or 'priority' in line_lower:
            if 'critique' in line_lower or 'critical' in line_lower:
                todo['priority'] = 'Critique'
            elif 'élevée' in line_lower or 'high' in line_lower:
                todo['priority'] = 'Élevée'
            elif 'moyenne' in line_lower or 'medium' in line_lower:
                todo['priority'] = 'Moyenne'
            elif 'faible' in line_lower or 'low' in line_lower:
                todo['priority'] = 'Faible'

    def _update_todo_effort(self, todo: Dict, line: str) -> None:
        """Met à jour le niveau d'effort d'un TODO."""
        line_lower = line.lower()
        if 'effort' in line_lower:
            if 'élevé' in line_lower or 'high' in line_lower:
                todo['effort'] = 'Élevé'
            elif 'moyen' in line_lower or 'medium' in line_lower:
                todo['effort'] = 'Moyen'
            elif 'faible' in line_lower or 'low' in line_lower:
                todo['effort'] = 'Faible'

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
