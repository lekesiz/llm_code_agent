#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module de gestion des tâches TODO pour l'agent d'analyse de code multi-LLM.
Ce module est responsable de l'extraction, de la gestion et de la persistance des tâches TODO.
"""

import os
import json
import logging
import time
from datetime import datetime
from pathlib import Path

logger = logging.getLogger('llm_code_agent.todo_manager')

class TodoManager:
    """
    Gestionnaire des tâches TODO identifiées lors de l'analyse de code.
    """
    
    def __init__(self, todo_file="project_todo.json"):
        """
        Initialise le gestionnaire de tâches TODO.
        
        Args:
            todo_file (str): Chemin du fichier JSON pour stocker les tâches
        """
        self.todo_file = todo_file
        self.todos = self._load_todos()
        logger.info(f"Gestionnaire de tâches initialisé avec {len(self.todos)} tâches existantes")
    
    def _load_todos(self):
        """
        Charge les tâches TODO depuis le fichier JSON s'il existe.
        
        Returns:
            list: Liste des tâches TODO
        """
        if os.path.exists(self.todo_file):
            try:
                with open(self.todo_file, 'r', encoding='utf-8') as f:
                    todos = json.load(f)
                logger.info(f"Chargement de {len(todos)} tâches depuis {self.todo_file}")
                return todos
            except Exception as e:
                logger.error(f"Erreur lors du chargement des tâches: {str(e)}")
                return []
        else:
            logger.info(f"Fichier {self.todo_file} non trouvé, création d'une nouvelle liste de tâches")
            return []
    
    def save_todos(self, new_todos=None):
        """
        Sauvegarde les tâches TODO dans le fichier JSON.
        
        Args:
            new_todos (list, optional): Nouvelles tâches à ajouter
        """
        if new_todos:
            # Ajouter un timestamp et un ID unique à chaque nouvelle tâche
            timestamp = self.get_current_timestamp()
            for todo in new_todos:
                if 'id' not in todo:
                    todo['id'] = f"todo_{timestamp}_{len(self.todos) + len(new_todos)}"
                if 'timestamp' not in todo:
                    todo['timestamp'] = timestamp
                if 'completed' not in todo:
                    todo['completed'] = False
            
            # Ajouter les nouvelles tâches à la liste existante
            self.todos.extend(new_todos)
        
        # Sauvegarder toutes les tâches dans le fichier JSON
        try:
            with open(self.todo_file, 'w', encoding='utf-8') as f:
                json.dump(self.todos, f, indent=2, ensure_ascii=False)
            logger.info(f"{len(self.todos)} tâches sauvegardées dans {self.todo_file}")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des tâches: {str(e)}")
    
    def extract_todos(self, claude_analysis, gpt_review, gemini_suggestions, file_path):
        """
        Extrait les tâches TODO à partir des analyses des trois LLMs.
        
        Args:
            claude_analysis (str): Analyse de Claude
            gpt_review (str): Validation et suggestions de ChatGPT
            gemini_suggestions (str): Suggestions avancées de Gemini
            file_path (str): Chemin du fichier analysé
            
        Returns:
            list: Liste des tâches TODO extraites
        """
        file_name = os.path.basename(file_path)
        logger.info(f"Extraction des tâches TODO pour {file_name}")
        
        todos = []
        
        # Extraction des TODOs de l'analyse de Claude
        claude_todos = self._extract_todos_from_text(claude_analysis, "Claude")
        for todo in claude_todos:
            todo['file'] = file_name
            todo['source'] = "Claude"
        todos.extend(claude_todos)
        
        # Extraction des TODOs de la validation de ChatGPT
        gpt_todos = self._extract_todos_from_text(gpt_review, "ChatGPT")
        for todo in gpt_todos:
            todo['file'] = file_name
            todo['source'] = "ChatGPT"
        todos.extend(gpt_todos)
        
        # Extraction des TODOs des suggestions de Gemini
        gemini_todos = self._extract_todos_from_text(gemini_suggestions, "Gemini")
        for todo in gemini_todos:
            todo['file'] = file_name
            todo['source'] = "Gemini"
        todos.extend(gemini_todos)
        
        logger.info(f"{len(todos)} tâches TODO extraites pour {file_name}")
        return todos
    
    def _extract_todos_from_text(self, text, source):
        """
        Extrait les tâches TODO à partir d'un texte d'analyse.
        
        Args:
            text (str): Texte d'analyse
            source (str): Source de l'analyse (Claude, ChatGPT, Gemini)
            
        Returns:
            list: Liste des tâches TODO extraites
        """
        todos = []
        
        # Recherche d'un bloc JSON contenant des TODOs
        import re
        json_pattern = r'```json\s*([\s\S]*?)\s*```'
        json_matches = re.findall(json_pattern, text)
        
        if json_matches:
            for json_str in json_matches:
                try:
                    # Tentative de parsing du JSON
                    todo_data = json.loads(json_str)
                    
                    # Si c'est une liste, on l'ajoute directement
                    if isinstance(todo_data, list):
                        todos.extend(todo_data)
                    # Si c'est un dictionnaire avec une clé "todos", on utilise cette liste
                    elif isinstance(todo_data, dict) and "todos" in todo_data:
                        todos.extend(todo_data["todos"])
                except json.JSONDecodeError:
                    logger.warning(f"Impossible de parser le JSON des TODOs depuis {source}")
        
        # Si aucun JSON n'est trouvé ou si le parsing a échoué, on extrait les TODOs à partir du texte
        if not todos:
            # Recherche des sections TODO ou des listes de tâches
            lines = text.split('\n')
            in_todo_section = False
            current_priority = "Moyenne"
            
            for i, line in enumerate(lines):
                line_lower = line.lower()
                
                # Détection des sections TODO
                if ('# todo' in line_lower or '## todo' in line_lower or 
                    '# tâches' in line_lower or '## tâches' in line_lower or
                    '# tasks' in line_lower or '## tasks' in line_lower):
                    in_todo_section = True
                    continue
                
                # Sortie de la section TODO
                if in_todo_section and line.startswith('#'):
                    in_todo_section = False
                
                # Détection de la priorité
                if 'priorité' in line_lower or 'priority' in line_lower:
                    if 'critique' in line_lower or 'critical' in line_lower:
                        current_priority = "Critique"
                    elif 'élevée' in line_lower or 'high' in line_lower:
                        current_priority = "Élevée"
                    elif 'moyenne' in line_lower or 'medium' in line_lower:
                        current_priority = "Moyenne"
                    elif 'faible' in line_lower or 'low' in line_lower:
                        current_priority = "Faible"
                
                # Détection des éléments de liste qui pourraient être des TODOs
                if (line.strip().startswith('- ') or line.strip().startswith('* ') or
                    line.strip().startswith('+ ') or line.strip().startswith('1. ')):
                    
                    # Si on est dans une section TODO ou si la ligne contient des mots-clés
                    if in_todo_section or any(keyword in line_lower for keyword in ['todo', 'fix', 'improve', 'refactor', 'optimize', 'add', 'remove', 'update']):
                        description = line.strip().lstrip('-*+1234567890. ').strip()
                        
                        # Éviter les descriptions trop courtes ou vides
                        if len(description) > 5:
                            todo = {
                                'description': description,
                                'priority': current_priority,
                                'effort': 'Moyen'  # Valeur par défaut
                            }
                            
                            # Déterminer l'effort en fonction du contenu
                            if any(word in line_lower for word in ['simple', 'easy', 'quick', 'minor']):
                                todo['effort'] = 'Faible'
                            elif any(word in line_lower for word in ['complex', 'difficult', 'major', 'significant']):
                                todo['effort'] = 'Élevé'
                            
                            todos.append(todo)
        
        return todos
    
    def get_todo_count(self):
        """
        Retourne le nombre total de tâches TODO.
        
        Returns:
            int: Nombre de tâches TODO
        """
        return len(self.todos)
    
    def get_top_todos(self, limit=10):
        """
        Retourne les tâches TODO les plus prioritaires.
        
        Args:
            limit (int): Nombre maximum de tâches à retourner
            
        Returns:
            list: Liste des tâches TODO les plus prioritaires
        """
        # Tri des tâches par priorité
        priority_order = {
            'Critique': 0,
            'Élevée': 1,
            'Moyenne': 2,
            'Faible': 3
        }
        
        sorted_todos = sorted(
            self.todos,
            key=lambda x: (
                priority_order.get(x.get('priority', 'Moyenne'), 4),  # Tri par priorité
                x.get('timestamp', 0)  # Puis par timestamp (plus récent d'abord)
            )
        )
        
        return sorted_todos[:limit]
    
    def mark_todo_completed(self, todo_id):
        """
        Marque une tâche TODO comme terminée.
        
        Args:
            todo_id (str): ID de la tâche à marquer comme terminée
            
        Returns:
            bool: True si la tâche a été trouvée et marquée, False sinon
        """
        for todo in self.todos:
            if todo.get('id') == todo_id:
                todo['completed'] = True
                todo['completed_at'] = self.get_current_timestamp()
                self.save_todos()
                logger.info(f"Tâche {todo_id} marquée comme terminée")
                return True
        
        logger.warning(f"Tâche {todo_id} non trouvée")
        return False
    
    def get_current_timestamp(self):
        """
        Retourne le timestamp actuel.
        
        Returns:
            int: Timestamp actuel
        """
        return int(time.time())
    
    def get_current_date(self):
        """
        Retourne la date actuelle au format lisible.
        
        Returns:
            str: Date actuelle au format lisible
        """
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def export_todos_as_markdown(self, output_file="project_todos.md"):
        """
        Exporte les tâches TODO au format Markdown.
        
        Args:
            output_file (str): Chemin du fichier Markdown de sortie
            
        Returns:
            bool: True si l'export a réussi, False sinon
        """
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("# Liste des tâches TODO du projet\n\n")
                f.write(f"*Généré le {self.get_current_date()}*\n\n")
                
                # Grouper les tâches par priorité
                priorities = ['Critique', 'Élevée', 'Moyenne', 'Faible']
                
                for priority in priorities:
                    f.write(f"## Priorité: {priority}\n\n")
                    
                    # Filtrer les tâches par priorité
                    priority_todos = [todo for todo in self.todos if todo.get('priority') == priority]
                    
                    if not priority_todos:
                        f.write("*Aucune tâche dans cette catégorie*\n\n")
                        continue
                    
                    # Grouper par fichier
                    files = sorted(set(todo.get('file', 'Général') for todo in priority_todos))
                    
                    for file in files:
                        f.write(f"### Fichier: {file}\n\n")
                        
                        # Filtrer les tâches par fichier
                        file_todos = [todo for todo in priority_todos if todo.get('file') == file]
                        
                        for todo in file_todos:
                            status = "✅" if todo.get('completed', False) else "⬜"
                            source = todo.get('source', 'Inconnu')
                            effort = todo.get('effort', 'Moyen')
                            
                            f.write(f"- [{status}] {todo['description']} (Effort: {effort}, Source: {source})\n")
                        
                        f.write("\n")
            
            logger.info(f"Tâches TODO exportées au format Markdown dans {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'export des tâches au format Markdown: {str(e)}")
            return False

# Test unitaire simple si exécuté directement
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Créer un gestionnaire de tâches
    todo_manager = TodoManager("test_todo.json")
    
    # Ajouter quelques tâches de test
    test_todos = [
        {
            "description": "Corriger le bug dans la fonction calculate_total()",
            "priority": "Critique",
            "effort": "Moyen",
            "file": "calculator.py",
            "source": "Claude"
        },
        {
            "description": "Optimiser la boucle for dans process_data()",
            "priority": "Moyenne",
            "effort": "Faible",
            "file": "data_processor.py",
            "source": "ChatGPT"
        },
        {
            "description": "Refactoriser la classe UserManager pour utiliser le pattern Singleton",
            "priority": "Élevée",
            "effort": "Élevé",
            "file": "user_manager.py",
            "source": "Gemini"
        }
    ]
    
    # Sauvegarder les tâches
    todo_manager.save_todos(test_todos)
    
    # Afficher les tâches les plus prioritaires
    top_todos = todo_manager.get_top_todos(2)
    print(f"Top {len(top_todos)} tâches:")
    for todo in top_todos:
        print(f"- {todo['description']} (Priorité: {todo['priority']}, Fichier: {todo['file']})")
    
    # Exporter les tâches au format Markdown
    todo_manager.export_todos_as_markdown("test_todos.md")
    print("Tâches exportées au format Markdown dans test_todos.md")
