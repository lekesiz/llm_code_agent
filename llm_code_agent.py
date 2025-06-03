#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LLM Destekli Kod Analiz ve Refaktör Ajanı
-----------------------------------------
Un agent d'analyse de code multi-LLM qui utilise Claude 3, GPT-4 et Gemini Pro
pour analyser des projets logiciels, détecter des erreurs et proposer des améliorations.

Auteur: Manus
Date: Juin 2025
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from dotenv import load_dotenv

# Import des modules utilitaires
from utils.file_scanner import FileScanner
from utils.claude_agent import ClaudeAgent
from utils.chatgpt_agent import ChatGPTAgent
from utils.gemini_agent import GeminiAgent
from utils.todo_manager import TodoManager
from utils.html_exporter import HTMLExporter

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('llm_code_agent')

class LLMCodeAgent:
    """Classe principale de l'agent d'analyse de code multi-LLM."""
    
    def __init__(self):
        """Initialise l'agent avec les configurations et dépendances nécessaires."""
        # Chargement des variables d'environnement depuis .env
        load_dotenv()
        
        # Vérification des clés API
        self._check_api_keys()
        
        # Initialisation des composants
        self.file_scanner = FileScanner()
        self.claude_agent = ClaudeAgent()
        self.chatgpt_agent = ChatGPTAgent()
        self.gemini_agent = GeminiAgent()
        self.todo_manager = TodoManager()
        self.html_exporter = HTMLExporter()
        
        # Création des dossiers de sortie s'ils n'existent pas
        self._ensure_output_dirs()
    
    def _check_api_keys(self):
        """Vérifie la présence des clés API nécessaires."""
        required_keys = {
            'ANTHROPIC_API_KEY': 'Claude',
            'OPENAI_API_KEY': 'OpenAI GPT',
            'GOOGLE_API_KEY': 'Google Gemini'
        }
        
        missing_keys = []
        for key, service in required_keys.items():
            if not os.getenv(key):
                missing_keys.append(f"{service} ({key})")
        
        if missing_keys:
            logger.error(f"Clés API manquantes: {', '.join(missing_keys)}")
            logger.error("Veuillez ajouter les clés API manquantes dans le fichier .env")
            sys.exit(1)
        
        logger.info("Toutes les clés API requises sont présentes.")
    
    def _ensure_output_dirs(self):
        """Crée les dossiers de sortie s'ils n'existent pas."""
        dirs = [
            'analysis_reports',
            'refactoring_suggestions'
        ]
        
        for dir_name in dirs:
            dir_path = Path(dir_name)
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"Dossier créé: {dir_path}")
    
    def analyze_project(self, project_path):
        """
        Analyse un projet complet en parcourant tous les fichiers compatibles.
        
        Args:
            project_path (str): Chemin vers le dossier du projet à analyser
        """
        logger.info(f"Début de l'analyse du projet: {project_path}")
        
        # Scan du projet pour trouver les fichiers à analyser
        files = self.file_scanner.scan_directory(project_path)
        logger.info(f"Nombre de fichiers trouvés: {len(files)}")
        
        # Analyse de chaque fichier
        for file_path in files:
            self.analyze_file(file_path)
        
        # Génération du rapport principal
        self._generate_master_report(project_path, files)
        
        logger.info(f"Analyse du projet terminée: {project_path}")
    
    def analyze_file(self, file_path):
        """
        Analyse un fichier individuel avec les trois LLMs.
        
        Args:
            file_path (str): Chemin vers le fichier à analyser
        """
        rel_path = os.path.basename(file_path)
        logger.info(f"Analyse du fichier: {rel_path}")
        
        try:
            # Lecture du contenu du fichier
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 1. Analyse avec Claude
            logger.info(f"Analyse avec Claude: {rel_path}")
            claude_analysis = self.claude_agent.analyze_code(content, file_path)
            claude_output_path = f"analysis_reports/{os.path.basename(file_path)}_claude_analysis.md"
            with open(claude_output_path, 'w', encoding='utf-8') as f:
                f.write(claude_analysis)
            
            # 2. Analyse avec GPT
            logger.info(f"Analyse avec GPT: {rel_path}")
            gpt_review = self.chatgpt_agent.review_code(content, claude_analysis, file_path)
            gpt_output_path = f"refactoring_suggestions/{os.path.basename(file_path)}_chatgpt_review.md"
            with open(gpt_output_path, 'w', encoding='utf-8') as f:
                f.write(gpt_review)
            
            # 3. Analyse avec Gemini
            logger.info(f"Analyse avec Gemini: {rel_path}")
            gemini_suggestions = self.gemini_agent.suggest_refactoring(content, claude_analysis, file_path)
            gemini_output_path = f"refactoring_suggestions/{os.path.basename(file_path)}_gemini_suggestions.md"
            with open(gemini_output_path, 'w', encoding='utf-8') as f:
                f.write(gemini_suggestions)
            
            # 4. Extraction des tâches TODO
            todos = self.todo_manager.extract_todos(claude_analysis, gpt_review, gemini_suggestions, file_path)
            self.todo_manager.save_todos(todos)
            
            logger.info(f"Analyse complète pour: {rel_path}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse de {rel_path}: {str(e)}")
            return False
    
    def _generate_master_report(self, project_path, files):
        """
        Génère le rapport principal d'analyse du projet.
        
        Args:
            project_path (str): Chemin vers le dossier du projet analysé
            files (list): Liste des fichiers analysés
        """
        logger.info("Génération du rapport principal...")
        
        # Collecte des informations pour le rapport principal
        project_name = os.path.basename(os.path.abspath(project_path))
        file_count = len(files)
        todo_count = self.todo_manager.get_todo_count()
        
        # Création du contenu du rapport
        report_content = f"""# Rapport d'analyse du projet: {project_name}

## Résumé

- **Projet analysé:** {project_name}
- **Chemin:** {os.path.abspath(project_path)}
- **Nombre de fichiers analysés:** {file_count}
- **Nombre de tâches identifiées:** {todo_count}
- **Date d'analyse:** {self.todo_manager.get_current_date()}

## Fichiers analysés

"""
        
        # Ajout de la liste des fichiers analysés
        for file_path in files:
            rel_path = os.path.relpath(file_path, project_path)
            report_content += f"- [{rel_path}](analysis_reports/{os.path.basename(file_path)}_claude_analysis.md)\n"
        
        # Ajout des tâches principales identifiées
        report_content += "\n## Principales tâches identifiées\n\n"
        top_todos = self.todo_manager.get_top_todos(10)
        for todo in top_todos:
            report_content += f"- {todo['description']} (Priorité: {todo['priority']}, Fichier: {todo['file']})\n"
        
        # Ajout des liens vers les rapports complets
        report_content += "\n## Rapports détaillés\n\n"
        report_content += "### Analyses Claude\n\n"
        for file_path in files:
            file_name = os.path.basename(file_path)
            report_content += f"- [{file_name}](analysis_reports/{file_name}_claude_analysis.md)\n"
        
        report_content += "\n### Suggestions de refactoring (ChatGPT)\n\n"
        for file_path in files:
            file_name = os.path.basename(file_path)
            report_content += f"- [{file_name}](refactoring_suggestions/{file_name}_chatgpt_review.md)\n"
        
        report_content += "\n### Suggestions avancées (Gemini)\n\n"
        for file_path in files:
            file_name = os.path.basename(file_path)
            report_content += f"- [{file_name}](refactoring_suggestions/{file_name}_gemini_suggestions.md)\n"
        
        # Écriture du rapport principal
        with open("master_project_analysis_report.md", 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        # Génération de la version HTML
        self.html_exporter.convert_to_html("master_project_analysis_report.md", "master_project_analysis_report.html")
        
        logger.info("Rapport principal généré avec succès.")

def main():
    """Point d'entrée principal du programme."""
    parser = argparse.ArgumentParser(
        description="LLM Destekli Kod Analiz ve Refaktör Ajanı - Un agent d'analyse de code multi-LLM"
    )
    parser.add_argument(
        "project_path", 
        help="Chemin vers le dossier du projet à analyser"
    )
    parser.add_argument(
        "-f", "--file", 
        help="Analyser un fichier spécifique au lieu du projet entier"
    )
    parser.add_argument(
        "-v", "--verbose", 
        action="store_true", 
        help="Afficher des informations détaillées"
    )
    
    args = parser.parse_args()
    
    # Configuration du niveau de logging
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Initialisation de l'agent
    agent = LLMCodeAgent()
    
    # Analyse du projet ou d'un fichier spécifique
    if args.file:
        file_path = os.path.join(args.project_path, args.file) if not os.path.isabs(args.file) else args.file
        if os.path.isfile(file_path):
            agent.analyze_file(file_path)
        else:
            logger.error(f"Le fichier spécifié n'existe pas: {file_path}")
            sys.exit(1)
    else:
        if os.path.isdir(args.project_path):
            agent.analyze_project(args.project_path)
        else:
            logger.error(f"Le dossier spécifié n'existe pas: {args.project_path}")
            sys.exit(1)
    
    logger.info("Analyse terminée avec succès.")

if __name__ == "__main__":
    main()
