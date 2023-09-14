from typing import List

from analex import Identifier
from IdentifierTable import (
    CallableEntry,
    IdentifierEntry,
    IdentifierTable,
    IdentifierType,
    IdentifierTypeError,
)


class Compiler:
    """
    Représente un compilateur NilNovi

    Attributs:
        instructions (List): liste des instructions en assembleur

        identifierTable (IdentifierTable): table des identificateurs

        nestedAltern (int): compteur des blocs d'alternatives imbriqués

        nestedLoop (int): compteur des boucles imbriquées

        identifierQueue (List[Identifier]): queue des identificateurs

        passingParam (bool): indique si les identificateurs de type variable rencontrés sont passés en paramètre

        passingOut (bool): indique si les identificateurs de type variable rencontrés sont passés en paramètre avec un drapeau _out_

        declaredCallables (bool): indique si des appelables ont déjà été déclaré

        scope (IdentifierEntry): portée actuelle

        callableStack (List[CallableEntry]): pile d'appelables en cours de traitement

        outStack (List[bool]): pile de drapeaux _out_
    """

    def __init__(self):
        self.instructions: List = []
        self.identifierTable: IdentifierTable = IdentifierTable()

        self.nestedAltern: int = 0
        self.nestedLoop: int = 0
        self.identifierQueue: List[Identifier] = []
        self.passingParam = False
        self.passingOut = False

        self.declaredCallables: bool = False
        self.scope: IdentifierEntry = None
        self.passingParam: bool = False
        self.passingOut: bool = False
        self.callableStack: List[CallableEntry] = []
        self.outStack: List[bool] = []

    def addCallable(
        self,
        identifier: Identifier,
        identifierType: IdentifierType,
        machineCodeAddress: int = None,
    ) -> CallableEntry:
        """Ajoute un appelable au tableau des identificateurs et le référence dans la portée actuelle

        Args:
            identifier (Identifier): l’identificateur
            identifierType (IdentifierType): le type d’identificateur
            machineCodeAddress (int, optional): l'adresse de début de l'appelable. Par défaut None.

        Raises:
            IdentifierTypeError: l'identificateur n'est pas un appelable

        Returns:
            CallableEntry: l'appelable ajouté dans le tableau d'identificateur
        """
        if not IdentifierType.isCallableType:
            raise IdentifierTypeError(
                f"{str(identifier)} n'est pas un identificateur d'appelable"
            )

        machineCodeAddress = (
            len(self.instructions) + 1
            if machineCodeAddress is None
            else machineCodeAddress
        )
        callableEntry = self.identifierTable.addCallable(
            identifier, identifierType, self.scope, machineCodeAddress
        )
        self.setScope(callableEntry)
        return callableEntry

    def stackCallable(self, callable: CallableEntry):
        """Empilement d'un *CallableEntry*

        Args:
            callable (CallableEntry): à empiler

        Raises:
            TypeError: l'appelable n'est pas un appelable
        """
        if not isinstance(callable, CallableEntry):
            raise TypeError(f"{str(callable)} is not a CallableEntry")
        self.callableStack.append(callable)
        self.passingParam = True
        self.outStack += [parameter.outStatus for parameter in callable.parameters]

    def unstackCallable(self, value: int = 1):
        """Dépilement de *CallableEntry* de la pile.

        Args:
            value (int, optional): nombre de dépilements. Par défaut 1

        Raises:
            ValueError: nombre de dépilements supérieur à la taille de la pille
        """
        if value == -1:
            value = len(self.callableStack)
        elif value > len(self.callableStack):
            raise ValueError(
                f"Impossible de dépiler {value} éléments car la pile n'en contient que {len(self.callableStack)}"
            )
        for _ in range(value):
            self.callableStack.pop()
        if not self.callableStack:
            self.passingParam = False

    def unstackOutStatus(self) -> bool:
        """Dépile un drapeau *out* de la pile

        Raises:
            ValueError: la pile est vide

        Returns:
            bool: drapeau *out*
        """
        if not self.outStack:
            raise ValueError("La pile est vide")
        return self.outStack.pop()

    def addVariable(
        self,
        identifier: Identifier,
        identifierType: IdentifierType,
        scope: CallableEntry,
        isIn: bool,
        isOut: bool,
    ):
        """Ajoute une variable au tableau des identificateurs et le référence dans la portée actuelle

        Args:
            identifier (Identifier): l'identificateur
            identifierType (IdentifierType): le type d'identificateur
            scope (CallableEntry): la portée
            isIn (bool): drapeau *in* pour les paramètres
            isOut (bool): drapeau *out* pour les paramètres

        Raises:
            IdentifierTypeError: l'identificateur n'est pas une variable
            ValueError: la portée n'est pas définie
        """
        if not IdentifierType.isVariableType:
            raise IdentifierTypeError(
                f"{str(identifier)} n'est pas un identificateur de variable"
            )
        if not scope:
            raise ValueError(
                f"Il n'y a aucune portée définie, il n'est pas possible d'ajouter la variable {identifier}"
            )
        variableAddress = scope.nbVar
        variableEntry = self.identifierTable.addVariable(
            identifier, identifierType, scope, isIn, isOut, variableAddress
        )
        scope.add(variableEntry)

    def addQueue(self, identifier: Identifier):
        """Ajoute un identificateur à la queue

        Args:
            identifier (Identifier): un identificateur
        """
        self.identifierQueue.append(identifier)

    def emptyQueue(self, identifierType: IdentifierType, isOut: bool = None):
        """Vide la queue de d'*Identifier* de variables en les ajoutant au tableau d'identificateur.

        Args:
            identifierType (IdentifierType): le type d'*Identifier*
            isOut (bool, optional): drapeau *out* pour les paramètres. Par défaut None

        Raises:
            ValueError: la queue est vide
            IdentifierTypeError: les identificateurs ne sont pas des variables
        """
        if not self.identifierQueue:
            raise ValueError("La queue d'identificateurs est déjà vide !")
        if not identifierType.isVariableType:
            raise IdentifierTypeError("Les identificateurs ne sont pas des variables")
        isIn = False
        if isOut is not None:
            isIn = True
        while self.identifierQueue:
            identifier = self.identifierQueue.pop(0)
            self.addVariable(identifier, identifierType, self.scope, isIn, isOut)

    def setScope(self, entry: CallableEntry):
        """Définit la portée

        Args:
            entry (CallableEntry): la portée
        """
        self.scope = entry

    def leaveScope(self):
        """Quitte la portée actuelle et redéfinit sa portée au parent"""
        self.scope = self.scope.scope

    @staticmethod
    def generate_instruction(function: str, *param) -> List:
        """Génère l'instruction selon la structure de donnée définie

        Args:
            function (str): nom de l'instruction

        Returns:
            List: l'instruction et ses paramètres
        """
        return [function, param]

    def addInstruction(self, function: str, *param):
        """Ajoute au sommet l'instruction avec ses paramètres

        Args:
            function (str): nom de l'instruction
        """
        instr = Compiler.generate_instruction(function, *param)
        self.instructions.append(instr)

    def insertInstruction(self, function: str, position: int, *param):
        """Insère l'instruction avec ses paramètres à la *position* demandée

        Args:
            function (str): nom de l'instruction
            position (int): position dans la liste d'instructions

        Raises:
            ValueError: la position n'est pas accessible
        """
        instr = Compiler.generate_instruction(function, *param)
        if position > len(self.instructions):
            raise ValueError(
                f"Insertion de l'instruction {function} à la position {position} impossible : il n'y a que {len(self.instructions)} instructions !"
            )
        self.instructions.insert(position, instr)

    def __str__(self) -> str:
        string = ""
        for index, instruction in enumerate(self.instructions):
            instructionName: str = instruction[0]
            param = instruction[1]
            paramString: str = ""
            if len(param) == 1:
                paramString = f"{param[0]}"
            elif len(param) == 2:
                paramString = f"{param[0]}, {param[1]}"
            instructionString: str = f"{instructionName}({paramString})"
            string += f"{instructionString}\n"
        return string[:-1]

    def saveInstructions(self, file: str):
        """Sauvegarde la liste des instructions au format assembleur

        Args:
            file (str): chemin où enregistrer le code assembleur
        """
        filename = open(file, "w")
        filename.write(str(self))
        filename.close()

    def debutProg(self):
        """Ajoute l'instruction "debutProg" à la liste d'instructions."""
        self.addInstruction("debutProg")

    def finProg(self):
        """Ajoute l'instruction "finProg" à la liste d'instructions."""
        self.addInstruction("finProg")

    def reserver(self, n):
        """Ajoute l'instruction "reserver" à la liste d'instructions.

        Args:
            n (int): nombre d'emplacements mémoire à réserver
        """
        self.addInstruction("reserver", n)

    def empiler(self, n):
        """Ajoute l'instruction "empiler" à la liste d'instructions.

        Args:
            n: valeur numérique à empiler
        """
        self.addInstruction("empiler", n)

    def empilerAd(self, ad):
        """Ajoute l'instruction "empilerAd" à la liste d'instructions.

        Args:
            ad (int): adresse de variable à empiler
        """
        self.addInstruction("empilerAd", ad)

    def affectation(self):
        """Ajoute l'instruction "affectation" à la liste d'instructions."""
        self.addInstruction("affectation")

    def valeurPile(self):
        """Ajoute l'instruction "valeurPile" à la liste d'instructions."""
        self.addInstruction("valeurPile")

    def get(self):
        """Ajoute l'instruction "get" à la liste d'instructions."""
        self.addInstruction("get")

    def put(self):
        """Ajoute l'instruction "put" à la liste d'instructions."""
        self.addInstruction("put")

    def moins(self):
        """Ajoute l'instruction "moins" à la liste d'instructions."""
        self.addInstruction("moins")

    def sous(self):
        """Ajoute l'instruction "sous" à la liste d'instructions."""
        self.addInstruction("sous")

    def add(self):
        """Ajoute l'instruction "add" à la liste d'instructions."""
        self.addInstruction("add")

    def mult(self):
        """Ajoute l'instruction "mult" à la liste d'instructions."""
        self.addInstruction("mult")

    def div(self):
        """Ajoute l'instruction "div" à la liste d'instructions."""
        self.addInstruction("div")

    def egal(self):
        """Ajoute l'instruction "egal" à la liste d'instructions."""
        self.addInstruction("egal")

    def diff(self):
        """Ajoute l'instruction "diff" à la liste d'instructions."""
        self.addInstruction("diff")

    def inf(self):
        """Ajoute l'instruction "inf" à la liste d'instructions."""
        self.addInstruction("inf")

    def infeg(self):
        """Ajoute l'instruction "infeg" à la liste d'instructions."""
        self.addInstruction("infeg")

    def sup(self):
        """Ajoute l'instruction "sup" à la liste d'instructions."""
        self.addInstruction("sup")

    def supeg(self):
        """Ajoute l'instruction "supeg" à la liste d'instructions."""
        self.addInstruction("supeg")

    def et(self):
        """Ajoute l'instruction "et" à la liste d'instructions."""
        self.addInstruction("et")

    def ou(self):
        """Ajoute l'instruction "ou" à la liste d'instructions."""
        self.addInstruction("ou")

    def non(self):
        """Ajoute l'instruction "non" à la liste d'instructions."""
        self.addInstruction("non")

    def tra(self, ad):
        """Ajoute l'instruction "tra" à la liste d'instructions.

        Args:
            ad (int): adresse de l'instruction.
        """
        self.addInstruction("tra", ad)

    def tze(self, ad):
        """Ajoute l'instruction "tze" à la liste d'instructions.

        Args:
            ad (int): adresse de l'instruction.
        """
        self.addInstruction("tze", ad)

    def erreur(self):
        """Ajoute l'instruction "erreur" à la liste d'instructions."""
        self.addInstruction("erreur")

    def reserverBloc(self):
        """Ajoute l'instruction "reserverBloc" à la liste d'instructions."""
        self.addInstruction("reserverBloc")

    def retourConstr(self):
        """Ajoute l'instruction "retourConstr" à la liste d'instructions."""
        self.addInstruction("retourConstr")

    def retourFonct(self):
        """Ajoute l'instruction "retourFonct" à la liste d'instructions."""
        self.addInstruction("retourFonct")

    def retourProc(self):
        """Ajoute l'instruction "retourProc" à la liste d'instructions."""
        self.addInstruction("retourProc")

    def empilerParam(self, ad):
        """Ajoute l'instruction "empilerParam" à la liste d'instructions.

        Args:
            ad (int): adresse du paramètre à empiler
        """
        self.addInstruction("empilerParam", ad)

    def traStat(self, ad: int, nbP: int):
        """Ajoute l'instruction "traStat" à la liste d'instruction

        Args:
            ad (int): addresse de l'instruction
            nbP (int): nombre de positions sous le sommet de pile
        """
        self.addInstruction("traStat", ad, nbP)
