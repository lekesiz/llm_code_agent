#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module d'intégration avec GPT-4/GPT-4o (OpenAI) pour la validation et les suggestions de code.
Ce module est responsable de la validation du code et des suggestions d'amélioration.
"""

import os
import logging
import time
import json
from openai import OpenAI

logger = logging.getLogger('llm_code_agent.chatgpt_agent')

class ChatGPTAgent:
    """
    Agent de validation et de suggestion de code utilisant GPT-4/GPT-4o d'OpenAI.
    """
    
    def __init__(self):
        """Initialise l'agent ChatGPT avec la configuration nécessaire."""
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            logger.error("Clé API OpenAI non trouvée. Veuillez définir OPENAI_API_KEY dans le fichier .env")
            raise ValueError("Clé API OpenAI manquante")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4o"  # Utilisation de GPT-4o par défaut, peut être modifié selon disponibilité
        logger.info(f"Agent ChatGPT initialisé avec le modèle {self.model}")
    
    async def analyze_code(self, code_content: str, claude_analysis: str, file_path: str) -> str:
        """
        Valide le code et propose des suggestions d'amélioration en s'appuyant sur l'analyse de Claude.
        
        Args:
            code_content (str): Contenu du code à analyser
            claude_analysis (str): Analyse préalable réalisée par Claude
            file_path (str): Chemin du fichier analysé
            
        Returns:
            str: Rapport de validation et suggestions au format Markdown
        """
        file_name = os.path.basename(file_path)
        file_extension = os.path.splitext(file_name)[1].lower()
        
        logger.info(f"Validation du fichier {file_name} avec ChatGPT")
        
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
        
        # Construction du prompt pour ChatGPT
        prompt = f"""
# Validation et suggestions de code {language}

Je vais te fournir le contenu d'un fichier {language} ainsi qu'une analyse préalable réalisée par Claude 3.
Ton rôle est de valider cette analyse, d'identifier d'éventuels problèmes supplémentaires et de proposer des solutions concrètes.

## Fichier à analyser: `{file_name}`

## Instructions:

1. Examine le code et l'analyse de Claude pour:
   - Valider ou corriger les problèmes identifiés par Claude
   - Identifier des problèmes supplémentaires que Claude aurait pu manquer
   - Proposer des solutions concrètes et des exemples de code pour résoudre ces problèmes

2. Concentre-toi particulièrement sur:
   - La correction des bugs et erreurs
   - L'amélioration de la structure et de la lisibilité du code
   - L'optimisation des performances
   - Le respect des bonnes pratiques spécifiques au langage {language}

3. Pour chaque problème identifié:
   - Explique clairement pourquoi c'est un problème
   - Propose une solution concrète avec un exemple de code
   - Indique le niveau de priorité (Critique, Élevé, Moyen, Faible)

## Format de sortie:
Ton analyse doit être structurée en sections claires avec des titres en Markdown.
Utilise des blocs de code pour illustrer tes suggestions.

## Voici le code à analyser:
```{language}
{code_content}
```

## Voici l'analyse préalable de Claude:
{claude_analysis[:2000]}... (analyse tronquée pour la longueur)

Merci de fournir une validation et des suggestions détaillées et concrètes.
"""

        # Appel à l'API OpenAI
        max_retries = 3
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    max_tokens=4000,
                    temperature=0.2,
                    messages=[
                        {"role": "system", "content": "Tu es un expert en développement logiciel spécialisé dans la validation de code et les suggestions d'amélioration. Tu fournis des analyses précises et des solutions concrètes avec des exemples de code."},
                        {"role": "user", "content": prompt}
                    ]
                )
                
                review = response.choices[0].message.content
                
                # Ajout d'un en-tête au rapport
                header = f"""# Validation et suggestions pour {file_name} par ChatGPT

*Ce rapport a été généré automatiquement par l'agent d'analyse de code multi-LLM.*

**Fichier analysé:** {file_path}  
**Date d'analyse:** {time.strftime('%Y-%m-%d %H:%M:%S')}  
**Modèle utilisé:** {self.model}

---

"""
                
                full_review = header + review
                
                logger.info(f"Validation de {file_name} terminée avec succès")
                return full_review
                
            except Exception as e:
                logger.warning(f"Tentative {attempt+1}/{max_retries} échouée: {str(e)}")
                if attempt < max_retries - 1:
                    logger.info(f"Nouvelle tentative dans {retry_delay} secondes...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Backoff exponentiel
                else:
                    logger.error(f"Échec de la validation après {max_retries} tentatives")
                    return f"""# Erreur de validation pour {file_name}

Une erreur s'est produite lors de la validation de ce fichier avec ChatGPT:

```
{str(e)}
```

Veuillez vérifier votre connexion internet et votre clé API, puis réessayer.
"""

    def extract_code_suggestions(self, review_content):
        """
        Extrait les suggestions de code concrètes à partir du rapport de validation.
        
        Args:
            review_content (str): Contenu du rapport de validation
            
        Returns:
            list: Liste des suggestions de code avec leur priorité
        """
        suggestions = []
        
        # Analyse simple basée sur les titres et les blocs de code
        lines = review_content.split('\n')
        current_suggestion = None
        current_priority = "Moyen"  # Priorité par défaut
        
        for line in lines:
            # Détection des titres qui pourraient indiquer une suggestion
            if line.startswith('##') and ('suggestion' in line.lower() or 'problème' in line.lower() or 'amélioration' in line.lower()):
                # Sauvegarder la suggestion précédente si elle existe
                if current_suggestion:
                    suggestions.append({
                        'description': current_suggestion['title'],
                        'code': current_suggestion['code'],
                        'priority': current_priority
                    })
                
                # Commencer une nouvelle suggestion
                current_suggestion = {
                    'title': line.lstrip('#').strip(),
                    'code': ''
                }
                
            # Détection de la priorité
            elif current_suggestion and ('priorité' in line.lower() or 'priority' in line.lower()):
                if 'critique' in line.lower() or 'critical' in line.lower():
                    current_priority = "Critique"
                elif 'élevé' in line.lower() or 'high' in line.lower():
                    current_priority = "Élevé"
                elif 'moyen' in line.lower() or 'medium' in line.lower():
                    current_priority = "Moyen"
                elif 'faible' in line.lower() or 'low' in line.lower():
                    current_priority = "Faible"
            
            # Capture des blocs de code
            elif current_suggestion and line.startswith('```'):
                in_code_block = not in_code_block if 'in_code_block' in locals() else True
                if not in_code_block and current_suggestion['code']:
                    current_suggestion['code'] = current_suggestion['code'].strip()
            
            # Ajout du contenu au bloc de code
            elif current_suggestion and 'in_code_block' in locals() and in_code_block:
                current_suggestion['code'] += line + '\n'
        
        # Ajouter la dernière suggestion si elle existe
        if current_suggestion and current_suggestion['code']:
            suggestions.append({
                'description': current_suggestion['title'],
                'code': current_suggestion['code'].strip(),
                'priority': current_priority
            })
        
        return suggestions

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
            
            agent = ChatGPTAgent()
            review = agent.analyze_code(code, mock_claude_analysis, test_file)
            
            print(review[:500] + "...\n[Validation tronquée pour l'affichage]")
        else:
            print(f"Le fichier {test_file} n'existe pas.")
    else:
        print("Usage: python chatgpt_agent.py <fichier_à_analyser>")
