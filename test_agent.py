#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module de test pour l'agent d'analyse de code multi-LLM.
Ce module contient les tests unitaires et d'intégration pour les différents composants.
"""

import os
import sys
import json
import logging
import unittest
from typing import Dict, List, Optional
from pathlib import Path

# Ajout du répertoire parent au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.gemini_agent import GeminiAgent
from utils.todo_manager import TodoManager
from utils.claude_agent import ClaudeAgent
from utils.gpt_agent import GPTAgent

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test_agent')

class TestGeminiAgent(unittest.TestCase):
    """Tests unitaires pour l'agent Gemini."""
    
    def setUp(self):
        """Initialisation avant chaque test."""
        self.agent = GeminiAgent()
        self.test_file = "test_files/test.py"
        self._create_test_file()
    
    def tearDown(self):
        """Nettoyage après chaque test."""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
    
    def _create_test_file(self):
        """Crée un fichier de test."""
        os.makedirs(os.path.dirname(self.test_file), exist_ok=True)
        with open(self.test_file, 'w') as f:
            f.write("""
def calculate_total(items):
    total = 0
    for item in items:
        total += item.price
    return total

class Item:
    def __init__(self, price):
        self.price = price
""")
    
    def test_suggest_refactoring(self):
        """Test de la méthode suggest_refactoring."""
        suggestions = self.agent.suggest_refactoring(self.test_file)
        self.assertIsNotNone(suggestions)
        self.assertIsInstance(suggestions, str)
        self.assertTrue(len(suggestions) > 0)
    
    def test_extract_todos(self):
        """Test de l'extraction des TODOs."""
        suggestions = self.agent.suggest_refactoring(self.test_file)
        todos = self.agent.extract_todos_from_suggestions(suggestions)
        self.assertIsInstance(todos, list)
        if todos:
            self.assertIsInstance(todos[0], dict)
            self.assertIn('description', todos[0])
            self.assertIn('priority', todos[0])
            self.assertIn('effort', todos[0])

class TestTodoManager(unittest.TestCase):
    """Tests unitaires pour le gestionnaire de tâches TODO."""
    
    def setUp(self):
        """Initialisation avant chaque test."""
        self.todo_file = "test_todos.json"
        self.manager = TodoManager(self.todo_file)
    
    def tearDown(self):
        """Nettoyage après chaque test."""
        if os.path.exists(self.todo_file):
            os.remove(self.todo_file)
    
    def test_add_todos(self):
        """Test de l'ajout de tâches TODO."""
        test_todos = [
            {
                "description": "Test task 1",
                "priority": "Élevée",
                "effort": "Moyen",
                "file": "test.py"
            }
        ]
        self.manager.add_todos(test_todos, "Test")
        self.assertEqual(len(self.manager.get_todos()), 1)
    
    def test_mark_completed(self):
        """Test du marquage d'une tâche comme complétée."""
        test_todos = [
            {
                "description": "Test task 1",
                "priority": "Élevée",
                "effort": "Moyen",
                "file": "test.py"
            }
        ]
        self.manager.add_todos(test_todos, "Test")
        todo_id = self.manager.get_todos()[0]['id']
        self.assertTrue(self.manager.mark_completed(todo_id))
        self.assertTrue(self.manager.get_todos(completed=True)[0]['completed'])
    
    def test_get_todos_with_filters(self):
        """Test de la récupération des tâches avec filtres."""
        test_todos = [
            {
                "description": "Test task 1",
                "priority": "Élevée",
                "effort": "Moyen",
                "file": "test1.py"
            },
            {
                "description": "Test task 2",
                "priority": "Moyenne",
                "effort": "Faible",
                "file": "test2.py"
            }
        ]
        self.manager.add_todos(test_todos, "Test")
        
        # Test des filtres
        self.assertEqual(len(self.manager.get_todos(file="test1.py")), 1)
        self.assertEqual(len(self.manager.get_todos(priority="Élevée")), 1)
        self.assertEqual(len(self.manager.get_todos(effort="Faible")), 1)
    
    def test_cleanup_duplicates(self):
        """Test du nettoyage des doublons."""
        test_todos = [
            {
                "description": "Test task",
                "priority": "Élevée",
                "effort": "Moyen",
                "file": "test.py"
            },
            {
                "description": "Test task",
                "priority": "Élevée",
                "effort": "Moyen",
                "file": "test.py"
            }
        ]
        self.manager.add_todos(test_todos, "Test")
        removed_count = self.manager.cleanup_duplicates()
        self.assertEqual(removed_count, 1)
        self.assertEqual(len(self.manager.get_todos()), 1)

class TestIntegration(unittest.TestCase):
    """Tests d'intégration pour l'ensemble du système."""
    
    def setUp(self):
        """Initialisation avant chaque test."""
        self.test_dir = "test_files"
        self.todo_file = "test_todos.json"
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Initialisation des agents
        self.gemini_agent = GeminiAgent()
        self.todo_manager = TodoManager(self.todo_file)
    
    def tearDown(self):
        """Nettoyage après chaque test."""
        if os.path.exists(self.todo_file):
            os.remove(self.todo_file)
        if os.path.exists(self.test_dir):
            for file in os.listdir(self.test_dir):
                os.remove(os.path.join(self.test_dir, file))
            os.rmdir(self.test_dir)
    
    def test_full_workflow(self):
        """Test du workflow complet."""
        # Création d'un fichier de test
        test_file = os.path.join(self.test_dir, "test.py")
        with open(test_file, 'w') as f:
            f.write("""
def process_data(data):
    result = []
    for item in data:
        result.append(item * 2)
    return result
""")
        
        # Analyse avec Gemini
        suggestions = self.gemini_agent.suggest_refactoring(test_file)
        self.assertIsNotNone(suggestions)
        
        # Extraction des TODOs
        todos = self.gemini_agent.extract_todos_from_suggestions(suggestions)
        self.assertIsInstance(todos, list)
        
        # Ajout des TODOs
        self.todo_manager.add_todos(todos, "Gemini")
        self.assertTrue(len(self.todo_manager.get_todos()) > 0)
        
        # Vérification des statistiques
        stats = self.todo_manager.get_todo_statistics()
        self.assertIn('total', stats)
        self.assertIn('by_priority', stats)
        self.assertIn('by_effort', stats)

def run_tests():
    """Exécute tous les tests."""
    # Création de la suite de tests
    suite = unittest.TestSuite()
    
    # Ajout des tests
    suite.addTest(unittest.makeSuite(TestGeminiAgent))
    suite.addTest(unittest.makeSuite(TestTodoManager))
    suite.addTest(unittest.makeSuite(TestIntegration))
    
    # Exécution des tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Affichage des résultats
    print("\nRésultats des tests:")
    print(f"Tests exécutés: {result.testsRun}")
    print(f"Tests réussis: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Tests échoués: {len(result.failures)}")
    print(f"Tests avec erreurs: {len(result.errors)}")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
