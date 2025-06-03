#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module de gestion des tâches TODO du projet.
Ce module est responsable de l'extraction, de la validation et de la sauvegarde des tâches TODO.
"""

import os
import json
import logging
import time
from typing import List, Dict, Optional, Set
from datetime import datetime

logger = logging.getLogger('llm_code_agent.todo_manager')

class TodoManager:
    """
    Gestionnaire de tâches TODO du projet.
    Responsable de l'extraction, de la validation et de la sauvegarde des tâches.
    """
    
    def __init__(self, todo_file: str = "project_todo.json"):
        """
        Initialise le gestionnaire de tâches TODO.
        
        Args:
            todo_file (str): Chemin du fichier JSON contenant les tâches TODO
        """
        self.todo_file = todo_file
        self.todos: List[Dict] = []
        self._load_todos()
        logger.info(f"Gestionnaire de tâches initialisé avec {len(self.todos)} tâches existantes")
    
    def _load_todos(self) -> None:
        """Charge les tâches TODO depuis le fichier JSON."""
        if os.path.exists(self.todo_file):
            try:
                with open(self.todo_file, 'r', encoding='utf-8') as f:
                    self.todos = json.load(f)
                logger.info(f"Chargement de {len(self.todos)} tâches depuis {self.todo_file}")
            except json.JSONDecodeError as e:
                logger.error(f"Erreur lors du chargement des tâches: {str(e)}")
                self.todos = []
        else:
            logger.info(f"Fichier {self.todo_file} non trouvé, création d'une nouvelle liste de tâches")
            self.todos = []
    
    def _save_todos(self) -> None:
        """Sauvegarde les tâches TODO dans le fichier JSON."""
        try:
            with open(self.todo_file, 'w', encoding='utf-8') as f:
                json.dump(self.todos, f, indent=2, ensure_ascii=False)
            logger.info(f"{len(self.todos)} tâches sauvegardées dans {self.todo_file}")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des tâches: {str(e)}")
    
    def _generate_todo_id(self) -> str:
        """Génère un ID unique pour une tâche TODO."""
        timestamp = int(time.time())
        return f"todo_{timestamp}_{len(self.todos)}"
    
    def _validate_todo(self, todo: Dict) -> bool:
        """
        Valide une tâche TODO.
        
        Args:
            todo (Dict): Tâche TODO à valider
            
        Returns:
            bool: True si la tâche est valide, False sinon
        """
        required_fields = {'description', 'priority', 'effort', 'file'}
        if not all(field in todo for field in required_fields):
            logger.warning(f"Tâche invalide: champs requis manquants. Tâche: {todo}")
            return False
        
        valid_priorities = {'Critique', 'Élevée', 'Moyenne', 'Faible'}
        if todo['priority'] not in valid_priorities:
            logger.warning(f"Priorité invalide: {todo['priority']}. Tâche: {todo}")
            return False
        
        valid_efforts = {'Élevé', 'Moyen', 'Faible'}
        if todo['effort'] not in valid_efforts:
            logger.warning(f"Niveau d'effort invalide: {todo['effort']}. Tâche: {todo}")
            return False
        
        return True
    
    def _is_duplicate(self, new_todo: Dict) -> bool:
        """
        Vérifie si une tâche TODO est un doublon.
        
        Args:
            new_todo (Dict): Nouvelle tâche à vérifier
            
        Returns:
            bool: True si la tâche est un doublon, False sinon
        """
        for existing_todo in self.todos:
            if (existing_todo['description'] == new_todo['description'] and
                existing_todo['file'] == new_todo['file'] and
                not existing_todo.get('completed', False)):
                return True
        return False
    
    def add_todos(self, new_todos: List[Dict], source: str = "Unknown") -> None:
        """
        Ajoute de nouvelles tâches TODO.
        
        Args:
            new_todos (List[Dict]): Liste des nouvelles tâches à ajouter
            source (str): Source des tâches (Claude, ChatGPT, etc.)
        """
        added_count = 0
        for todo in new_todos:
            # Ajout des métadonnées
            todo['source'] = source
            todo['id'] = self._generate_todo_id()
            todo['timestamp'] = int(time.time())
            todo['completed'] = False
            
            # Validation et ajout
            if self._validate_todo(todo) and not self._is_duplicate(todo):
                self.todos.append(todo)
                added_count += 1
            else:
                logger.warning(f"Tâche ignorée: {todo['description']}")
        
        if added_count > 0:
            self._save_todos()
            logger.info(f"{added_count} nouvelles tâches ajoutées depuis {source}")
    
    def mark_completed(self, todo_id: str) -> bool:
        """
        Marque une tâche comme complétée.
        
        Args:
            todo_id (str): ID de la tâche à marquer
            
        Returns:
            bool: True si la tâche a été marquée, False sinon
        """
        for todo in self.todos:
            if todo['id'] == todo_id:
                todo['completed'] = True
                todo['completed_at'] = int(time.time())
                self._save_todos()
                logger.info(f"Tâche {todo_id} marquée comme complétée")
                return True
        logger.warning(f"Tâche {todo_id} non trouvée")
        return False
    
    def get_todos(self, 
                 file: Optional[str] = None,
                 priority: Optional[str] = None,
                 effort: Optional[str] = None,
                 completed: Optional[bool] = None) -> List[Dict]:
        """
        Récupère les tâches TODO avec filtres optionnels.
        
        Args:
            file (str, optional): Filtre par fichier
            priority (str, optional): Filtre par priorité
            effort (str, optional): Filtre par niveau d'effort
            completed (bool, optional): Filtre par statut de complétion
            
        Returns:
            List[Dict]: Liste des tâches filtrées
        """
        filtered_todos = self.todos
        
        if file is not None:
            filtered_todos = [todo for todo in filtered_todos if todo['file'] == file]
        
        if priority is not None:
            filtered_todos = [todo for todo in filtered_todos if todo['priority'] == priority]
        
        if effort is not None:
            filtered_todos = [todo for todo in filtered_todos if todo['effort'] == effort]
        
        if completed is not None:
            filtered_todos = [todo for todo in filtered_todos if todo.get('completed', False) == completed]
        
        return filtered_todos
    
    def get_todo_statistics(self) -> Dict:
        """
        Génère des statistiques sur les tâches TODO.
        
        Returns:
            Dict: Statistiques des tâches
        """
        stats = {
            'total': len(self.todos),
            'completed': len([todo for todo in self.todos if todo.get('completed', False)]),
            'by_priority': {},
            'by_effort': {},
            'by_file': {},
            'by_source': {}
        }
        
        for todo in self.todos:
            # Statistiques par priorité
            priority = todo['priority']
            stats['by_priority'][priority] = stats['by_priority'].get(priority, 0) + 1
            
            # Statistiques par niveau d'effort
            effort = todo['effort']
            stats['by_effort'][effort] = stats['by_effort'].get(effort, 0) + 1
            
            # Statistiques par fichier
            file = todo['file']
            stats['by_file'][file] = stats['by_file'].get(file, 0) + 1
            
            # Statistiques par source
            source = todo.get('source', 'Unknown')
            stats['by_source'][source] = stats['by_source'].get(source, 0) + 1
        
        return stats
    
    def cleanup_duplicates(self) -> int:
        """
        Nettoie les tâches TODO en double.
        
        Returns:
            int: Nombre de tâches supprimées
        """
        seen_descriptions: Set[str] = set()
        unique_todos = []
        removed_count = 0
        
        for todo in self.todos:
            description = todo['description']
            if description not in seen_descriptions:
                seen_descriptions.add(description)
                unique_todos.append(todo)
            else:
                removed_count += 1
        
        if removed_count > 0:
            self.todos = unique_todos
            self._save_todos()
            logger.info(f"{removed_count} tâches en double supprimées")
        
        return removed_count

    def extract_todos(self, claude_analysis, gpt_review, gemini_suggestions, file_path):
        """
        Extrait les tâches TODO à partir des analyses des trois agents.
        
        Args:
            claude_analysis (str): Analyse de Claude
            gpt_review (str): Review de ChatGPT
            gemini_suggestions (str): Suggestions de Gemini
            file_path (str): Chemin du fichier analysé
            
        Returns:
            list: Liste des tâches TODO
        """
        todos = []
        
        # Extraction depuis l'analyse de Claude
        claude_todos = self._extract_todos_from_text(claude_analysis)
        todos.extend(claude_todos)
        
        # Extraction depuis la review de ChatGPT
        gpt_todos = self._extract_todos_from_text(gpt_review)
        todos.extend(gpt_todos)
        
        # Extraction depuis les suggestions de Gemini
        gemini_todos = self._extract_todos_from_text(gemini_suggestions)
        todos.extend(gemini_todos)
        
        # Ajout du fichier source à chaque TODO
        for todo in todos:
            todo['file'] = file_path
        
        return todos

    def _extract_todos_from_text(self, content: str) -> List[Dict]:
        """
        Extrait les tâches TODO à partir du texte d'une analyse.
        
        Args:
            content (str): Contenu de l'analyse
            
        Returns:
            List[Dict]: Liste des tâches TODO extraites
        """
        todos = []
        lines = content.split('\n')
        current_todo = None
        
        for line in lines:
            # Détection des titres qui pourraient indiquer une tâche TODO
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
            elif current_todo and 'effort' in line.lower():
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
    logging.basicConfig(level=logging.INFO)
    
    # Test du gestionnaire de tâches
    manager = TodoManager("test_todos.json")
    
    # Ajout de quelques tâches de test
    test_todos = [
        {
            "description": "Refactoriser la méthode X",
            "priority": "Élevée",
            "effort": "Moyen",
            "file": "test.py"
        },
        {
            "description": "Ajouter des tests unitaires",
            "priority": "Moyenne",
            "effort": "Élevé",
            "file": "test.py"
        }
    ]
    
    manager.add_todos(test_todos, "Test")
    print(f"Statistiques: {manager.get_todo_statistics()}")
    
    # Nettoyage
    os.remove("test_todos.json")
