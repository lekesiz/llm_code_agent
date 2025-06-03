#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module d'intégration avec Claude 3 (Anthropic) pour l'analyse de code.
Ce module est responsable de l'analyse initiale du code source.
"""

import os
import logging
import time
from anthropic import Anthropic

logger = logging.getLogger('llm_code_agent.claude_agent')

class ClaudeAgent:
    """
    Agent d'analyse de code utilisant Claude 3 d'Anthropic.
    """
    
    def __init__(self):
        """Initialise l'agent Claude avec la configuration nécessaire."""
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            logger.error("Clé API Anthropic non trouvée. Veuillez définir ANTHROPIC_API_KEY dans le fichier .env")
            raise ValueError("Clé API Anthropic manquante")
        
        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-3-opus-20240229"
        logger.info(f"Agent Claude initialisé avec le modèle {self.model}")
    
    def analyze_code(self, code_content, file_path):
        """
        Analyse le code source avec Claude 3 et génère un rapport d'analyse.
        
        Args:
            code_content (str): Contenu du code à analyser
            file_path (str): Chemin du fichier analysé
            
        Returns:
            str: Rapport d'analyse au format Markdown
        """
        file_name = os.path.basename(file_path)
        file_extension = os.path.splitext(file_name)[1].lower()
        
        logger.info(f"Analyse du fichier {file_name} avec Claude")
        
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
        
        # Construction du prompt pour Claude
        prompt = f"""
# Analyse de code {language}

Je vais te fournir le contenu d'un fichier {language} et j'aimerais que tu l'analyses en profondeur. 
Voici le fichier à analyser: `{file_name}`

## Instructions d'analyse:

1. Analyse le code ligne par ligne pour identifier:
   - Erreurs de syntaxe ou bugs potentiels
   - Problèmes de sécurité ou vulnérabilités
   - Mauvaises pratiques ou anti-patterns
   - Code redondant ou inefficace
   - Problèmes de lisibilité ou de maintenabilité
   - Commentaires manquants ou insuffisants

2. Évalue la qualité globale du code:
   - Structure et organisation
   - Respect des conventions de nommage
   - Modularité et réutilisabilité
   - Gestion des erreurs et exceptions
   - Performance et optimisation

3. Fournis des suggestions d'amélioration concrètes:
   - Refactoring pour améliorer la lisibilité
   - Optimisations pour la performance
   - Corrections pour les bugs identifiés
   - Améliorations de sécurité

4. Identifie les tâches TODO spécifiques:
   - Liste les actions prioritaires à entreprendre
   - Attribue un niveau de priorité (Critique, Élevé, Moyen, Faible)
   - Explique brièvement pourquoi chaque tâche est importante

## Format de sortie:
Ton analyse doit être structurée en sections claires avec des titres en Markdown.

## Voici le code à analyser:
```{language}
{code_content}
```

Merci de fournir une analyse détaillée et constructive.
"""

        # Appel à l'API Claude
        max_retries = 3
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=4000,
                    temperature=0.1,
                    system="Tu es un expert en analyse de code et en bonnes pratiques de programmation. Tu fournis des analyses détaillées, précises et constructives.",
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                
                analysis = response.content[0].text
                
                # Ajout d'un en-tête au rapport
                header = f"""# Analyse de {file_name} par Claude 3

*Ce rapport a été généré automatiquement par l'agent d'analyse de code multi-LLM.*

**Fichier analysé:** {file_path}  
**Date d'analyse:** {time.strftime('%Y-%m-%d %H:%M:%S')}  
**Modèle utilisé:** {self.model}

---

"""
                
                full_analysis = header + analysis
                
                logger.info(f"Analyse de {file_name} terminée avec succès")
                return full_analysis
                
            except Exception as e:
                logger.warning(f"Tentative {attempt+1}/{max_retries} échouée: {str(e)}")
                if attempt < max_retries - 1:
                    logger.info(f"Nouvelle tentative dans {retry_delay} secondes...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Backoff exponentiel
                else:
                    logger.error(f"Échec de l'analyse après {max_retries} tentatives")
                    return f"""# Erreur d'analyse pour {file_name}

Une erreur s'est produite lors de l'analyse de ce fichier avec Claude 3:

```
{str(e)}
```

Veuillez vérifier votre connexion internet et votre clé API, puis réessayer.
"""

# Test unitaire simple si exécuté directement
if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    
    if len(sys.argv) > 1:
        test_file = sys.argv[1]
        
        if os.path.isfile(test_file):
            with open(test_file, 'r', encoding='utf-8') as f:
                code = f.read()
            
            agent = ClaudeAgent()
            analysis = agent.analyze_code(code, test_file)
            
            print(analysis[:500] + "...\n[Analyse tronquée pour l'affichage]")
        else:
            print(f"Le fichier {test_file} n'existe pas.")
    else:
        print("Usage: python claude_agent.py <fichier_à_analyser>")
