import argparse
import logging
import os
import sys
from collections.abc import Iterable
from typing import List, Tuple

import colorlog


class VM:
    """
    Représente une machine virtuelle.

    Attributs:
        logger (logging.Logger): L'objet logger pour enregistrer les messages liés à la VM.

        pile (List): L'attribut pile de la VM.

        base (int): L'attribut base de la VM.

        ip (int): L'attribut pointeur d'instruction de la VM.

        stack (List): L'attribut stack de la VM, qui contient les différentes instructions.

        co (int): Le compteur ordinal de la VM.
    """

    def __init__(
        self,
        stack: List = None,
        loggingLevel: int = logging.INFO,
        stepped: bool = False,
        dashboard: bool = False,
    ):
        self.pile: List = None
        self.base: int = None
        self.ip: int = None
        if stack is None:
            stack = []
        self.stack: List = stack
        self.co: int = 0

        self.logger: logging.Logger = logging.getLogger("VM")
        self.logger.setLevel(loggingLevel)
        ch = logging.StreamHandler()
        formatter = colorlog.ColoredFormatter(
            "%(name)s - %(log_color)s%(levelname)s%(reset)s - %(message_log_color)s%(message)s",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
            secondary_log_colors={"message": {"ERROR": "red", "CRITICAL": "red"}},
        )
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
        self.stepped = stepped
        self.dashboard = dashboard
        self.debugOutput = None

    # Définition des fonctions

    def debutProg(self):
        """
        This instruction is generated at the beginning of a program.
        It initializes the data structure (stack, registers).
        """
        try:
            self.pile = []
            self.pile.append(0)
            self.pile.append(0)
            self.base = 0
            self.ip = 1
        except Exception as e:
            self.logger.error("Erreur à l'exécution de debutProg(): " + str(e))
            raise ExceptionVM("Erreur à l'exécution de debutProg(): " + str(e))

    def finProg(self):
        """Cette instruction arrête la machine NilNovi."""
        try:
            exit()
        except Exception as e:
            self.logger.error("Erreur à l'exécution de finProg(): " + str(e))
            raise

    def reserver(self, n: int):
        """_summary_ :
        Cette instruction a pour but de réserver n emplacements pour n variables au sommet de la pile d'exécution.

        Args:
            n (int): le nombre de paramètre à réserver, strictement supérieur à 0
        """
        try:
            if int(n) > 0:
                i = 0
                while i < int(n):
                    self.ip += 1
                    self.pile.append(0)
                    i += 1
        except Exception as e:
            self.logger.error("Erreur à l'exécution de reserver(): " + str(e))
            raise ExceptionVM("Erreur à l'exécution de reserver(): " + str(e))

    def empiler(self, val: int):
        """Cette instruction est utilisée pour empiler les adresses des variables ainsi que les valeurs présentes dans une expression.

        Args:
            val (int): valeur à empiler
        """
        try:
            self.pile.append(int(val))
            self.ip += 1
        except Exception as e:
            self.logger.error("Erreur à l'exécution de empiler(): " + str(e))
            raise ExceptionVM("Erreur à l'exécution de empiler(): " + str(e))

    def affectation(self):
        """Cette instruction place la valeur située en sommet de pile à l'adresse désign ée par l'emplacement sous le sommet."""

        try:
            index = int(self.pile[self.ip - 1])
            self.pile[index] = int(self.pile[self.ip])
            self.pile.pop(self.ip)
            self.pile.pop(self.ip - 1)
            self.ip -= 2
        except Exception as e:
            self.logger.error("Erreur à l'exécution de affectation(): " + str(e))
            raise ExceptionVM("Erreur à l'exécution de affectation(): " + str(e))

    def valeurPile(self):
        """Cette instruction remplace le sommet de pile par le contenu de l'emplacement désigné par le sommet."""
        try:
            self.index = int(self.pile[self.ip])
            self.pile[self.ip] = self.pile[self.index]
        except Exception as e:
            self.logger.error("Erreur à l'exécution de valeurPile(): " + str(e))
            raise ExceptionVM("Erreur à l'exécution de valeurPile(): " + str(e))

    # Entrées-Sorties

    def get(self):
        """Cette instruction permet de placer la valeur lue sur le clavier dans la variable qui est désignée par le sommet de pile."""
        try:
            userInput = input()
            c = int(userInput)
        except:
            if not userInput.strip():
                self.logger.error("User input is empty")
                raise ExceptionVM("User input is empty")
            else:
                self.logger.error("User input casting to integer failed")
                raise ExceptionVM("User input casting to integer failed")
        self.index = self.pile[self.ip]
        self.ip = self.ip - 1
        self.pile[self.index] = c
        self.pile.pop()

    def put(self):
        """Cette instruction permet d'afficher la valeur présente au sommet de la pile."""
        try:
            self.ip = self.ip - 1
            toPrint = self.pile.pop()
            print(str(toPrint))
            self.debugOutput = str(toPrint)
        except Exception as e:
            self.logger.error("Erreur à l'exécution de put(): " + str(e))
            raise ExceptionVM("Erreur à l'exécution de put(): " + str(e))

    # Expressions arithmétiques

    def moins(self):
        """Cette instruction permet de calculer l'opposé de la valeur enti`ere en sommet de pile."""
        try:
            val = int(self.pile[self.ip])
            self.pile[self.ip] = -val
        except Exception as e:
            self.logger.error("Erreur à l'exécution de moins(): " + str(e))
            raise ExceptionVM("Erreur à l'exécution de moins(): " + str(e))

    def sous(self):
        """Cette instruction permet de calculer la différence entre les deux valeurs au sommet de pile."""
        try:
            result = int(self.pile[self.ip - 1]) - int(self.pile[self.ip])
            self.pile.pop()
            self.ip = self.ip - 1
            self.pile[self.ip] = result
        except Exception as e:
            self.logger.error("Erreur à l'exécution de sous(): " + str(e))
            raise ExceptionVM("Erreur à l'exécution de sous(): " + str(e))

    def add(self):
        """Cette instruction permet de calculer la somme  entre les deux valeurs au sommet de pile."""
        try:
            result = int(self.pile[self.ip]) + int(self.pile[self.ip - 1])
            self.pile.pop()
            self.ip = self.ip - 1
            self.pile[self.ip] = result
        except Exception as e:
            self.logger.error("Erreur à l'exécution de add(): " + str(e))
            raise ExceptionVM("Erreur à l'exécution de add(): " + str(e))

    def mult(self):
        """Cette instruction permet de calculer le produit entre les deux valeurs au sommet de pile"""
        try:
            result = int(self.pile[self.ip]) * int(self.pile[self.ip - 1])
            self.pile.pop()
            self.ip = self.ip - 1
            self.pile[self.ip] = result
        except Exception as e:
            self.logger.error("Erreur à l'exécution de mult(): " + str(e))
            raise ExceptionVM("Erreur à l'exécution de mult(): " + str(e))

    def div(self):
        """Cette instruction permet de calculer la division entre les deux valeurs au sommet de pile."""
        try:
            val1 = int(self.pile[self.ip])
            val2 = int(self.pile[self.ip - 1])
            if val2 != 0:
                result = int(val2 / val1)
                self.pile.pop()
                self.pile[self.ip - 1] = result
            else:
                print("Error : dividing by 0")
            self.ip = self.ip - 1
        except Exception as e:
            self.logger.error("Erreur à l'exécution de div(): " + str(e))
            raise ExceptionVM("Erreur à l'exécution de div(): " + str(e))

    # Expressions relationnelles et booléennes

    def egal(self):
        """Cette instruction compare les deux valeurs op1 et op2 en sommet de pile et empile le code de l'expression booléenne op1=op2."""
        try:
            val1 = self.pile[self.ip]
            val2 = self.pile[self.ip - 1]
            self.pile.pop()
            self.ip = self.ip - 1
            if val1 == val2:
                self.pile[self.ip] = 1
            else:
                self.pile[self.ip] = 0
        except Exception as e:
            self.logger.error("Erreur à l'exécution de egal(): " + str(e))
            raise ExceptionVM("Erreur à l'exécution de egal(): " + str(e))

    def diff(self):
        """Cette instruction compare les deux valeurs op1 et op2 en sommet de pile et empile le code de l'expression booleenne op1!=op2."""

        try:
            val1 = self.pile[self.ip]
            val2 = self.pile[self.ip - 1]
            self.pile.pop()
            self.ip = self.ip - 1
            if val2 != val1:
                self.pile[self.ip] = 1
            else:
                self.pile[self.ip] = 0
        except Exception as e:
            self.logger.error("Erreur à l'exécution de diff(): " + str(e))
            raise ExceptionVM("Erreur à l'exécution de diff(): " + str(e))

    def inf(self):
        """Cette instruction compare les deux valeurs op1 et op2 en sommet de pile et empile le code de l'expression booleenne op1<op2."""
        try:
            val1 = self.pile[self.ip]
            val2 = self.pile[self.ip - 1]
            self.pile.pop()
            self.ip = self.ip - 1
            if val2 < val1:
                self.pile[self.ip] = 1
            else:
                self.pile[self.ip] = 0
        except Exception as e:
            self.logger.error("Erreur à l'exécution de inf(): " + str(e))
            raise ExceptionVM("Erreur à l'exécution de inf(): " + str(e))

    def infeg(self):
        """Cette instruction compare les deux valeurs op1 et op2 en sommet de pile et empile le code de l'expression booleenne op1<=op2."""
        try:
            val1 = self.pile[self.ip]
            val2 = self.pile[self.ip - 1]
            self.pile.pop()
            self.ip = self.ip - 1
            if val2 <= val1:
                self.pile[self.ip] = 1
            else:
                self.pile[self.ip] = 0
        except Exception as e:
            self.logger.error("Erreur à l'exécution de infeg(): " + str(e))
            raise ExceptionVM("Erreur à l'exécution de infeg(): " + str(e))

    def sup(self):
        """Cette instruction compare les deux valeurs op1 et op2 en sommet de pile et empile le code de l'expression booleenne op1>op2."""
        try:
            val1 = self.pile[self.ip]
            val2 = self.pile[self.ip - 1]
            self.pile.pop()
            self.ip = self.ip - 1
            if val2 > val1:
                self.pile[self.ip] = 1
            else:
                self.pile[self.ip] = 0
        except Exception as e:
            self.logger.error("Erreur à l'exécution de sup(): " + str(e))
            raise ExceptionVM("Erreur à l'exécution de sup(): " + str(e))

    def supeg(self):
        """Cette instruction compare les deux valeurs op1 et op2 en sommet de pile et empile le code de l'expression booleenne op1>=op2."""
        try:
            val1 = self.pile[self.ip]
            val2 = self.pile[self.ip - 1]
            self.pile.pop()
            self.ip = self.ip - 1
            if val2 >= val1:
                self.pile[self.ip] = 1
            else:
                self.pile[self.ip] = 0
        except Exception as e:
            self.logger.error("Erreur à l'exécution de supeg(): " + str(e))
            raise ExceptionVM("Erreur à l'exécution de supeg(): " + str(e))

    def et(self):
        """Cette instruction prend en compte deux booléens op1 et op2 en sommet de pile et place dans la pile le code de l'expression booléenne (op1 and op2)."""
        try:
            if self.pile[self.ip] and self.pile[self.ip - 1]:
                self.pile.pop()
                self.pile[self.ip - 1] = 1
            else:
                self.pile.pop()
                self.pile[self.ip - 1] = 0
            self.ip = self.ip - 1
        except Exception as e:
            self.logger.error("Erreur à l'exécution de et(): " + str(e))
            raise ExceptionVM("Erreur à l'exécution de et(): " + str(e))

    def ou(self):
        """Cette instruction prend en compte deux booléens op1 et op2 en sommet de pile, et place dans la pile le code de l'expression booléenne (op1 or op2)."""
        try:
            if self.pile[self.ip] or self.pile[self.ip - 1]:
                self.pile.pop()
                self.pile[self.ip - 1] = 1
            else:
                self.pile.pop()
                self.pile[self.ip - 1] = 0
            self.ip = self.ip - 1
        except Exception as e:
            self.logger.error("Erreur à l'exécution de ou(): " + str(e))
            raise ExceptionVM("Erreur à l'exécution de ou(): " + str(e))

    def non(self):
        """Cette instruction permet de calculer la négation du booléen en sommet de pile."""
        try:
            if self.pile[self.ip] == 0:
                self.pile[self.ip] = 1
            else:
                self.pile[self.ip] = 0
        except Exception as e:
            self.logger.error("Erreur à l'exécution de non(): " + str(e))
            raise ExceptionVM("Erreur à l'exécution de non(): " + str(e))

    # Contrôle

    def tra(self, ad: int):
        """Cette instruction donne le contrôle à l'instruction située à l'adresse ad. Il s'agit d'un branchement inconditionnel.
        Args:
        ad (int): l'addresse ad ou doit être situation l'instruction
        """
        try:
            self.co = int(ad) - 2
        except Exception as e:
            self.logger.error("Erreur à l'exécution de tra(): " + str(e))
            raise ExceptionVM("Erreur à l'exécution de tra(): " + str(e))

    def tze(self, ad: int):
        """Cette instruction donne le contrôle à l'instruction située à l'adresse ad si le sommet de pile contient faux, continue en séquence sinon.

        Args:
            ad (int): l'addresse ad ou doit être situation l'instruction
        """
        try:
            if self.pile[self.ip] == 0:
                self.ip = self.ip - 1
                self.pile.pop(self.ip + 1)
                self.co = int(ad) - 2
            else:
                self.ip = self.ip - 1
                self.pile.pop(self.ip + 1)
        except Exception as e:
            self.logger.error("Erreur à l'exécution de tze(): " + str(e))
            raise ExceptionVM("Erreur à l'exécution de tze(): " + str(e))

    # nnp
    # unité de compilation

    def empilerAd(self, ad: int):
        """Cette instruction est utilisée dans le cas de variables locales pour transformer l'adresse statique en adresse dynamique

        Args:
            ad (int): l'emplacement au-dessus du bloc de liaison courant.
        """
        try:
            self.pile += [self.base + 2 + int(ad)]
            self.ip = self.ip + 1
        except Exception as e:
            self.logger.error("Erreur à l'exécution de empilerAd(): " + str(e))
            raise ExceptionVM("Erreur à l'exécution de empilerAd(): " + str(e))

    # Opérations

    def reserverBloc(self):
        """Cette instruction permet, lors de l'appel d'une opération, de réserver les emplacements du futur bloc de liaison et d'initialiser la partie pointeur vers le bloc de liaison de l'appelant"""
        try:
            self.pile += [self.base, 0]
            self.ip = self.ip + 2
        except Exception as e:
            self.logger.error("Erreur à l'exécution de reserverBloc(): " + str(e))
            raise ExceptionVM("Erreur à l'exécution de reserverBloc(): " + str(e))

    def traStat(self, tuple: Tuple[int, int]):
        """Cette instruction est produite à la fin de la compilation d'un appel à une opération. Lors de l'exécution, elle complète la structure créée par l'exécution de l'instruction _reserverBloc_ (structure qui se trouve à *nbp* positions sous le sommet de pile) en introduisant l'adresse de retour (qui estl'adresse suivant l'adresse de cette instruction). Cette structure est promue (nouveau) bloc de liaison. Enfin cette structure affecte le compteur ordinal _co_ avec la valeur *a*.

        Args:
            tuple (Tuple[int, int]): (a, nbp) : nouvelle position du compteur ordinateur co; nombre de positions sous le sommet de pile
        """
        (a, nbp) = tuple
        try:
            index = self.ip - int(nbp)
            self.base = index - 1
            self.pile[index] = self.co + 1
            self.co = int(a) - 2
        except Exception as e:
            self.logger.error("Erreur à l'exécution de traStat(): " + str(e))
            raise ExceptionVM("Erreur à l'exécution de traStat(): " + str(e))

    def retourFonct(self):
        """Cette instruction est produite à la fin de la compilation d'une instruction _return_ dans une fonction. Outre son rôle dans le retour, elle assure que la valeur en sommet de pile sera le résultat de l'appel."""
        try:
            val = self.pile[self.ip]
            ar = self.pile[self.base + 1]
            index = self.base
            self.base = self.pile[self.base]
            while self.ip >= index:
                self.pile.pop()
                self.ip = self.ip - 1
            self.pile.append(val)
            self.ip = self.ip + 1
            self.co = ar - 1
        except Exception as e:
            self.logger.error("Erreur à l'exécution de retourFonct(): " + str(e))
            raise ExceptionVM("Erreur à l'exécution de retourFonct(): " + str(e))

    def retourProc(self):
        """Cette instruction est produite à la fin de la compilation d'une procédure. Elle assure le retour à l'appelant."""
        try:
            ar = self.pile[self.base + 1]
            index = self.base
            self.base = self.pile[self.base]

            while self.ip >= index:
                self.pile.pop()
                self.ip = self.ip - 1
            self.co = ar - 1
        except Exception as e:
            self.logger.error("Erreur à l'exécution de retourProc(): " + str(e))
            raise ExceptionVM("Erreur à l'exécution de retourProc(): " + str(e))

    def empilerParam(self, ad: int):
        """Cette instruction permet de gérer les paramètres effectifs.

        Args:
            ad (int): addresse  de la valeur à empiler
        """
        try:
            val = self.pile[self.base + int(ad) + 2]
            self.pile.append(val)
            self.ip = self.ip + 1
        except Exception as e:
            self.logger.error("Erreur à l'exécution de empilerParam(): " + str(e))
            raise ExceptionVM("Erreur à l'exécution de empilerParam(): " + str(e))

    def erreur(self):
        """Provoque l'arrêt de la machine."""
        exit(-1)

    def run(self):
        """Démarre l'éxécution du code machine sauvegardé dans *stack*"""
        while self.co < len(self.stack):
            instruction = self.stack[self.co]
            params = instruction[1]

            if self.logger.getEffectiveLevel() <= logging.DEBUG:
                if self.dashboard:
                    print(
                        sideBySideStrings(
                            instructionsTableString(self.stack, self.co + 1, True),
                            stackTable(self.pile, True),
                        )
                    )
                    # print(stackTable(self.pile, True))
                    # print(instructionsTableString(self.stack, self.co+1, True))
                    if self.debugOutput:
                        self.logger.debug(f"Output: {self.debugOutput}")
                        self.debugOutput = None
                else:
                    self.logger.debug(
                        f"\033[92mbase: \033[92m{str(self.base)} \033[93mip: \033[93m{str(self.ip)}\033[0m - \033[94m{str(self.pile)}\033[0m"
                    )
                    self.logger.debug(
                        f"\033[95mco: {self.co+1}\033[0m - \033[96m{instruction[0]}(\033[38;2;0;0;255m{paramToString(params)}\033[96m)\033[0m"
                    )
                if self.stepped:
                    input()
                    clearScreen()
            match instruction[0]:
                case "debutProg":
                    self.debutProg()
                case "reserver":
                    self.reserver(int(params[0]))
                case "empiler":
                    self.empiler(int(params[0]))
                case "affectation":
                    self.affectation()
                case "valeurPile":
                    self.valeurPile()
                case "get":
                    self.get()
                case "put":
                    self.put()
                case "moins":
                    self.moins()
                case "sous":
                    self.sous()
                case "add":
                    self.add()
                case "mult":
                    self.mult()
                case "div":
                    self.div()
                case "egal":
                    self.egal()
                case "diff":
                    self.diff()
                case "inf":
                    self.inf()
                case "infeg":
                    self.infeg()
                case "sup":
                    self.sup()
                case "supeg":
                    self.supeg()
                case "et":
                    self.et()
                case "ou":
                    self.ou()
                case "non":
                    self.non()
                case "tra":
                    self.tra(int(params[0]))
                case "tze":
                    self.tze(int(params[0]))
                case "empilerAd":
                    self.empilerAd(int(params[0]))
                case "reserverBloc":
                    self.reserverBloc()
                case "traStat":
                    a = int(params[0])
                    nbp = int(params[1])
                    self.traStat((a, nbp))
                case "retourFonct":
                    self.retourFonct()
                case "retourProc":
                    self.retourProc()
                case "empilerParam":
                    self.empilerParam(int(params[0]))
                case "finProg":
                    self.finProg()
                case _:
                    self.erreur()
                    break
            self.co = self.co + 1


def paramToString(param: Iterable) -> str:
    """Transforme un itérable de paramètre en chaine de caractère délimitée par des virgules

    Args:
        param (Iterable): Les paramètres

    Returns:
        str: Chaine de caractère délimitée par des virgules
    """
    string = ""
    if param:
        string += str(param[0])

        for p in param[1:]:
            string += f", {str(p)}"
    return string


def instructionsTableString(
    instructions: List, coPosition: int = 0, showIndex: bool = False
) -> str:
    """Transforme en chaine ASCII la liste d'instructions avec son pointeur ordinal

    Args:
        instructions (List): Liste des instructions
        coPosition (int, optional): Position du compteur ordinal. Lorsqu'il vaut 0 le pointeur n'apparait pas. Par défaut vaut 0
        showIndex (bool, optional): Indiquer la position des éléments. Par défaut vaut Faux

    Returns:
        str: Tableau graphique avec le pointeur
    """

    padding = 4
    pointerOffset = 2
    pointer = "\033[38;2;0;255;m<-- CO\033[0m"

    maxLen = 0
    instructionsToString = []
    for instruction in instructions:
        instructionString = f"{instruction[0]}({paramToString(instruction[1])})"
        instructionsToString.append(instructionString)
        maxLen = len(instructionString) if len(instructionString) > maxLen else maxLen

    horizBar = f"+{'-'*(maxLen+padding+(padding+1)*int(showIndex))}+"

    tableString = horizBar
    for position, instruction in enumerate(instructionsToString):
        rowString = "\n|"
        if showIndex:
            rowString += f"{str(position+1).ljust(padding, ' ')}|"
        if position + 1 == coPosition:
            rowString += (
                f"\033[38;2;0;255;m{instruction.ljust(maxLen+padding, ' ')}\033[0m|"
            )
            rowString += f"{' '*pointerOffset}{pointer}"
        else:
            rowString += f"{instruction.ljust(maxLen+padding, ' ')}|"
        tableString += rowString
    tableString += f"\n{horizBar}\n"
    return tableString


def stackTable(stack: List, showIndex: bool = False) -> str:
    """Affiche une pile dans un tableau

    Args:
        stack (List): La pile à afficher
        showIndex (bool, optional): Indiquer la position des éléments. Par défaut vaut Faux

    Returns:
        str: Tableau graphique de la pile
    """
    padding = 4

    stackString = ""
    maxLen = 0

    if not stack:
        return ""

    for element in stack:
        maxLen = len(str(element)) if len(str(element)) > maxLen else maxLen

    horizBar = f"+{'-'*(maxLen+padding+(padding+1)*int(showIndex))}+"

    stackString = horizBar
    stack.reverse()
    for index, element in enumerate(stack):
        rowString = "\n|"
        if showIndex:
            rowString += f"{str(len(stack)-index).ljust(padding, ' ')}|"
        rowString += f"{str(element).ljust(maxLen+padding, ' ')}|"
        stackString += rowString
    stack.reverse()
    stackString += f"\n{horizBar}\n"

    return stackString


def sideBySideStrings(string1: str, string2: str) -> str:
    """Place côte à côte 2 chaînes de caractères délimitées par le caractère \\n. Les chaines doivent terminer par \n.

    Args:
        string1 (str): Chaine de caractères
        string2 (str): Chaine de caractères

    Returns:
        str: Les 2 chaines côtes à côtes
    """
    padding = 5

    sidedStrings = "\n"

    if not string2:
        return sideBySideStrings(string1, sidedStrings)

    if not string1:
        return sideBySideStrings(sidedStrings, string2)

    l1 = string1.split("\n")[:-1]
    l2 = string2.split("\n")[:-1]

    if len(l2) > len(l1):
        l1, l2 = l2, l1

    l1.reverse()
    l2.reverse()

    l0 = []

    maxLen = 0

    for index, s2 in enumerate(l2):
        s1 = l1[index]
        totalLen = len(s1) + len(s2)
        maxLen = totalLen if totalLen > maxLen else maxLen

    for index, s2 in enumerate(l2):
        s1 = l1[index]
        s = f"{s1}{s2.rjust(maxLen-len(s1)+padding , ' ')}\n"
        l0.append(s)

    # l0 += "\n".join(l1[len(l2):])
    l0.reverse()
    for s0 in l0:
        sidedStrings += s0
    subl1 = l1[len(l2) :]
    subl1.reverse()
    sidedStrings = "\n".join(subl1) + sidedStrings

    return sidedStrings


def clearScreen():
    """Efface le contenu de l'affichage graphique."""
    if os.name == "nt":
        os.system("cls")  # Use the "cls" command to clear the screen on Windows
    else:
        os.system(
            "clear"
        )  # Use the "clear" command to clear the screen on Unix-like systems


class ExceptionVM(Exception):
    """Raise to specify an error with Class VM"""


if __name__ == "__main__":
    vm = VM()
    parser = argparse.ArgumentParser(description="VM of a NNP program.")
    parser.add_argument(
        "inputfile", type=str, nargs=1, help="name of the input source file"
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_const",
        const=logging.DEBUG,
        default=logging.INFO,
        help="show debugging info on output",
    )
    args = parser.parse_args()
    filename = sys.argv[1]
    file = open(filename, "r")
    stack = []
    for line in file:
        param = line.split("(")[1].split(")")[0].split(",")
        stack.append([line.split("(")[0], param])

    file.close()
    vm.run(stack, args)
