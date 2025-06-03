# LLM Destekli Kod Analiz ve Refaktör Ajanı

Un agent d'analyse de code multi-LLM qui utilise Claude 3, GPT-4 et Gemini Pro pour analyser des projets logiciels, détecter des erreurs et proposer des améliorations.

## 📋 Présentation

Cet outil CLI Python analyse automatiquement votre code source à l'aide de trois modèles LLM différents :

1. **Claude 3 (Anthropic)** : Analyse initiale du code
2. **GPT-4/GPT-4o (OpenAI)** : Validation et suggestions d'amélioration
3. **Gemini Pro (Google)** : Refactoring avancé et suggestions d'architecture

Pour chaque fichier analysé, l'agent génère trois rapports distincts et maintient une liste TODO persistante des problèmes à résoudre.

## ✨ Fonctionnalités

- 🔍 **Analyse complète de projets** : Scan récursif des répertoires
- 🤖 **Support multi-LLM** : Trois modèles complémentaires pour une analyse approfondie
- 📊 **Rapports détaillés** : Analyse par fichier et rapport global du projet
- ✅ **Liste TODO persistante** : Suivi des problèmes et améliorations à apporter
- 📄 **Export HTML et Markdown** : Rapports dans plusieurs formats
- 🧩 **Architecture modulaire** : Facilement extensible

## 🛠️ Installation

### Prérequis

- Python 3.11 ou supérieur
- Clés API pour Anthropic (Claude), OpenAI (GPT) et Google (Gemini)

### Étapes d'installation

1. Clonez ce dépôt :
   ```bash
   git clone https://github.com/votre-utilisateur/llm_code_agent.git
   cd llm_code_agent
   ```

2. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

3. Configurez vos clés API :
   ```bash
   cp .env.example .env
   ```
   Puis modifiez le fichier `.env` pour y ajouter vos clés API.

## 🚀 Utilisation

### Analyser un projet complet

```bash
python llm_code_agent.py /chemin/vers/votre/projet
```

### Analyser un fichier spécifique

```bash
python llm_code_agent.py /chemin/vers/votre/projet -f chemin/relatif/fichier.py
```

### Options disponibles

- `-f, --file` : Analyser un fichier spécifique au lieu du projet entier
- `-v, --verbose` : Afficher des informations détaillées pendant l'exécution

## 📂 Structure des sorties

L'agent génère les fichiers et dossiers suivants :

- `analysis_reports/` : Analyses détaillées par Claude
- `refactoring_suggestions/` : Suggestions de ChatGPT et Gemini
- `master_project_analysis_report.md` : Rapport global du projet
- `master_project_analysis_report.html` : Version HTML du rapport global
- `project_todo.json` : Liste persistante des tâches à effectuer

## 🧪 Tests

Pour tester l'agent sur un petit projet exemple :

```bash
python test_agent.py
```

Ce script crée un projet de test avec quelques fichiers contenant des problèmes intentionnels, puis exécute l'agent dessus.

## 📚 Architecture du projet

```
llm_code_agent/
├── llm_code_agent.py                ← Fichier principal CLI
├── .env                             ← API keys (à créer)
├── .env.example                     ← Exemple de fichier .env
├── requirements.txt                 ← Dépendances Python
├── test_agent.py                    ← Script de test
├── project_todo.json                ← Liste des tâches persistante
├── analysis_reports/                ← Rapports Claude
├── refactoring_suggestions/         ← Sorties ChatGPT + Gemini
└── utils/
    ├── claude_agent.py              ← Intégration avec Claude
    ├── chatgpt_agent.py             ← Intégration avec GPT
    ├── gemini_agent.py              ← Intégration avec Gemini
    ├── file_scanner.py              ← Scanner de fichiers
    ├── todo_manager.py              ← Gestionnaire de tâches
    └── html_exporter.py             ← Exportation HTML
```

## 🔄 Flux de travail

1. **Scan du projet** : Identification des fichiers à analyser
2. **Analyse avec Claude** : Analyse initiale du code
3. **Validation avec GPT** : Vérification et suggestions
4. **Refactoring avec Gemini** : Suggestions avancées
5. **Génération des rapports** : Création des fichiers Markdown et HTML
6. **Extraction des TODOs** : Mise à jour de la liste des tâches

## 🛡️ Sécurité

- Les clés API sont stockées dans un fichier `.env` local
- Aucune donnée n'est partagée en dehors des appels API nécessaires
- Le code analysé reste sur votre machine

## 🔮 Fonctionnalités futures

- 🧠 Système de mémoire persistante
- 🌐 Intégration avec Webhook/Slack/Email
- 🌍 Support multilingue (Turc/Anglais)
- 🔌 Architecture de plugins

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🙏 Remerciements

- Anthropic pour l'API Claude
- OpenAI pour l'API GPT
- Google pour l'API Gemini

---

Développé par Manus - Juin 2025
