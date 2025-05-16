# Projekt CI/CD – Automatyczna aplikacja agregująca dane z API OpenWeather, generująca raporty PDF i zapisująca je do AWS S3

## Cel projektu

Celem projektu jest stworzenie kompletnej infrastruktury chmurowej oraz aplikacji webowej, która:

* automatycznie agreguje dane z publicznego API (np. pogody lub kursów walut),
* zapisuje te dane w bazie danych (PostgreSQL),
* generuje raporty PDF z danych i przesyła je do S3,
* udostępnia prosty interfejs webowy zrealizowany we Flasku,
* całość jest zautomatyzowana z użyciem CI/CD w Jenkinsie oraz infrastruktury jako kod (Terraform + Ansible),
* zapewnia monitoring działania aplikacji za pomocą Prometheus + Grafana. (opcjonalnie)

## Architektura i komponenty

* Infra VM (EC2): maszyna inicjalna z Jenkinsem Master i plikami projektu.
* App VM (EC2): maszyna z uruchomioną aplikacją (Docker + Flask + PostgreSQL + Fetcher + Reporter).
* AWS S3: przechowywanie wygenerowanych raportów PDF.
* AWS RDS (PostgreSQL): baza danych do przechowywania danych z API.
* Jenkins CI/CD: pełny pipeline automatyzujący provisioning, konfigurację i deployment.
* Terraform: tworzenie infrastruktury (EC2, RDS, S3).
* Ansible: konfiguracja maszyn EC2 (App VM).
* Docker + Docker Compose: uruchamianie aplikacji.
* Prometheus + Grafana: monitoring działania aplikacji (opcjonalne rozszerzenie).

## Struktura plików projektu

project/
│
├── terraform/
│   ├── main.tf              # Tworzy App VM, RDS, S3
│   ├── variables.tf         # Zmienne konfiguracyjne (np. region, VM name)
│   ├── outputs.tf           # Outputy (np. publiczny IP App VM)
│   └── terraform.tfvars     # Wartości zmiennych
│
├── ansible/
│   ├── setup_app.yml        # Instalacja Dockera, Pythona, agenta Jenkins, AWS CLI
│   ├── deploy_app.yml       # Przesyłanie plików i uruchamianie docker-compose
│   ├── inventory            # Tymczasowy inventory (np. dynamiczny IP App VM)
│
├── app/
│   ├── docker-compose.yml   # Uruchamia flask-app, fetcher, reporter, postgres
│   ├── flask-app/
│   │   ├── app.py           # Aplikacja Flask
│   │   └── templates/
│   │       └── index.html   # Prosty interfejs
│   ├── fetcher/
│   │   └── fetcher.py       # Pobiera dane z API i zapisuje do bazy
│   ├── reporter/
│   │   └── report_generator.py  # Generuje PDF z danych i wrzuca do S3
│   └── requirements.txt     # Wspólne zależności
│
├── jenkins/
│   ├── jenkins.yaml         # JCasC – konfiguracja Jenkinsa
│   └── pipeline.groovy      # Pipeline definiujący cały workflow
│
├── monitoring/ (opcjonalnie)
│   ├── prometheus.yml       # Konfiguracja Prometheus
│   ├── docker-compose.yml   # Prometheus + Grafana
│
└── README.md                # Ten plik


## Workflow działania projektu (krok po kroku):

###  1. Przygotowanie Infra VM (z zainstalowanym Jenkins):

* Instalacja: Jenkins, Git, Terraform, Ansible, Docker, AWS CLI.
* Jenkins skonfigurowany przez plik `jenkins/jenkins.yaml` (JCasC).
* Pipeline `pipeline.groovy` dostępny z GUI.

###  2. Uruchomienie pipeline z GUI Jenkinsa

#### 2.1. Provisioning (Terraform)

* Jenkins job uruchamia `terraform/`:
- Tworzy App VM (EC2),
- Tworzy RDS (PostgreSQL),
- Tworzy S3 bucket.

* Publiczny IP App VM jest zapisywany jako output.

#### 2.2. Konfiguracja (Ansible)

* Ansible (uruchamiany z Jenkinsa) łączy się z App VM po IP.
* Instaluje:
- Docker + Docker Compose,
- agenta Jenkins,
- Flask, AWS CLI, zależności.

#### 2.3. Deploy (Docker)

* Pliki aplikacji `app/` przesyłane na App VM.
* Uruchamiany `docker-compose up -d`.

#### 2.4. Aplikacja

* Fetcher.py (uruchamiany co godzinę przez cron lub Jenkinsa) pobiera dane z API i zapisuje je do bazy.
* report_generator.py generuje PDF z danych z bazy i zapisuje plik do S3.
* Flask pokazuje aktualne dane i historię raportów.

##  Zmienne i konfiguracja

aws_region = "eu-central-1"
app_vm_name = "AppVM"
instance_type = "t2.micro"

Możesz te wartości również ustawiać dynamicznie jako parametry pipeline w Jenkinsie.


##  Monitoring (opcjonalnie)

Można uruchomić dodatkowy docker-compose z Prometheus + Grafana na App VM lub osobnym hoście.

Prometheus będzie zbierał dane np. z Flask lub fetchera (metryki HTTP).

Grafana pokaże je w panelu webowym.

