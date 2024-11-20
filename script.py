import os
import yaml

# Fonction pour générer un volume unique par service
def generate_volumes(service_name):
    return f"postgres_data_{service_name}"

# Fonction pour générer un port libre pour le service (app ou db)
def get_free_port(used_ports, start_port, end_port):
    # Trouver un port libre dans la plage définie
    for port in range(start_port, end_port + 1):
        if port not in used_ports:
            return port
    raise ValueError(f"Aucun port libre disponible dans la plage spécifiée ({start_port}-{end_port}).")

# Fonction pour lire le fichier docker-compose et obtenir les bons noms
def read_service_docker_compose(service_path):
    compose_file = os.path.join(service_path, 'docker-compose.yml')
    if os.path.exists(compose_file):
        with open(compose_file, 'r') as f:
            docker_compose = yaml.safe_load(f)
            # Extraire les noms des services dans le fichier docker-compose
            db_service_name = next((key for key in docker_compose['services'] if key.startswith('db-')), None)
            app_service_name = next((key for key in docker_compose['services'] if key != db_service_name), None)
            if not db_service_name or not app_service_name:
                raise ValueError(f"Le fichier docker-compose de {service_path} doit définir 'container_name' pour les services 'app' et 'db'.")
            return app_service_name, db_service_name
    else:
        raise FileNotFoundError(f"Le fichier docker-compose.yml est introuvable dans {service_path}.")

# Fonction pour générer la partie services d'un docker-compose
def generate_services(service_name, service_path, used_ports):
    app_service_name, db_service_name = read_service_docker_compose(service_path)
    
    # Générer un port libre pour le service (application)
    app_port = get_free_port(used_ports, 8000, 8099)
    
    # Générer un port libre pour la base de données
    db_port = get_free_port(used_ports, 5432, 5449)
    
    db_service = {
        "image": "postgres:13",
        "container_name": db_service_name,
        "ports": [
            f"{db_port}:5432"
        ],
        "volumes": [
            f"{generate_volumes(service_name)}:/var/lib/postgresql/data",
            f"{os.path.join(service_path, '.env')}:/app/.env",  # .env du service
            f"{os.path.join(service_path, 'docker/entrypoint_db.sh')}:/app/docker/entrypoint_db.sh"  # entrypoint_db.sh
        ],
        "entrypoint": ["/app/docker/entrypoint_db.sh"]
    }
    
    app_service = {
        "build": {
            "context": os.path.join(service_path, 'docker')  # Dockerfile pour le service
        },
        "container_name": app_service_name,
        "ports": [
            f"{app_port}:8000"
        ],
        "volumes": [
            f"{os.path.join(service_path)}:/app",  # Monter tout le répertoire du service
            f"{os.path.join(service_path, 'docker')}:/app/docker"  # Monter le répertoire docker
        ],
        "environment": [
            "PYTHONUNBUFFERED=1",
            "DEBUG=True"
        ],
        "env_file": [
            f"{os.path.join(service_path, '.env')}"  # Fichier .env spécifique pour ce service
        ],
        "entrypoint": ["/app/docker/entrypoint_dev.sh"],
        "depends_on": [
            db_service_name
        ]
    }
    
    return db_service, app_service, app_port, db_port

# Fonction pour générer le docker-compose.yml complet
def generate_docker_compose(services_dir, output_file='docker-compose.yml'):
    services = {}
    volumes = {}
    used_ports = set()  # Ensemble des ports déjà utilisés

    # Si le fichier docker-compose.yml existe déjà, lisez les ports utilisés
    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            docker_compose = yaml.safe_load(f)
            # Extraire les ports utilisés dans les services existants
            for service in docker_compose.get('services', {}).values():
                if 'ports' in service:
                    for port_mapping in service['ports']:
                        used_ports.add(int(port_mapping.split(":")[0]))

    # Parcourir les dossiers des services
    for service_name in os.listdir(services_dir):
        service_path = os.path.join(services_dir, service_name)

        # Ignorer les répertoires indésirables comme .git, .idea, etc.
        if service_name.startswith('.') or not os.path.isdir(service_path):
            continue

        # Vérifier si le dossier contient un service valide
        try:
            db_service, app_service, app_port, db_port = generate_services(service_name, service_path, used_ports)
            services[db_service['container_name']] = db_service
            services[app_service['container_name']] = app_service
            volumes[generate_volumes(service_name)] = {}

            # Ajouter les ports utilisés pour le prochain service
            used_ports.add(app_port)
            used_ports.add(db_port)

            print(f"Service pris en compte: {service_name}")
            print(f"  Base de données: {db_service['container_name']} sur le port {db_port}")
            print(f"  Application: {app_service['container_name']} sur le port {app_port}")

        except Exception as e:
            print(f"Erreur dans le répertoire {service_path}: {e}")

    # Structure finale du docker-compose
    docker_compose = {
        'services': services,
        'volumes': volumes
    }

    # Écrire dans le fichier output_file
    with open(output_file, 'w') as f:
        yaml.dump(docker_compose, f, default_flow_style=False)

    print(f"docker-compose.yml généré avec succès dans {output_file}")

# Chemin du répertoire contenant vos services
services_dir = './'  # Exemple, modifiez si nécessaire

# Générer le docker-compose.yml
generate_docker_compose(services_dir)
