#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module de scan de fichiers pour l'agent d'analyse de code multi-LLM.
Ce module est responsable de la recherche et du filtrage des fichiers à analyser.
"""

import os
import logging
from pathlib import Path

logger = logging.getLogger('llm_code_agent.file_scanner')

class FileScanner:
    """
    Classe responsable de la recherche et du filtrage des fichiers à analyser.
    """
    
    def __init__(self):
        """Initialise le scanner de fichiers avec les extensions supportées."""
        # Extensions de fichiers supportées pour l'analyse
        self.supported_extensions = [
            '.py',   # Python
            '.js',   # JavaScript
            '.ts',   # TypeScript
            '.tsx',  # TypeScript React
            '.jsx',  # JavaScript React
            '.html', # HTML
            '.css',  # CSS
            '.json', # JSON
            '.md'    # Markdown
        ]
        
        # Dossiers à ignorer lors du scan
        self.ignored_dirs = [
            'node_modules',
            'venv',
            '.git',
            '__pycache__',
            '.vscode',
            '.idea',
            'dist',
            'build',
            'env'
        ]
        
        logger.debug(f"Scanner initialisé avec {len(self.supported_extensions)} extensions supportées")
    
    def scan_directory(self, directory_path):
        """
        Parcourt récursivement un répertoire et retourne les chemins des fichiers à analyser.
        
        Args:
            directory_path (str): Chemin du répertoire à scanner
            
        Returns:
            list: Liste des chemins de fichiers à analyser
        """
        directory_path = os.path.abspath(directory_path)
        logger.info(f"Scan du répertoire: {directory_path}")
        
        if not os.path.isdir(directory_path):
            logger.error(f"Le chemin spécifié n'est pas un répertoire valide: {directory_path}")
            return []
        
        files_to_analyze = []
        
        for root, dirs, files in os.walk(directory_path):
            # Filtrer les dossiers ignorés
            dirs[:] = [d for d in dirs if d not in self.ignored_dirs]
            
            for file in files:
                file_path = os.path.join(root, file)
                file_extension = os.path.splitext(file)[1].lower()
                
                if file_extension in self.supported_extensions:
                    files_to_analyze.append(file_path)
                    logger.debug(f"Fichier ajouté pour analyse: {file_path}")
        
        logger.info(f"{len(files_to_analyze)} fichiers trouvés pour analyse")
        return files_to_analyze
    
    def is_supported_file(self, file_path):
        """
        Vérifie si un fichier est supporté pour l'analyse.
        
        Args:
            file_path (str): Chemin du fichier à vérifier
            
        Returns:
            bool: True si le fichier est supporté, False sinon
        """
        if not os.path.isfile(file_path):
            return False
        
        file_extension = os.path.splitext(file_path)[1].lower()
        return file_extension in self.supported_extensions
    
    def get_file_type(self, file_path):
        """
        Détermine le type de fichier en fonction de son extension.
        
        Args:
            file_path (str): Chemin du fichier
            
        Returns:
            str: Type de fichier (python, javascript, etc.)
        """
        file_extension = os.path.splitext(file_path)[1].lower()
        
        extension_to_type = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript_react',
            '.jsx': 'javascript_react',
            '.html': 'html',
            '.css': 'css',
            '.json': 'json',
            '.md': 'markdown'
        }
        
        return extension_to_type.get(file_extension, 'unknown')
    
    def get_file_stats(self, file_path):
        """
        Récupère des statistiques sur un fichier.
        
        Args:
            file_path (str): Chemin du fichier
            
        Returns:
            dict: Statistiques du fichier (taille, nombre de lignes, etc.)
        """
        if not os.path.isfile(file_path):
            return None
        
        stats = {
            'path': file_path,
            'name': os.path.basename(file_path),
            'type': self.get_file_type(file_path),
            'size': os.path.getsize(file_path),
            'last_modified': os.path.getmtime(file_path)
        }
        
        # Compter le nombre de lignes
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                stats['line_count'] = sum(1 for _ in f)
        except Exception as e:
            logger.warning(f"Impossible de compter les lignes dans {file_path}: {str(e)}")
            stats['line_count'] = 0
        
        return stats

# Test unitaire simple si exécuté directement
if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    
    if len(sys.argv) > 1:
        test_dir = sys.argv[1]
    else:
        test_dir = "."
    
    scanner = FileScanner()
    files = scanner.scan_directory(test_dir)
    
    print(f"Fichiers trouvés ({len(files)}):")
    for file in files:
        stats = scanner.get_file_stats(file)
        print(f"- {stats['name']} ({stats['type']}, {stats['line_count']} lignes)")
