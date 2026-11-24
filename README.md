\# ClubISET



Gestion d'un club étudiant : membres, cotisations, événements et inscriptions.



\## Démarrage en une commande



Prérequis : Docker Desktop.



Première fois seulement, créer le fichier de configuration (puis choisir un mot de passe dedans) :



&#x20;   copy .env.example .env



Démarrer l'application et sa base PostgreSQL :



&#x20;   docker compose up -d --build --wait



Vérifier : http://localhost:5000/health



Arrêter (les données sont conservées dans un volume) :



&#x20;   docker compose down



\## Développement local sans Docker



&#x20;   python -m venv .venv

&#x20;   .venv\\Scripts\\Activate.ps1

&#x20;   pip install -r requirements.txt

&#x20;   ./scripts/check.sh

