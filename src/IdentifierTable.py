from __future__ import annotations

from enum import Enum, unique
from typing import List

from analex import Identifier


class IdentifierTable:
    """
    Représente un tableau d'identificateurs

    Attributs:
        table (List): liste des identificateurs dans la table

        variableTable (List[VariableEntry]): liste des entrées de variables dans la table

        callableTable (List[CallableEntry]): liste des entrées d'appelables dans la table

        identifierQueue (List[Identifier]): file d'attente des identificateurs
    """

    def __init__(self, table=None):
        if table is None:
            table = []
        self.table = table
        self.variableTable: List[VariableEntry] = []
        self.callableTable: List[CallableEntry] = []
        self.identifierQueue: List[Identifier] = []

    def addVariable(
        self,
        identifier: Identifier,
        variableType: IdentifierType.VariableType,
        scope: CallableEntry,
        isIn: bool = False,
        isOut: bool = False,
        address: int = None,
    ) -> VariableEntry:
        """Ajoute une variable

        Args:
            identifier (Identifier): l'identificateur
            variableType (IdentifierType.VariableType): le type de variable
            scope (CallableEntry): la portée
            isIn (bool, optional): drapeau _in_ pour les paramètres. Par défaut False
            isOut (bool, optional): drapeau _out_ pour les paramètres. Par défaut False
            address (int, optional): l'adresse dans la portée. Par défaut None

        Returns:
            VariableEntry: la nouvelle entrée
        """
        variable = VariableEntry(
            identifier,
            scope,
            variableType,
            inStatus=isIn,
            outStatus=isOut,
            address=address,
        )
        self.addEntry(variable)
        return variable

    def addCallable(
        self,
        identifier: Identifier,
        callableType: IdentifierType.CallableType,
        scope: CallableEntry,
        address: int,
    ) -> CallableEntry:
        """Ajoute un appelable

        Args:
            identifier (Identifier): l'identificateur
            callableType (IdentifierType.CallableType): le type d'appelable
            scope (CallableEntry): la portée
            address (int): l'adresse de début du code assembleur de l'appelable

        Returns:
            CallableEntry: la nouvelle entrée
        """
        callableEntry = None
        match callableType:
            case IdentifierType.FUNCTION:
                callableEntry = FunctionEntry(identifier, scope, address)
            case IdentifierType.PROCEDURE:
                callableEntry = ProcedureEntry(identifier, scope, address)
        self.addEntry(callableEntry)
        return callableEntry

    def addEntry(self, entry: IdentifierEntry):
        """Référence une nouvelle entrée dans _table_

        Args:
            entry (IdentifierEntry): l'identificateur entré
        """
        if isinstance(entry, CallableEntry):
            self.callableTable.append(entry)
        if isinstance(entry, VariableEntry):
            self.variableTable.append(entry)
        self.table.append(entry)

    def getByName(self, name: str) -> IdentifierEntry:
        """Récupère un identificateur référencé par son nom

        Args:
            name (str): le nom de l'identificateur recherché

        Raises:
            ValueError: l'identificateur n'existe pas

        Returns:
            IdentifierEntry: l'identificateur retrouvé
        """
        result: IdentifierEntry = None
        for entry in self.table:
            if entry.name == name:
                result = entry
                break
        if result is None:
            raise ValueError(
                f"{name} n'est pas référencé dans le tableau d'identificateur"
            )
        return result

    def __str__(self):
        string = "Index\tEntry\tName\tAddress\tScope\tType\n"
        horizBar = f"{'_'*len(string.expandtabs())}\n"
        string += horizBar
        for index, entry in enumerate(self.table):
            string += str(index) + "\t" + str(entry) + "\n"
        string += horizBar
        for index in range(len(self.identifierQueue)):
            reversedIndex = len(self.identifierQueue) - 1 - index
            ident = self.identifierQueue[reversedIndex]
            string += f"{reversedIndex}\t{ident}"
        string = horizBar + string
        return string


@unique
class IdentifierType(Enum):
    """
    Représente les types d'identificateurs possibles

    Valeurs:
        INTEGER: type entier

        BOOLEAN: type booléen

        PROCEDURE: type procédure

        FUNCTION: type fonction
    """

    INTEGER = "int"
    BOOLEAN = "boolean"
    PROCEDURE = "procedure"
    FUNCTION = "function"

    @classmethod
    @property
    def VariableType(cls):
        """
        Renvoie les types d'identificateurs considérés comme des variables.

        Returns:
            Tuple[IdentifierType]: les types d'identificateurs variables.
        """
        return cls.INTEGER, cls.BOOLEAN

    @classmethod
    @property
    def CallableType(cls):
        """
        Renvoie les types d'identificateurs considérés comme des callable.

        Returns:
            Tuple[IdentifierType]: les types d'identificateurs appelables.
        """
        return cls.PROCEDURE, cls.FUNCTION

    @property
    def isVariableType(self):
        """
        Vérifie si l'identificateur est de type variable.

        Returns:
            bool: le type d'identificateur est de type variable
        """
        return self in IdentifierType.VariableType

    @property
    def isCallableType(self):
        """
        Vérifie si l'identificateur est de type callable.

        Returns:
            bool: le type d'identificateur est de type appelable
        """
        return self in IdentifierType.CallableType


class IdentifierTypeError(Exception):
    """Raise to specify an error with Enum IdentifyType"""


class IdentifierEntry:
    """
    Représente une entrée d'identificateur dans la table des identificateurs

    Attributs:
        identifier (Identifier): l'identificateur

        scope (IdentifierEntry): la portée auquelle appartient l'identificateur

        type (IdentifierType): le type de l'identificateur

        address (int, optional): l'adresse associée à l'identificateur. Par défaut None

    """

    def __init__(
        self,
        identifier: Identifier,
        scope: IdentifierEntry,
        idType: IdentifierType,
        address: int = None,
    ):
        self.identifier = identifier
        self.scope = scope
        self.type = idType
        self.address = address

    @property
    def name(self) -> str:
        return self.identifier.value

    def __str__(self) -> str:
        string = ""
        string += str(self.identifier.value) + "\t"
        string += str(self.address) + "\t"
        if self.scope:
            string += self.scope.name + "\t"
        else:
            string += str(None) + "\t"
        string += self.type.value

        return string


class VariableEntry(IdentifierEntry):
    """
    Représente une entrée d'identificateur de variable dans la table des identificateurs

    Attributs:
        identifier (Identifier): l'identificateur de la variable

        scope (IdentifierEntry): l'entrée de l'identificateur parent dans la table

        type (IdentifierType): le type de la variable

        inStatus (bool): indique si la variable est en mode d'entrée

        outStatus (bool): indique si la variable est en mode de sortie

        address (int, optional): l'adresse dans la portée. Par défaut None
    """

    def __init__(
        self,
        identifier: Identifier,
        scope: IdentifierEntry,
        varType: IdentifierType,
        inStatus: bool = False,
        outStatus: bool = False,
        address: int = None,
    ):
        if not varType.isVariableType:
            raise IdentifierTypeError(
                f"{identifier} à ajouter n'est pas un type de variable !"
            )
        super().__init__(identifier, scope, varType, address)
        self.inStatus = inStatus
        self.outStatus = outStatus

    @property
    def isParameter(self):
        return self.inStatus

    def __str__(self) -> str:
        string = "Var\t"
        return string + super().__str__()


class CallableEntry(IdentifierEntry):
    """
    Représente une entrée d'identificateur d'appelable dans la table des identificateurs

    Attributs:
        identifier (Identifier): l'identificateur de l'appelable

        scope (IdentifierEntry): l'entrée de l'identificateur parent dans la table

        type (IdentifierType): le type de l'appelable

        address (int, optional): l'adresse de début du code assembleur de l'appelable. Par défaut None

        returnType (IdentifierType, optional): le type retourné par l'appelable. Par défaut None

        variables (List[VariableEntry]): la liste des variables locales de l'appelable

        parameters (List[VariableEntry]): la liste des paramètres de l'appelable

    """

    def __init__(
        self,
        identifier: Identifier,
        scope: IdentifierEntry,
        calType: IdentifierType,
        address: int = None,
        returnType: IdentifierType = None,
    ):
        if not calType.isCallableType:
            raise IdentifierTypeError(
                f"{identifier} à ajouter n'est pas un type d'appelable !"
            )
        super().__init__(identifier, scope, calType, address)
        self.returnType = returnType
        self.variables: List[VariableEntry] = []
        self.parameters: List[VariableEntry] = []

    def add(self, newVariable: VariableEntry):
        """
        Ajoute une nouvelle variable à la liste des variables de l'appelable.

        Args:
            newVariable (VariableEntry): La variable à ajouter.

        Raises:
            NameError: Si une variable du même nom existe déjà dans la portée de l'appelable.
        """
        for var in self.variables:
            if var.name == newVariable.name:
                raise NameError(
                    f"Une variable existe déjà dans la portée de {self.name}"
                )
        self.variables.append(newVariable)
        if newVariable.isParameter:
            self.parameters.append(newVariable)

    @property
    def nbVar(self) -> int:
        return len(self.variables)

    @property
    def nbParam(self) -> int:
        return len(self.parameters)

    def __str__(self) -> str:
        returnTypeStr = self.returnType.value if self.returnType else "None"
        return "\t".join(super().__str__().split("\t")[:-1]) + f"\t{returnTypeStr}"


class ProcedureEntry(CallableEntry):
    """
    Représente une entrée de procédure dans la table des identificateurs.

    Attributs:
        identifier (Identifier): l'identificateur de la procédure

        scope (IdentifierEntry): l'entrée de l'identificateur parent dans la table

        ddress (int, optional): l'adresse de début du code assembleur de la procédure. Par défaut None.
    """

    def __init__(
        self,
        identifier: Identifier,
        scope: IdentifierEntry,
        address: int = None,
    ):
        super().__init__(identifier, scope, IdentifierType.PROCEDURE, address)

    def __str__(self) -> str:
        string = "Proc\t"
        return string + super().__str__()


class FunctionEntry(CallableEntry):
    """
    Représente une entrée de fonction dans la table des identificateurs.

    Attributs:
        identifier (Identifier): l'identificateur de la fonction

        scope (IdentifierEntry): l'entrée de l'identificateur parent dans la table

        address (int, optional): l'adresse de début du code assembleur de la fonction. Par défaut None

        returnType (IdentifierType, optional): le type de retour de la fonction. Par défaut None
    """

    def __init__(
        self,
        identifier: Identifier,
        scope: IdentifierEntry,
        address: int = None,
        returnType: IdentifierType = None,
    ):
        super().__init__(
            identifier, scope, IdentifierType.FUNCTION, address, returnType
        )

    def __str__(self) -> str:
        string = "Func\t"
        return string + super().__str__()

    def setReturnType(self, returnType):
        self.returnType = returnType
