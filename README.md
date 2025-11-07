# StreamEvents

Aplicació Django per gestionar esdeveniments i usuaris
(extensible): base educativa amb bones practiques
(entorns, estructura, separació de templates/static,
etc.). Conté un sistema complet d'autenticació i gestió de perfils.
Permet als usuaris registrar-se, iniciar sessió 
i gestionar els seus perfils.


---

## ✨ Objectius
- Practicar un projecte Django modular.
- Treballar amb un usuari personalitzat (app users).
- Organitzar templates, estàtics i media correctament.
- Introduir fitxers d'entorn (.env) i bones practiques
Git.
- Preparar el terreny per a futures funcionalitats (API,
auth avançada, etc.).

---

## 🧱 Stack Principal
- Python 3.13
- Django 5.x
- SQLite (per defecte) / MongoDB (opcional via Djongo)
- HTML, CSS i JS (templates i estàtics)
- Git & GitHub (control de versions)

---

## 📂 Estructura Simplificada
streamevents/
│── config/ # Configuració principal (settings, urls, etc.)
│── users/ # App personalitzada d'usuaris
│── templates/ # Plantilles globals (base.html, layouts, etc.)
│── static/ # Fitxers estàtics (css, js, img)
│── media/ # Pujades d’usuari (IGNORAT al Git)
│── fixtures/ # (Opcional) JSON amb dades d'exemple
│── seeds/ # (Opcional) Scripts per omplir dades
│── requirements.txt # Dependències del projecte
│── .env # Variables d’entorn (privat)
│── env.example # Exemple d’entorn (sense secrets)
│── README.md # Documentació del projecte

---

## ✅ Requisits previs
- Python 3.13 instal·lat
- Git instal·lat
- Entorn virtual creat (`python -m venv venv`)

---

## 🚀 Instal·lació ràpida

### Clonar el repositori
`git clone https://github.com/jasonokoro10/streamevents.git`
`cd streamevents`

### Activar l'entorn virtual
`.\venv\Scripts\activate`   # Windows
`source venv/bin/activate`  # Linux/Mac

### Instal·lar dependències
`pip install -r requirements.txt`

### Migracions i superusuari
`python manage.py migrate`
`python manage.py createsuperuser`

---

## 7. Variables d'entorn

## 🔐 Variables d'entorn (env.example)

SECRET_KEY=12345
DEBUG=1
ALLOWED_HOSTS=localhost,127.0.0.1
MONGO_URL=mongodb://localhost:27017
DB_NAME=streamevents_db

---

## 8. Superusuari

`python manage.py createsuperuser`

---

## 9. Migrar a MongoDB

### 🗃️ Migrar a MongoDB
- Instal·lar `djongo` i `pymongo`
- Canviar `settings.py` → `ENGINE = 'djongo'`
- Configurar `CLIENT` amb `mongodb://localhost:27017`

---

### 🛠️ Comandes útils
- Arrencar el servidor: `python manage.py runserver`
- Crear migracions: `python manage.py makemigrations`
- Aplicar migracions: `python manage.py migrate`
- Proves: `python manage.py test`

---

## 💾 Fixtures i Seeders - 🚀 Instruccions de càrrega

Per carregar dades inicials (grups i usuaris) farem servir **fixtures** en format JSON.

### Primer els grups:

`python manage.py loaddata 01_groups.json`

### Després els usuaris:

`python manage.py loaddata 02_users.json`

#### Carrega totes les fixtures de l'app users
`python manage.py loaddata users/fixtures/*.json`

#### O especificar l'ordre
`python manage.py loaddata 01_groups 02_users`

### Verificar la càrrega

#### Comprovar grups
`python manage.py shell -c "from django.contrib.auth.models import Group; print(Group.objects.all())"`

#### Comprovar usuaris
`python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print(User.objects.all())"`
