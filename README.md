
# Compilateur et machine virtuel Nilnovi

**nnp-mv** est une application Python permettant de compiler et d'éxecuter du code en Nilnovi.

## Équipe

- Ahmed Abid
- Victor Dang
- Yasser El Ayyachy
- Imane Elmeskiri
- Yasser Jarmouni
- Oussama Khaloui


## Pré-requis

Il est supposé que l'utilisateur utilisé un système d'exploitation doté de *bash*. Toutefois le projet reste compatible avec un terminal de type Windows.

### Nécéssaires
- Python de version **>= 3.10**

### Recommandés (pour l'installation automatisée)
- [virtualenv](https://github.com/pypa/virtualenv)
- [bash](https://www.gnu.org/software/bash/)

## Installation d'un environnement virtuel

Il est conseillé d'installer un environnement virtuel Python afin de garantir la reproductibilité des résultats.

Récupérer les sources du programme en clonant le répertoire git

```bash
git clone https://gitlab.enssat.fr/vdang/nnp-mv.git
```

Se placer dans le dossier nnp-mv

```bash
cd nnp-mv
```

Choisir l'une des deux méthodes d'installation.

### Installation (semi-)automatique

Un script shell compatible avec bash est disponible en exécutant *install_bash.sh*

```bash
./install_bash.sh
```

L'installateur vous donne le choix du mode d'installation. Il suffit de suivre les instructions affichées.

### Installation manuelle

Créer un envrionnement virtuel. Dans cet exemple, **virtualenv** est utilisé. **conda** est une alternative possible.

*$env_name* désigne le nom de l'environnement allant être créé.

```bash
virtualenv $env_name
```

Installer les dépendances pythons.

```bash
pip install -r requirements.txt
```

### Dépendances

Quelle que soit la méthode d'installation choisie, il est nécéssaire d'installer des paquets pythons.

Paquets nécéssaires au fonctionnement de *nnp-mv* :

- [colorlog](https://pypi.org/project/colorlog/), affichage graphique en mode debug

Paquets conseillés pour le développement de *nnp-mv* :

- [black](https://black.readthedocs.io/en/stable/)
- [isort](https://pycqa.github.io/isort/)
- [ruff](https://beta.ruff.rs/docs/)
- [pre-commit](https://pre-commit.com/)

## Utilisation

⚠️ **Il ne faut pas oublier d'activer l'environnement virtuel Python qui a été créé lors de l'installation.** ⚠️

virtualenv
```bash
source $env_name/bin/activate
```

virtualenvwrapper
```bash
workon $env_name
```

conda
```bash
source activate $env_name
```

## Interface Python

### Compilateur

Le compilateur est disponible en exécutant

```bash
python nnp-comp.py filename [--outputfile file --show-ident-table --debug --help]
```

- filename : chemin pointant vers le programme NilNovi
- file : chemin où enregistrer le programme assembleur
- --show-ident-table : affiche le tableau des identificateurs à la fin de la compilation
- --debug : active le mode débogage

### Machine virtuelle

La machine virtuelle est disponible en exécutant

```bash
python nnp-exec.py filename [--debug --stepped --board --version --help]
```

- filename : chemin pointant vers le programme assembleur

- --debug : active le mode débogage

- --stepped : l'exécution se fait instruction par instruction

- --board : un tableau de bord contenant les instructions et la pile est affiché

### Intégration dans une chaine de développement

⚠️ **Cette fonctionnalité n'a pas été développée ni testée en totalité.** ⚠️

Les scripts *nnp-comp.py* et *nnp-execpy* servent principalement à passer des paramètres. Il est possible d'utiliser les objets Python faisant fonctionner *nnp-mv* sans passer par les scripts. 


Un cas d'utilisation est la création d'une chaine de développement complète où l'on souhaterait en entrée un fichier nilnovi et en sortie l'éxécution de son code compilé.

#### Obtention d'un code compilé

Le code compilé est obtenu avec l'analyseur syntaxique (*src/anasyn.py*) qui va utiliser une instance de **Compiler** nommé *compiler*. Cette dernière instancie un **IdentifierTable** accessible avec *compiler.identifierTable*.

Ajouter au chemins de recherche des modules le dossier src et importer *anasyn*

```python
from pathlib import Path
sys.path.insert(0, str(Path(".", "src").absolute()))
import anasyn
```

Démarrer l'analyse lexical du programme Nilnovi. On suppose que le programme est chargé dans une variable *file*

```python
lexical_analyser = analex.LexicalAnalyser()

for lineIndex, line in enumerate(file):
    line = line.rstrip("\r\n")
    lexical_analyser.analyse_line(lineIndex, line)
```

Procéder à l'analyse syntaxique et la compilation

```python
lexical_analyser.init_analyser()
anasyn.program(lexical_analyser)
```

Pour récupérer la liste des instructions en assembleur, il suffit d'accéder à l'attribut *instructions* de *compiler*
```python
anasyn.compiler.instructions
```
La structure de la liste des instructions est décrite dans la documentation et le rapport.

#### Exécution d'un code compilé

Le code compilé est exécuté par une instance de la classe **VM**.

On suppose que la liste des instructions des instructions est stocké dans une variable nommé **instructions**.

Instancier une instance de **VM** en spécifiant le paramètre *stack*

```python
vm = VM(stack=instructions)
```

L'exécution démarre en appelant la méthode *run*

```python
vm.run()
```

La documentation contient plus d'information sur l'utilisation d'une machine virtuelle.

<!-- ## Interface Bash (Pas implémenté)

### Compilateur

Le compilateur est disponible en exécutant

```bash
nnp-comp.py filename [--outputfile file --show-ident-table --debug --help]
```

### Machine virtuelle

La machine virtuelle est disponible en exécutant

```bash
nnp-exec.py filename [--debug --stepped --board --help --version]
``` -->

## Documentation

La documentation est générée avec [Sphinx](https://www.sphinx-doc.org) en utilisant le thème [Read the Docs Sphinx Theme](https://sphinx-rtd-theme.readthedocs.io/). Ces dépendances sont référencées dans le fichier *requirements.txt*.

[GNU Make](https://www.gnu.org/software/make/) est une autre dépendance à installer.

### Génération de la documentation

Se placer dans le dossier *docs*

```bash
cd docs
```

```bash
make html
```

La génération des pages HTML prend un temps non négligeable.

### Visualisation de la documentation

La page d'acceuil de la documentation se trouve dans le dossier *docs/_build/html*

```bash
cd docs/_build/html
firefox index.html
```

## Remerciements

 - Pr. Damien Lolive