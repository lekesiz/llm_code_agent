#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de test pour valider le fonctionnement global de l'agent d'analyse de code multi-LLM.
Ce script permet de tester l'ensemble des fonctionnalités sur un petit projet exemple.
"""

import os
import sys
import logging
import shutil
from pathlib import Path

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('test_llm_code_agent')

# Chemin vers le script principal
MAIN_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "llm_code_agent.py")

def create_test_project():
    """
    Crée un petit projet de test avec quelques fichiers pour tester l'agent.
    
    Returns:
        str: Chemin vers le projet de test
    """
    logger.info("Création d'un projet de test...")
    
    # Création du dossier de test
    test_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_project")
    os.makedirs(test_dir, exist_ok=True)
    
    # Création d'un fichier Python
    python_file = os.path.join(test_dir, "calculator.py")
    with open(python_file, 'w', encoding='utf-8') as f:
        f.write("""
# Simple calculator module with some intentional issues

def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    # Missing check for division by zero
    return a / b

# Unused function
def square(a):
    return a * a

# Function with a bug
def average(numbers):
    total = 0
    for num in numbers:
        total += num
    # Bug: should divide by len(numbers)
    return total

# Main calculator class with some issues
class Calculator:
    def __init__(self):
        self.result = 0
    
    # Method with redundant code
    def calculate(self, a, b, operation):
        if operation == 'add':
            self.result = self.add(a, b)
        elif operation == 'subtract':
            self.result = self.subtract(a, b)
        elif operation == 'multiply':
            self.result = self.multiply(a, b)
        elif operation == 'divide':
            self.result = self.divide(a, b)
        return self.result
    
    # Redundant methods that duplicate the functions above
    def add(self, a, b):
        return a + b
    
    def subtract(self, a, b):
        return a - b
    
    def multiply(self, a, b):
        return a * b
    
    def divide(self, a, b):
        return a / b

# Global variable - not a good practice
calculator = Calculator()
""")
    
    # Création d'un fichier JavaScript
    js_file = os.path.join(test_dir, "user_manager.js")
    with open(js_file, 'w', encoding='utf-8') as f:
        f.write("""
// User manager module with some intentional issues

// Global variables - not a good practice
var users = [];
var currentUser = null;

// Function with security issues
function login(username, password) {
    // Insecure: storing passwords in plain text
    for (var i = 0; i < users.length; i++) {
        if (users[i].username === username && users[i].password === password) {
            currentUser = users[i];
            console.log("User logged in: " + username);
            return true;
        }
    }
    console.log("Login failed");
    return false;
}

// Function with performance issues
function findUserById(id) {
    // Inefficient: should use a map or object for O(1) lookup
    for (var i = 0; i < users.length; i++) {
        if (users[i].id === id) {
            return users[i];
        }
    }
    return null;
}

// Function with a bug
function registerUser(username, password, email) {
    // Bug: doesn't check if username already exists
    var newUser = {
        id: users.length + 1,
        username: username,
        password: password,  // Security issue: storing password in plain text
        email: email,
        createdAt: new Date()
    };
    users.push(newUser);
    return newUser;
}

// Exposed functions
module.exports = {
    login: login,
    findUserById: findUserById,
    registerUser: registerUser
};
""")
    
    # Création d'un fichier HTML
    html_file = os.path.join(test_dir, "index.html")
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Test Page</title>
    <style>
        /* Redundant CSS rules */
        body {
            font-family: Arial, sans-serif;
            font-family: Arial;
            color: #333;
            color: #333333;
        }
        
        /* Unused CSS class */
        .unused-class {
            display: none;
        }
    </style>
</head>
<body>
    <!-- Missing alt attribute for accessibility -->
    <img src="logo.png">
    
    <!-- Deprecated HTML tag -->
    <center>Centered Text</center>
    
    <!-- Form with accessibility issues -->
    <form action="/submit" method="post">
        <!-- Missing label for input -->
        <input type="text" name="username">
        <input type="password" name="password">
        <button type="submit">Login</button>
    </form>
    
    <!-- Inline script - better to separate concerns -->
    <script>
        function validateForm() {
            // Missing form validation
            return true;
        }
    </script>
</body>
</html>
""")
    
    logger.info(f"Projet de test créé dans {test_dir}")
    return test_dir

def run_test(test_project_path):
    """
    Exécute l'agent d'analyse de code sur le projet de test.
    
    Args:
        test_project_path (str): Chemin vers le projet de test
    """
    logger.info("Exécution du test de l'agent d'analyse de code...")
    
    # Vérification de la présence du fichier .env
    env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if not os.path.exists(env_file):
        logger.error(f"Le fichier .env n'existe pas. Veuillez créer un fichier .env basé sur .env.example")
        return False
    
    # Exécution de l'agent sur le projet de test
    cmd = f"python {MAIN_SCRIPT} {test_project_path} -v"
    logger.info(f"Commande: {cmd}")
    
    try:
        import subprocess
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        logger.info("Exécution réussie")
        logger.info(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Erreur lors de l'exécution: {e}")
        logger.error(e.stderr)
        return False

def verify_outputs():
    """
    Vérifie que les fichiers de sortie attendus ont été générés.
    
    Returns:
        bool: True si tous les fichiers attendus sont présents, False sinon
    """
    logger.info("Vérification des fichiers de sortie...")
    
    # Liste des fichiers attendus
    expected_files = [
        "analysis_reports/calculator.py_claude_analysis.md",
        "analysis_reports/user_manager.js_claude_analysis.md",
        "analysis_reports/index.html_claude_analysis.md",
        "refactoring_suggestions/calculator.py_chatgpt_review.md",
        "refactoring_suggestions/user_manager.js_chatgpt_review.md",
        "refactoring_suggestions/index.html_chatgpt_review.md",
        "refactoring_suggestions/calculator.py_gemini_suggestions.md",
        "refactoring_suggestions/user_manager.js_gemini_suggestions.md",
        "refactoring_suggestions/index.html_gemini_suggestions.md",
        "master_project_analysis_report.md",
        "master_project_analysis_report.html",
        "project_todo.json"
    ]
    
    missing_files = []
    for file in expected_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        logger.error(f"Fichiers manquants: {', '.join(missing_files)}")
        return False
    
    logger.info("Tous les fichiers attendus sont présents")
    return True

def cleanup_test_project(test_project_path):
    """
    Nettoie le projet de test.
    
    Args:
        test_project_path (str): Chemin vers le projet de test
    """
    logger.info(f"Nettoyage du projet de test: {test_project_path}")
    
    try:
        shutil.rmtree(test_project_path)
        logger.info("Projet de test supprimé avec succès")
    except Exception as e:
        logger.error(f"Erreur lors de la suppression du projet de test: {str(e)}")

if __name__ == "__main__":
    logger.info("Début des tests de l'agent d'analyse de code multi-LLM")
    
    # Création du projet de test
    test_project = create_test_project()
    
    # Exécution du test
    success = run_test(test_project)
    
    # Vérification des sorties
    if success:
        outputs_ok = verify_outputs()
        if outputs_ok:
            logger.info("Test réussi: tous les fichiers attendus ont été générés")
        else:
            logger.error("Test échoué: certains fichiers attendus sont manquants")
    
    # Nettoyage (optionnel, commenter pour conserver le projet de test)
    # cleanup_test_project(test_project)
    
    logger.info("Fin des tests")
