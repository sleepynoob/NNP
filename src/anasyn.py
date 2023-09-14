#!/usr/bin/python

## 	@package anasyn
# 	Syntactical Analyser package.
#

import argparse
import logging

import analex
from Compiler import Compiler
from IdentifierTable import IdentifierType

logger = logging.getLogger("anasyn")

DEBUG = False
LOGGING_LEVEL = logging.DEBUG

compiler = Compiler()
lineNumber = 0


class AnaSynException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


########################################################################
#### Syntactical Diagrams
########################################################################


def program(lexical_analyser):
    global compiler, lineNumber
    compiler.debutProg()
    specifProgPrinc(lexical_analyser)
    lexical_analyser.acceptKeyword("is")
    lineNumber += 1
    corpsProgPrinc(lexical_analyser)


def specifProgPrinc(lexical_analyser):
    global compiler, lineNumber
    lexical_analyser.acceptKeyword("procedure")
    ident = lexical_analyser.acceptIdentifier()
    identifier = lexical_analyser.lexical_units[lexical_analyser.lexical_unit_index - 1]
    compiler.addCallable(identifier, IdentifierType.PROCEDURE, 0)
    logger.debug("Name of program : " + ident)


def corpsProgPrinc(lexical_analyser):
    global compiler, lineNumber
    if not lexical_analyser.isKeyword("begin"):
        logger.debug("Parsing declarations")
        partieDecla(lexical_analyser)
        logger.debug("End of declarations")
    lexical_analyser.acceptKeyword("begin")
    lineNumber += 1
    if not lexical_analyser.isKeyword("end"):
        logger.debug("Parsing instructions")
        suiteInstr(lexical_analyser)
        logger.debug("End of instructions")
    lexical_analyser.acceptKeyword("end")
    lexical_analyser.acceptFel()
    compiler.finProg()
    logger.debug("End of program")


def partieDecla(lexical_analyser):
    global compiler, lineNumber
    if lexical_analyser.isKeyword("procedure") or lexical_analyser.isKeyword(
        "function"
    ):
        compiler.declaredCallables = True
        i = len(compiler.instructions)
        listeDeclaOp(lexical_analyser)
        j = len(compiler.instructions)
        compiler.insertInstruction("tra", i, j + 1 + 1)
        if not lexical_analyser.isKeyword("begin"):
            listeDeclaVar(lexical_analyser)

    else:
        listeDeclaVar(lexical_analyser)


def listeDeclaOp(lexical_analyser):
    global compiler, lineNumber
    declaOp(lexical_analyser)
    lexical_analyser.acceptCharacter(";")
    if lexical_analyser.isKeyword("procedure") or lexical_analyser.isKeyword(
        "function"
    ):
        listeDeclaOp(lexical_analyser)


def declaOp(lexical_analyser):
    global compiler, lineNumber
    if lexical_analyser.isKeyword("procedure"):
        procedure(lexical_analyser)
    if lexical_analyser.isKeyword("function"):
        fonction(lexical_analyser)


def procedure(lexical_analyser):
    global compiler, lineNumber
    lexical_analyser.acceptKeyword("procedure")
    ident = lexical_analyser.acceptIdentifier()
    logger.debug("Name of procedure : " + ident)
    identifier = lexical_analyser.lexical_units[lexical_analyser.lexical_unit_index - 1]
    compiler.addCallable(identifier, IdentifierType.PROCEDURE)
    partieFormelle(lexical_analyser)
    lexical_analyser.acceptKeyword("is")
    lineNumber += 1
    corpsProc(lexical_analyser)
    compiler.retourProc()


def fonction(lexical_analyser):
    global compiler, lineNumber
    lexical_analyser.acceptKeyword("function")
    ident = lexical_analyser.acceptIdentifier()
    logger.debug("Name of function : " + ident)
    identifier = lexical_analyser.lexical_units[lexical_analyser.lexical_unit_index - 1]
    functionEntry = compiler.addCallable(identifier, IdentifierType.FUNCTION)
    partieFormelle(lexical_analyser)
    lexical_analyser.acceptKeyword("return")
    returnType = nnpType(lexical_analyser)
    functionEntry.setReturnType(returnType)
    lexical_analyser.acceptKeyword("is")
    lineNumber += 1
    corpsFonct(lexical_analyser)


def corpsProc(lexical_analyser):
    global compiler, lineNumber
    if not lexical_analyser.isKeyword("begin"):
        partieDeclaProc(lexical_analyser)
    lexical_analyser.acceptKeyword("begin")
    lineNumber += 1
    suiteInstr(lexical_analyser)
    lexical_analyser.acceptKeyword("end")
    lineNumber += 1
    compiler.leaveScope()


def corpsFonct(lexical_analyser):
    global compiler, lineNumber
    if not lexical_analyser.isKeyword("begin"):
        partieDeclaProc(lexical_analyser)
    lexical_analyser.acceptKeyword("begin")
    lineNumber += 1
    suiteInstrNonVide(lexical_analyser)
    lexical_analyser.acceptKeyword("end")
    lineNumber += 1
    compiler.leaveScope()


def partieFormelle(lexical_analyser):
    global compiler, lineNumber
    lexical_analyser.acceptCharacter("(")
    if not lexical_analyser.isCharacter(")"):
        listeSpecifFormelles(lexical_analyser)
    lexical_analyser.acceptCharacter(")")


def listeSpecifFormelles(lexical_analyser):
    global compiler, lineNumber
    specif(lexical_analyser)
    if not lexical_analyser.isCharacter(")"):
        lexical_analyser.acceptCharacter(";")
        listeSpecifFormelles(lexical_analyser)


def specif(lexical_analyser):
    global compiler, lineNumber
    listeIdent(lexical_analyser)
    lexical_analyser.acceptCharacter(":")
    isOut = False
    if lexical_analyser.isKeyword("in"):
        isOut = mode(lexical_analyser)

    varType = nnpType(lexical_analyser)
    compiler.emptyQueue(varType, isOut)


def mode(lexical_analyser) -> bool:
    global compiler, lineNumber
    lexical_analyser.acceptKeyword("in")
    isOut = False
    if lexical_analyser.isKeyword("out"):
        lexical_analyser.acceptKeyword("out")
        isOut = True
        logger.debug("in out parameter")
    else:
        logger.debug("in parameter")
    return isOut


def nnpType(lexical_analyser) -> IdentifierType:
    global compiler, lineNumber
    varType = None
    if lexical_analyser.isKeyword("integer"):
        lexical_analyser.acceptKeyword("integer")
        logger.debug("integer type")
        varType = IdentifierType.INTEGER
    elif lexical_analyser.isKeyword("boolean"):
        lexical_analyser.acceptKeyword("boolean")
        logger.debug("boolean type")
        varType = IdentifierType.BOOLEAN
    else:
        logger.error("Unknown type found <" + lexical_analyser.get_value() + ">!")
        raise AnaSynException(
            "Unknown type found <" + lexical_analyser.get_value() + ">!"
        )
    return varType


def partieDeclaProc(lexical_analyser):
    global compiler, lineNumber
    listeDeclaVar(lexical_analyser)


def listeDeclaVar(lexical_analyser):
    global compiler, lineNumber
    declaVar(lexical_analyser)
    if lexical_analyser.isIdentifier():
        listeDeclaVar(lexical_analyser)


def declaVar(lexical_analyser):
    global compiler, lineNumber
    n = listeIdent(lexical_analyser)
    lexical_analyser.acceptCharacter(":")
    logger.debug("now parsing type...")
    compiler.reserver(n)
    varType = nnpType(lexical_analyser)
    compiler.emptyQueue(varType)
    lexical_analyser.acceptCharacter(";")
    lineNumber += 1


def listeIdent(lexical_analyser) -> int:
    global compiler, lineNumber
    ident = lexical_analyser.acceptIdentifier()
    logger.debug("identifier found: " + str(ident))
    identifier = lexical_analyser.lexical_units[lexical_analyser.lexical_unit_index - 1]
    compiler.addQueue(identifier)
    if lexical_analyser.isCharacter(","):
        lexical_analyser.acceptCharacter(",")
        return listeIdent(lexical_analyser) + 1
    return 1


def suiteInstrNonVide(lexical_analyser):
    global compiler, lineNumber
    instr(lexical_analyser)
    if lexical_analyser.isCharacter(";"):
        lexical_analyser.acceptCharacter(";")
        suiteInstrNonVide(lexical_analyser)


def suiteInstr(lexical_analyser):
    global compiler, lineNumber
    if not lexical_analyser.isKeyword("end"):
        suiteInstrNonVide(lexical_analyser)


def instr(lexical_analyser):
    global compiler, lineNumber
    if lexical_analyser.isKeyword("while"):
        boucle(lexical_analyser)
    elif lexical_analyser.isKeyword("if"):
        altern(lexical_analyser)
    elif lexical_analyser.isKeyword("get") or lexical_analyser.isKeyword("put"):
        es(lexical_analyser)
    elif lexical_analyser.isKeyword("return"):
        retour(lexical_analyser)
    elif lexical_analyser.isIdentifier():
        ident = lexical_analyser.acceptIdentifier()
        identifier = compiler.identifierTable.getByName(ident)
        if lexical_analyser.isSymbol(":="):
            if identifier.type.isCallableType:
                raise AnaSynException(
                    f"Cannot allocate value to callable '{identifier.name}'"
                )
            if identifier.isParameter:
                if identifier.outStatus:
                    compiler.empilerParam(identifier.address)
                else:
                    raise AnaSynException(
                        f"{ident} is not set to 'out' but is beeing modified at {lineNumber}"  # TODO
                    )
            else:
                compiler.empilerAd(identifier.address)
            lexical_analyser.acceptSymbol(":=")
            expression(lexical_analyser)
            compiler.affectation()
            logger.debug("parsed affectation")
        elif lexical_analyser.isCharacter("("):
            compiler.stackCallable(identifier)
            lexical_analyser.acceptCharacter("(")
            compiler.reserverBloc()
            nbParam = 0
            if not lexical_analyser.isCharacter(")"):
                nbParam = listePe(lexical_analyser)
            if identifier.nbParam != nbParam:
                raise AnaSynException(
                    f"{identifier.name} expects {identifier.nbParam} parameter{'s' if identifier.nbParam > 1 else ''}, however {nbParam} were passed"
                )  # TODO
            compiler.traStat(identifier.address + 1, nbParam)
            lexical_analyser.acceptCharacter(")")
            compiler.unstackCallable()
            logger.debug("parsed procedure call")
        else:
            logger.error("Expecting procedure call or affectation!")
            raise AnaSynException("Expecting procedure call or affectation!")
    else:
        logger.error("Unknown Instruction <" + lexical_analyser.get_value() + ">!")
        raise AnaSynException(
            "Unknown Instruction <" + lexical_analyser.get_value() + ">!"
        )
    lineNumber += 1


def listePe(lexical_analyser) -> int:
    global compiler, lineNumber
    expression(lexical_analyser)
    if lexical_analyser.isCharacter(","):
        lexical_analyser.acceptCharacter(",")
        return 1 + listePe(lexical_analyser)
    return 1


def expression(lexical_analyser):
    global compiler, lineNumber
    logger.debug("parsing expression: " + str(lexical_analyser.get_value()))
    exp1(lexical_analyser)
    if lexical_analyser.isKeyword("or"):
        lexical_analyser.acceptKeyword("or")
        exp1(lexical_analyser)
        compiler.ou()


def exp1(lexical_analyser):
    global compiler, lineNumber
    logger.debug("parsing exp1")
    exp2(lexical_analyser)
    if lexical_analyser.isKeyword("and"):
        lexical_analyser.acceptKeyword("and")
        exp2(lexical_analyser)
        compiler.et()


def exp2(lexical_analyser):
    global compiler, lineNumber
    logger.debug("parsing exp2")
    operandCompiler: callable = None
    exp3(lexical_analyser)
    if (
        lexical_analyser.isSymbol("<")
        or lexical_analyser.isSymbol("<=")
        or lexical_analyser.isSymbol(">")
        or lexical_analyser.isSymbol(">=")
    ):
        operandCompiler = opRel(lexical_analyser)
        exp3(lexical_analyser)
    elif lexical_analyser.isSymbol("=") or lexical_analyser.isSymbol("/="):
        operandCompiler = opRel(lexical_analyser)
        exp3(lexical_analyser)
    if operandCompiler:
        operandCompiler()


def opRel(lexical_analyser) -> callable:
    global compiler, lineNumber
    logger.debug("parsing relationnal operator: " + lexical_analyser.get_value())
    if lexical_analyser.isSymbol("<"):
        lexical_analyser.acceptSymbol("<")
        return compiler.inf
    elif lexical_analyser.isSymbol("<="):
        lexical_analyser.acceptSymbol("<=")
        return compiler.infeg
    elif lexical_analyser.isSymbol(">"):
        lexical_analyser.acceptSymbol(">")
        return compiler.sup
    elif lexical_analyser.isSymbol(">="):
        lexical_analyser.acceptSymbol(">=")
        return compiler.supeg
    elif lexical_analyser.isSymbol("="):
        lexical_analyser.acceptSymbol("=")
        return compiler.egal
    elif lexical_analyser.isSymbol("/="):
        lexical_analyser.acceptSymbol("/=")
        return compiler.diff
    else:
        msg = "Unknown relationnal operator <" + lexical_analyser.get_value() + ">!"
        logger.error(msg)
        raise AnaSynException(msg)


def exp3(lexical_analyser):
    global compiler, lineNumber
    logger.debug("parsing exp3")
    exp4(lexical_analyser)
    if lexical_analyser.isCharacter("+") or lexical_analyser.isCharacter("-"):
        operandeCompiler = opAdd(lexical_analyser)
        exp4(lexical_analyser)
        operandeCompiler()


def opAdd(lexical_analyser) -> callable:
    global compiler, lineNumber
    logger.debug("parsing additive operator: " + lexical_analyser.get_value())
    if lexical_analyser.isCharacter("+"):
        lexical_analyser.acceptCharacter("+")
        return compiler.add
    elif lexical_analyser.isCharacter("-"):
        lexical_analyser.acceptCharacter("-")
        return compiler.sous
    else:
        msg = "Unknown additive operator <" + lexical_analyser.get_value() + ">!"
        logger.error(msg)
        raise AnaSynException(msg)


def exp4(lexical_analyser):
    global compiler, lineNumber
    logger.debug("parsing exp4")
    prim(lexical_analyser)
    if lexical_analyser.isCharacter("*") or lexical_analyser.isCharacter("/"):
        operandeCompiler = opMult(lexical_analyser)
        prim(lexical_analyser)
        if operandeCompiler:
            operandeCompiler()


def opMult(lexical_analyser) -> callable:
    global compiler, lineNumber
    logger.debug("parsing multiplicative operator: " + lexical_analyser.get_value())
    if lexical_analyser.isCharacter("*"):
        lexical_analyser.acceptCharacter("*")
        return compiler.mult
    elif lexical_analyser.isCharacter("/"):
        lexical_analyser.acceptCharacter("/")
        return compiler.div
    else:
        msg = "Unknown multiplicative operator <" + lexical_analyser.get_value() + ">!"
        logger.error(msg)
        raise AnaSynException(msg)


def prim(lexical_analyser):
    global compiler, lineNumber
    logger.debug("parsing prim")
    operandeCompiler = None
    if (
        lexical_analyser.isCharacter("+")
        or lexical_analyser.isCharacter("-")
        or lexical_analyser.isKeyword("not")
    ):
        operandeCompiler = opUnaire(lexical_analyser)
    elemPrim(lexical_analyser)
    if operandeCompiler:
        operandeCompiler()


def opUnaire(lexical_analyser) -> callable:
    global compiler, lineNumber
    logger.debug("parsing unary operator: " + lexical_analyser.get_value())
    if lexical_analyser.isCharacter("+"):
        lexical_analyser.acceptCharacter("+")
        return None
    elif lexical_analyser.isCharacter("-"):
        lexical_analyser.acceptCharacter("-")
        return compiler.moins
    elif lexical_analyser.isKeyword("not"):
        lexical_analyser.acceptKeyword("not")
        return compiler.non
    else:
        msg = "Unknown additive operator <" + lexical_analyser.get_value() + ">!"
        logger.error(msg)
        raise AnaSynException(msg)


def elemPrim(lexical_analyser):
    global compiler, lineNumber
    logger.debug("parsing elemPrim: " + str(lexical_analyser.get_value()))
    if lexical_analyser.isCharacter("("):
        lexical_analyser.acceptCharacter("(")
        expression(lexical_analyser)
        lexical_analyser.acceptCharacter(")")
    elif (
        lexical_analyser.isInteger()
        or lexical_analyser.isKeyword("true")
        or lexical_analyser.isKeyword("false")
    ):
        valeur(lexical_analyser)
    elif lexical_analyser.isIdentifier():
        ident = lexical_analyser.acceptIdentifier()
        identifier = compiler.identifierTable.getByName(ident)
        if lexical_analyser.isCharacter("("):  # identifier is callable
            compiler.stackCallable(identifier)
            lexical_analyser.acceptCharacter("(")
            compiler.reserverBloc()
            nbParam = 0
            if not lexical_analyser.isCharacter(")"):
                nbParam = listePe(lexical_analyser)
            if identifier.nbParam != nbParam:
                raise AnaSynException(
                    f"{identifier.name} expects {identifier.nbParam} parameter{'s' if identifier.nbParam > 1 else ''}, however {nbParam} were passed"
                )  # TODO
            lexical_analyser.acceptCharacter(")")
            compiler.unstackCallable()
            logger.debug("parsed procedure call")
            logger.debug("Call to function: " + ident)
            compiler.traStat(identifier.address + 1, nbParam)
        else:
            logger.debug("Use of an identifier as an expression: " + ident)
            if identifier.isParameter:
                if identifier.outStatus:
                    compiler.empilerParam(identifier.address)
                else:
                    compiler.empilerAd(identifier.address)
                compiler.valeurPile()
            else:
                compiler.empilerAd(identifier.address)
                if compiler.passingParam:
                    passOutParam = compiler.unstackOutStatus()
                    if not passOutParam:
                        compiler.valeurPile()
                else:
                    compiler.valeurPile()
    else:
        logger.error("Unknown Value!")
        raise AnaSynException("Unknown Value!")


def valeur(lexical_analyser) -> int | bool:
    global compiler, lineNumber
    if lexical_analyser.isInteger():
        entier = lexical_analyser.acceptInteger()
        logger.debug("integer value: " + str(entier))
        compiler.empiler(entier)
        return entier
    elif lexical_analyser.isKeyword("true") or lexical_analyser.isKeyword("false"):
        vtype = valBool(lexical_analyser)
        return vtype
    else:
        logger.error("Unknown Value! Expecting an integer or a boolean value!")
        raise AnaSynException(
            "Unknown Value ! Expecting an integer or a boolean value!"
        )


def valBool(lexical_analyser) -> bool:
    global compiler, lineNumber
    if lexical_analyser.isKeyword("true"):
        lexical_analyser.acceptKeyword("true")
        compiler.empiler(1)
        logger.debug("boolean true value")
        return True
    else:
        logger.debug("boolean false value")
        lexical_analyser.acceptKeyword("false")
        compiler.empiler(0)
        return False


def es(lexical_analyser):
    global compiler, lineNumber
    logger.debug("parsing E/S instruction: " + lexical_analyser.get_value())
    if lexical_analyser.isKeyword("get"):
        lexical_analyser.acceptKeyword("get")
        lexical_analyser.acceptCharacter("(")
        ident = lexical_analyser.acceptIdentifier()
        lexical_analyser.acceptCharacter(")")
        identifier = compiler.identifierTable.getByName(ident)
        compiler.empilerAd(identifier.address)
        compiler.get()
        logger.debug("Call to get " + ident)
    elif lexical_analyser.isKeyword("put"):
        lexical_analyser.acceptKeyword("put")
        lexical_analyser.acceptCharacter("(")
        expression(lexical_analyser)
        lexical_analyser.acceptCharacter(")")
        logger.debug("Call to put")
        compiler.put()
    else:
        logger.error("Unknown E/S instruction!")
        raise AnaSynException("Unknown E/S instruction!")


def boucle(lexical_analyser):
    global compiler, lineNumber
    logger.debug("parsing while loop: ")
    lexical_analyser.acceptKeyword("while")
    tzeAddress = compiler.nestedLoop
    traAddress = compiler.nestedLoop
    compiler.nestedLoop += 1
    if compiler.declaredCallables:
        tzeAddress += 1
        traAddress += 1
    ligne1 = len(compiler.instructions)
    traAddress += ligne1 + 1
    expression(lexical_analyser)
    lexical_analyser.acceptKeyword("loop")
    ligne2 = len(compiler.instructions)
    suiteInstr(lexical_analyser)
    ligne3 = len(compiler.instructions)
    tzeAddress += ligne3 + 1 + 1 + 1
    compiler.tra(traAddress)
    compiler.insertInstruction("tze", ligne2, tzeAddress)
    lexical_analyser.acceptKeyword("end")
    compiler.nestedLoop -= 1
    logger.debug("end of while loop ")


def altern(lexical_analyser):
    global compiler, lineNumber
    logger.debug("parsing if: ")
    lexical_analyser.acceptKeyword("if")
    expression(lexical_analyser)
    lexical_analyser.acceptKeyword("then")
    lineNumber += 1
    ligne1 = len(compiler.instructions)
    tzeAddress = compiler.nestedAltern
    compiler.nestedAltern += 1
    if compiler.declaredCallables:
        tzeAddress += 1
    suiteInstr(lexical_analyser)
    ligne2 = len(compiler.instructions)
    tzeAddress += ligne2 + 1 + 1
    if lexical_analyser.isKeyword("else"):
        lexical_analyser.acceptKeyword("else")
        lineNumber += 1
        ligne3 = len(compiler.instructions)
        suiteInstr(lexical_analyser)
        ligne4 = len(compiler.instructions)
        traAddress = ligne4 + 1 + 1 + 1
        if compiler.declaredCallables:
            traAddress += 1
        compiler.insertInstruction("tra", ligne3, traAddress)
        tzeAddress += 1
    compiler.insertInstruction("tze", ligne1, tzeAddress)
    compiler.nestedAltern -= 1
    lexical_analyser.acceptKeyword("end")
    logger.debug("end of if")


def retour(lexical_analyser):
    global compiler, lineNumber
    logger.debug("parsing return instruction")
    lexical_analyser.acceptKeyword("return")
    expression(lexical_analyser)
    compiler.retourFonct()


########################################################################
def main():
    parser = argparse.ArgumentParser(
        description="Do the syntactical analysis of a NNP program."
    )
    parser.add_argument(
        "inputfile", type=str, nargs=1, help="name of the input source file"
    )
    parser.add_argument(
        "-o",
        "--outputfile",
        dest="outputfile",
        action="store",
        default="",
        help="name of the output file (default: stdout)",
    )
    parser.add_argument("-v", "--version", action="version", version="%(prog)s 1.0")
    parser.add_argument(
        "-d",
        "--debug",
        action="store_const",
        const=logging.DEBUG,
        default=logging.INFO,
        help="show debugging info on output",
    )
    parser.add_argument(
        "--show-ident-table",
        action="store_true",
        help="shows the final identifiers table",
    )
    args = parser.parse_args()

    filename = args.inputfile[0]
    f = None
    try:
        f = open(filename, "r")
    except:
        print("Error: can't open input file!")
        return

    outputFilename = args.outputfile

    # create logger
    LOGGING_LEVEL = args.debug
    logger.setLevel(LOGGING_LEVEL)
    ch = logging.StreamHandler()
    ch.setLevel(LOGGING_LEVEL)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    lexical_analyser = analex.LexicalAnalyser()

    lineIndex = 0
    for line in f:
        line = line.rstrip("\r\n")
        lexical_analyser.analyse_line(lineIndex, line)
        lineIndex = lineIndex + 1
    f.close()

    # launch the analysis of the program
    lexical_analyser.init_analyser()
    program(lexical_analyser)

    if args.show_ident_table:
        identifierTable = compiler.identifierTable
        print(compiler)
        print("------ IDENTIFIER TABLE ------")
        print(identifierTable)
        print("------ END OF IDENTIFIER TABLE ------")

    if outputFilename != "":
        try:
            compiler.saveInstructions(outputFilename)
        except:
            print("Error: can't open output file!")
            return
    else:
        print(compiler)


########################################################################

if __name__ == "__main__":
    main()
