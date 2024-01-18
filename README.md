# Hawaii Blog

## Description

Il s'agit d'une application web de blog simple construite avec Flask, SQLAlchemy et d'autres technologies Python. L'application prend en charge l'inscription des utilisateurs, l'authentification et les opérations CRUD pour les articles de blog et les commentaires.

## Fonctionnalités

- **Authentification des utilisateurs** : Les utilisateurs peuvent s'inscrire, se connecter et se déconnecter. L'authentification utilise le hachage de mot de passe.
- **Articles de blog** : Créez, modifiez et supprimez des articles de blog. Chaque article a un titre, un sous-titre, un corps et une image facultative.
- **Commentaires** : Les utilisateurs peuvent laisser des commentaires sur les articles de blog.
- **Formulaire de contact** : Un formulaire de contact simple est disponible pour que les utilisateurs puissent envoyer des messages.

## Technologies Utilisées

- Flask
- SQLAlchemy
- Flask-Login
- Flask-WTF
- Flask-CKEditor
- Flask-Bootstrap
- Flask-Gravatar

## Instructions d'Installation

1. Clonez le dépôt. `git clone https://github.com/MarcOutt/Hawaii-Blog.git`
2. Installez les dépendances avec `pip install -r requirements.txt`.
3. Configurez l'URI de la base de données dans `app.config['SQLALCHEMY_DATABASE_URI']`.
4. Définissez vos identifiants de messagerie dans `personnal_infos.py` pour le formulaire de contact.
5. Lancez l'application avec `python app.py`.
6. Accédez à l'application à [http://localhost:5000](http://localhost:5000).

## Captures d'Écran

![img.png](img.png)
![img_1.png](img_1.png)
![img_2.png](img_2.png)
![img_3.png](img_3.png)
![img_4.png](img_4.png)
