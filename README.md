# LLM Code Agent

Un agent d'analyse de code multi-LLM qui utilise Claude, ChatGPT et Gemini pour analyser et suggérer des améliorations pour votre code.

## Fonctionnalités

- Analyse de code avec trois modèles de langage différents (Claude, ChatGPT, Gemini)
- Suggestions de refactorisation avancées
- Extraction et gestion des tâches TODO
- Génération de rapports d'analyse détaillés
- Support pour plusieurs langages de programmation
- Interface en ligne de commande intuitive

## Prérequis

- Python 3.8 ou supérieur
- Clés API pour:
  - Anthropic Claude
  - OpenAI ChatGPT
  - Google Gemini

## Installation

1. Clonez le dépôt:
```bash
git clone https://github.com/lekesiz/llm_code_agent.git
cd llm_code_agent
```

2. Installez les dépendances:
```bash
pip install -r requirements.txt
```

3. Configurez les clés API:
```bash
cp .env.example .env
```
Puis éditez le fichier `.env` avec vos clés API.

## Utilisation

### Analyse d'un projet

```bash
python llm_code_agent.py /chemin/vers/votre/projet
```

Options disponibles:
- `-v, --verbose`: Mode verbeux
- `-o, --output`: Dossier de sortie personnalisé
- `-l, --language`: Langage de programmation spécifique
- `-f, --format`: Format de sortie (markdown, html, json)

### Analyse d'un fichier unique

```bash
python llm_code_agent.py /chemin/vers/fichier.py --single-file
```

### Génération de rapports

```bash
python llm_code_agent.py /chemin/vers/projet --report
```

## Structure du Projet

```
llm_code_agent/
├── llm_code_agent.py      # Script principal
├── requirements.txt       # Dépendances Python
├── .env.example          # Exemple de configuration
├── utils/                # Utilitaires
│   ├── claude_agent.py   # Agent Claude
│   ├── gpt_agent.py      # Agent ChatGPT
│   ├── gemini_agent.py   # Agent Gemini
│   └── todo_manager.py   # Gestionnaire de TODOs
├── analysis_reports/     # Rapports d'analyse
└── refactoring_suggestions/ # Suggestions de refactorisation
```

## Format des Rapports

### Rapport d'Analyse Claude

```markdown
# Analyse de Code - Claude

## Résumé
[Synthèse de l'analyse]

## Points Forts
- [Liste des points forts]

## Points à Améliorer
- [Liste des améliorations suggérées]

## Recommandations
- [Recommandations détaillées]
```

### Suggestions de Refactorisation

```markdown
# Suggestions de Refactorisation

## Améliorations Prioritaires
- [Liste des améliorations prioritaires]

## Optimisations
- [Suggestions d'optimisation]

## Bonnes Pratiques
- [Recommandations de bonnes pratiques]
```

## Gestion des TODOs

Les tâches TODO sont extraites des analyses et stockées dans `project_todo.json`:

```json
{
  "todos": [
    {
      "id": "todo_1234567890_1",
      "description": "Refactoriser la méthode X",
      "priority": "Élevée",
      "effort": "Moyen",
      "file": "example.py",
      "source": "Claude",
      "timestamp": 1234567890,
      "completed": false
    }
  ]
}
```

## Tests

Exécutez les tests unitaires:

```bash
python test_agent.py
```

## Contribution

1. Fork le projet
2. Créez une branche pour votre fonctionnalité
3. Committez vos changements
4. Poussez vers la branche
5. Ouvrez une Pull Request

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## Support

Pour toute question ou problème, veuillez ouvrir une issue sur GitHub.

## Auteurs

- [Mikail Lekesiz](https://github.com/lekesiz)

## Remerciements

- Anthropic pour Claude
- OpenAI pour ChatGPT
- Google pour Gemini
