#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module d'exportation HTML pour l'agent d'analyse de code multi-LLM.
Ce module est responsable de la conversion des rapports Markdown en HTML.
"""

import os
import logging
import markdown
from pathlib import Path

logger = logging.getLogger('llm_code_agent.html_exporter')

class HTMLExporter:
    """
    Classe responsable de la conversion des rapports Markdown en HTML.
    """
    
    def __init__(self):
        """Initialise l'exportateur HTML avec les styles par défaut."""
        self.css_style = """
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f9f9f9;
        }
        
        h1, h2, h3, h4, h5, h6 {
            color: #2c3e50;
            margin-top: 24px;
            margin-bottom: 16px;
            font-weight: 600;
        }
        
        h1 {
            font-size: 2em;
            border-bottom: 1px solid #eaecef;
            padding-bottom: 0.3em;
        }
        
        h2 {
            font-size: 1.5em;
            border-bottom: 1px solid #eaecef;
            padding-bottom: 0.3em;
        }
        
        h3 {
            font-size: 1.25em;
        }
        
        a {
            color: #0366d6;
            text-decoration: none;
        }
        
        a:hover {
            text-decoration: underline;
        }
        
        pre {
            background-color: #f6f8fa;
            border-radius: 3px;
            padding: 16px;
            overflow: auto;
            font-family: 'Courier New', Courier, monospace;
        }
        
        code {
            background-color: #f6f8fa;
            border-radius: 3px;
            padding: 0.2em 0.4em;
            font-family: 'Courier New', Courier, monospace;
        }
        
        blockquote {
            border-left: 4px solid #dfe2e5;
            padding: 0 1em;
            color: #6a737d;
            margin: 0;
        }
        
        table {
            border-collapse: collapse;
            width: 100%;
            margin-bottom: 16px;
        }
        
        table, th, td {
            border: 1px solid #dfe2e5;
        }
        
        th, td {
            padding: 8px 16px;
            text-align: left;
        }
        
        th {
            background-color: #f6f8fa;
        }
        
        tr:nth-child(even) {
            background-color: #f6f8fa;
        }
        
        .priority-critical {
            color: #d73a49;
            font-weight: bold;
        }
        
        .priority-high {
            color: #e36209;
            font-weight: bold;
        }
        
        .priority-medium {
            color: #0366d6;
        }
        
        .priority-low {
            color: #2ea44f;
        }
        
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .header-title {
            margin: 0;
        }
        
        .header-meta {
            font-size: 0.9em;
            color: #6a737d;
        }
        
        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #eaecef;
            text-align: center;
            font-size: 0.9em;
            color: #6a737d;
        }
        """
        
        logger.info("Exportateur HTML initialisé")
    
    def convert_to_html(self, markdown_file, html_file=None):
        """
        Convertit un fichier Markdown en HTML.
        
        Args:
            markdown_file (str): Chemin du fichier Markdown à convertir
            html_file (str, optional): Chemin du fichier HTML de sortie
            
        Returns:
            str: Chemin du fichier HTML généré
        """
        if not os.path.isfile(markdown_file):
            logger.error(f"Le fichier Markdown {markdown_file} n'existe pas")
            return None
        
        # Si le fichier HTML n'est pas spécifié, utiliser le même nom avec l'extension .html
        if html_file is None:
            html_file = os.path.splitext(markdown_file)[0] + '.html'
        
        try:
            # Lecture du contenu Markdown
            with open(markdown_file, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
            
            # Conversion en HTML
            html_content = markdown.markdown(
                markdown_content,
                extensions=[
                    'markdown.extensions.tables',
                    'markdown.extensions.fenced_code',
                    'markdown.extensions.codehilite',
                    'markdown.extensions.toc'
                ]
            )
            
            # Ajout des styles CSS et de la structure HTML complète
            full_html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{os.path.basename(markdown_file)}</title>
    <style>
{self.css_style}
    </style>
</head>
<body>
    <div class="header">
        <h1 class="header-title">Rapport d'analyse de code</h1>
        <div class="header-meta">
            Généré le {self._get_current_date()}
        </div>
    </div>
    
    {html_content}
    
    <div class="footer">
        <p>Généré par LLM Destekli Kod Analiz ve Refaktör Ajanı</p>
    </div>
</body>
</html>"""
            
            # Écriture du fichier HTML
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(full_html)
            
            logger.info(f"Conversion de {markdown_file} en {html_file} réussie")
            return html_file
            
        except Exception as e:
            logger.error(f"Erreur lors de la conversion de {markdown_file} en HTML: {str(e)}")
            return None
    
    def _get_current_date(self):
        """
        Retourne la date actuelle au format lisible.
        
        Returns:
            str: Date actuelle au format lisible
        """
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def apply_custom_style(self, css_file):
        """
        Applique un style CSS personnalisé.
        
        Args:
            css_file (str): Chemin du fichier CSS personnalisé
            
        Returns:
            bool: True si le style a été appliqué avec succès, False sinon
        """
        if not os.path.isfile(css_file):
            logger.error(f"Le fichier CSS {css_file} n'existe pas")
            return False
        
        try:
            with open(css_file, 'r', encoding='utf-8') as f:
                self.css_style = f.read()
            
            logger.info(f"Style CSS personnalisé appliqué depuis {css_file}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'application du style CSS personnalisé: {str(e)}")
            return False
    
    def batch_convert(self, markdown_dir, html_dir=None):
        """
        Convertit tous les fichiers Markdown d'un répertoire en HTML.
        
        Args:
            markdown_dir (str): Chemin du répertoire contenant les fichiers Markdown
            html_dir (str, optional): Chemin du répertoire de sortie pour les fichiers HTML
            
        Returns:
            int: Nombre de fichiers convertis avec succès
        """
        if not os.path.isdir(markdown_dir):
            logger.error(f"Le répertoire {markdown_dir} n'existe pas")
            return 0
        
        # Si le répertoire HTML n'est pas spécifié, utiliser le même répertoire
        if html_dir is None:
            html_dir = markdown_dir
        else:
            # Créer le répertoire s'il n'existe pas
            os.makedirs(html_dir, exist_ok=True)
        
        # Recherche des fichiers Markdown
        markdown_files = [f for f in os.listdir(markdown_dir) if f.endswith('.md')]
        
        if not markdown_files:
            logger.warning(f"Aucun fichier Markdown trouvé dans {markdown_dir}")
            return 0
        
        # Conversion de chaque fichier
        success_count = 0
        for md_file in markdown_files:
            md_path = os.path.join(markdown_dir, md_file)
            html_path = os.path.join(html_dir, os.path.splitext(md_file)[0] + '.html')
            
            if self.convert_to_html(md_path, html_path):
                success_count += 1
        
        logger.info(f"{success_count}/{len(markdown_files)} fichiers Markdown convertis en HTML")
        return success_count

# Test unitaire simple si exécuté directement
if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    
    if len(sys.argv) > 1:
        test_file = sys.argv[1]
        
        if os.path.isfile(test_file) and test_file.endswith('.md'):
            exporter = HTMLExporter()
            html_file = exporter.convert_to_html(test_file)
            
            if html_file:
                print(f"Conversion réussie: {test_file} -> {html_file}")
        else:
            print(f"Le fichier {test_file} n'existe pas ou n'est pas un fichier Markdown.")
    else:
        print("Usage: python html_exporter.py <fichier_markdown>")
