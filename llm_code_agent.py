#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script principal de l'agent d'analyse de code multi-LLM.
Ce script coordonne l'analyse de code avec Claude, ChatGPT et Gemini.
"""

import os
import sys
import json
import time
import logging
import argparse
import asyncio
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import List, Dict, Optional, Set
from datetime import datetime

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.logging import RichHandler
from rich.panel import Panel
from rich.table import Table

from utils.gemini_agent import GeminiAgent
from utils.todo_manager import TodoManager
from utils.claude_agent import ClaudeAgent
from utils.gpt_agent import GPTAgent

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger("llm_code_agent")

# Initialisation de Rich
console = Console()

class LLMCodeAgent:
    """
    Agent principal d'analyse de code multi-LLM.
    Coordonne l'analyse avec Claude, ChatGPT et Gemini.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialise l'agent d'analyse de code.
        
        Args:
            config (Dict, optional): Configuration personnalisée
        """
        self.config = config or {}
        self.setup_agents()
        self.todo_manager = TodoManager()
        self.processed_files: Set[str] = set()
        self.stats = {
            'start_time': time.time(),
            'files_processed': 0,
            'total_todos': 0,
            'errors': 0
        }
    
    def setup_agents(self):
        """Initialise les agents LLM."""
        try:
            self.claude_agent = ClaudeAgent()
            self.gpt_agent = GPTAgent()
            self.gemini_agent = GeminiAgent()
            logger.info("Agents LLM initialisés avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation des agents: {str(e)}")
            raise
    
    async def analyze_file(self, file_path: str) -> Dict:
        """
        Analyse un fichier avec les trois agents LLM.
        
        Args:
            file_path (str): Chemin du fichier à analyser
            
        Returns:
            Dict: Résultats de l'analyse
        """
        try:
            # Vérification du fichier
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Fichier non trouvé: {file_path}")
            
            # Lecture du fichier
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Analyse parallèle avec les trois agents
            async with asyncio.TaskGroup() as group:
                claude_task = group.create_task(self.claude_agent.analyze_code(content, file_path))
                gpt_task = group.create_task(self.gpt_agent.analyze_code(content, file_path))
                gemini_task = group.create_task(self.gemini_agent.suggest_refactoring(file_path))
            
            # Récupération des résultats
            claude_analysis = claude_task.result()
            gpt_review = gpt_task.result()
            gemini_suggestions = gemini_task.result()
            
            # Extraction des TODOs
            todos = self.todo_manager.extract_todos(
                claude_analysis,
                gpt_review,
                gemini_suggestions,
                file_path
            )
            
            # Mise à jour des statistiques
            self.stats['files_processed'] += 1
            self.stats['total_todos'] += len(todos)
            
            return {
                'file': file_path,
                'claude_analysis': claude_analysis,
                'gpt_review': gpt_review,
                'gemini_suggestions': gemini_suggestions,
                'todos': todos
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse de {file_path}: {str(e)}")
            self.stats['errors'] += 1
            return {
                'file': file_path,
                'error': str(e)
            }
    
    async def analyze_project(self, project_path: str) -> List[Dict]:
        """
        Analyse un projet complet.
        
        Args:
            project_path (str): Chemin du projet à analyser
            
        Returns:
            List[Dict]: Résultats de l'analyse
        """
        try:
            # Vérification du projet
            if not os.path.exists(project_path):
                raise FileNotFoundError(f"Projet non trouvé: {project_path}")
            
            # Recherche des fichiers à analyser
            files_to_analyze = []
            for root, _, files in os.walk(project_path):
                for file in files:
                    if file.endswith(('.py', '.js', '.java', '.cpp', '.h', '.hpp')):
                        file_path = os.path.join(root, file)
                        if file_path not in self.processed_files:
                            files_to_analyze.append(file_path)
            
            # Analyse des fichiers
            results = []
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Analyse en cours...", total=len(files_to_analyze))
                
                for file_path in files_to_analyze:
                    result = await self.analyze_file(file_path)
                    results.append(result)
                    self.processed_files.add(file_path)
                    progress.update(task, advance=1)
            
            return results
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse du projet: {str(e)}")
            raise
    
    def generate_report(self, results: List[Dict], output_dir: str = "analysis_reports"):
        """
        Génère les rapports d'analyse.
        
        Args:
            results (List[Dict]): Résultats de l'analyse
            output_dir (str): Dossier de sortie
        """
        try:
            # Création du dossier de sortie
            os.makedirs(output_dir, exist_ok=True)
            
            # Génération des rapports par fichier
            for result in results:
                if 'error' in result:
                    continue
                
                file_name = os.path.basename(result['file'])
                base_name = os.path.splitext(file_name)[0]
                
                # Rapport Claude
                claude_report = os.path.join(output_dir, f"{file_name}_claude_analysis.md")
                with open(claude_report, 'w', encoding='utf-8') as f:
                    f.write(result['claude_analysis'])
                
                # Rapport GPT
                gpt_report = os.path.join(output_dir, f"{file_name}_chatgpt_review.md")
                with open(gpt_report, 'w', encoding='utf-8') as f:
                    f.write(result['gpt_review'])
                
                # Suggestions Gemini
                gemini_report = os.path.join(output_dir, f"{file_name}_gemini_suggestions.md")
                with open(gemini_report, 'w', encoding='utf-8') as f:
                    f.write(result['gemini_suggestions'])
            
            # Rapport global
            self._generate_global_report(results, output_dir)
            
            logger.info(f"Rapports générés dans {output_dir}")
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération des rapports: {str(e)}")
            raise
    
    def _generate_global_report(self, results: List[Dict], output_dir: str):
        """
        Génère le rapport global du projet.
        
        Args:
            results (List[Dict]): Résultats de l'analyse
            output_dir (str): Dossier de sortie
        """
        try:
            # Création du rapport
            report = []
            report.append("# Rapport d'Analyse Global du Projet\n")
            report.append(f"*Généré le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
            
            # Statistiques
            report.append("## Statistiques\n")
            report.append(f"- Fichiers analysés: {self.stats['files_processed']}")
            report.append(f"- Tâches TODO identifiées: {self.stats['total_todos']}")
            report.append(f"- Erreurs rencontrées: {self.stats['errors']}")
            report.append(f"- Temps d'exécution: {time.time() - self.stats['start_time']:.2f} secondes\n")
            
            # Résumé par fichier
            report.append("## Résumé par Fichier\n")
            for result in results:
                if 'error' in result:
                    report.append(f"### {result['file']} (Erreur)")
                    report.append(f"Erreur: {result['error']}\n")
                else:
                    report.append(f"### {result['file']}")
                    report.append(f"- TODOs: {len(result['todos'])}")
                    report.append(f"- Analyse Claude: {len(result['claude_analysis'].split())} mots")
                    report.append(f"- Review GPT: {len(result['gpt_review'].split())} mots")
                    report.append(f"- Suggestions Gemini: {len(result['gemini_suggestions'].split())} mots\n")
            
            # Écriture du rapport
            report_path = os.path.join(output_dir, "master_project_analysis_report.md")
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(report))
            
            # Conversion en HTML
            self._convert_to_html(report_path)
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du rapport global: {str(e)}")
            raise
    
    def _convert_to_html(self, markdown_path: str):
        """
        Convertit le rapport Markdown en HTML.
        
        Args:
            markdown_path (str): Chemin du fichier Markdown
        """
        try:
            import markdown
            with open(markdown_path, 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            html_content = markdown.markdown(
                md_content,
                extensions=['extra', 'codehilite', 'tables']
            )
            
            # Ajout du style
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Rapport d'Analyse</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    h1 {{ color: #2c3e50; }}
                    h2 {{ color: #34495e; margin-top: 30px; }}
                    h3 {{ color: #7f8c8d; }}
                    pre {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; }}
                    code {{ background-color: #f8f9fa; padding: 2px 5px; border-radius: 3px; }}
                    table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f8f9fa; }}
                </style>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """
            
            html_path = markdown_path.replace('.md', '.html')
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
        except Exception as e:
            logger.error(f"Erreur lors de la conversion en HTML: {str(e)}")
            raise

@click.command()
@click.argument('project_path', type=click.Path(exists=True))
@click.option('--verbose', '-v', is_flag=True, help='Mode verbeux')
@click.option('--output', '-o', default='analysis_reports', help='Dossier de sortie')
@click.option('--format', '-f', type=click.Choice(['markdown', 'html', 'json']), default='markdown', help='Format de sortie')
def main(project_path: str, verbose: bool, output: str, format: str):
    """
    Agent d'analyse de code multi-LLM.
    
    PROJECT_PATH: Chemin vers le projet à analyser
    """
    try:
        # Configuration du logging
        if verbose:
            logger.setLevel(logging.DEBUG)
        
        # Initialisation de l'agent
        agent = LLMCodeAgent()
        
        # Analyse du projet
        results = asyncio.run(agent.analyze_project(project_path))
        
        # Génération des rapports
        agent.generate_report(results, output)
        
        # Affichage des statistiques
        console.print(Panel.fit(
            f"[green]Analyse terminée avec succès![/green]\n"
            f"Fichiers analysés: {agent.stats['files_processed']}\n"
            f"Tâches TODO: {agent.stats['total_todos']}\n"
            f"Erreurs: {agent.stats['errors']}\n"
            f"Temps: {time.time() - agent.stats['start_time']:.2f}s",
            title="Résultats"
        ))
        
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
