#!PYTHONINTERPRETER

import argparse
import logging
import sys
from pathlib import Path

import colorlog

sys.path.insert(0, str(Path(".", "src").absolute()))

import analex
import anasyn


########################################################################
def main():
    parser = argparse.ArgumentParser(description="Compile un programme NilNovi")
    parser.add_argument(
        "inputfile", type=str, nargs=1, help="Chemin du programme NilNovi"
    )
    parser.add_argument(
        "-o",
        "--outputfile",
        dest="outputfile",
        action="store",
        default="",
        help="Chemin où enregistrer le programme assembleur compilé",
    )
    parser.add_argument("-v", "--version", action="version", version="%(prog)s 1.0")
    parser.add_argument(
        "-d",
        "--debug",
        action="store_const",
        const=logging.DEBUG,
        default=logging.INFO,
        help="active le mode débogage",
    )
    parser.add_argument(
        "--show-ident-table",
        action="store_true",
        help="affiche le tableau d'identificateur final",
    )
    args = parser.parse_args()

    filename = args.inputfile[0]
    outputFilename = args.outputfile

    # Logger creation
    LOGGING_LEVEL = args.debug
    anasyn.logger.setLevel(LOGGING_LEVEL)
    ch = logging.StreamHandler()
    ch.setLevel(LOGGING_LEVEL)
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
    anasyn.logger.addHandler(ch)

    lexical_analyser = analex.LexicalAnalyser()

    try:
        with open(filename, "r") as f:
            for lineIndex, line in enumerate(f):
                line = line.rstrip("\r\n")
                lexical_analyser.analyse_line(lineIndex, line)
    except FileNotFoundError:
        sys.exit(f"Le chemin '{filename}' ne mène vers aucun fichier.")
    except IOError as e:
        sys.exit(f"Une erreur lors de la lecture de {filename} est survenue:\n{e}\n")
    except analex.AnaLexException as e:
        sys.exit(
            f"\033[38;2;255;0;0mUne erreur lors de l'analyse syntaxique est survenue:\033[0m\n{e}"
        )

    try:
        lexical_analyser.init_analyser()
        anasyn.program(lexical_analyser)
    except anasyn.AnaSynException as e:
        sys.exit(
            (
                f"\033[38;2;255;0;0mUne erreur lors de la compilation est survenue:\033[0m\n{e}"
            )
        )

    if args.show_ident_table:
        idStr = str(anasyn.compiler.identifierTable)
        print("Tableau d'identificateurs".center(len(idStr.split("\n")[0]), "_"))
        print(idStr)

    if outputFilename != "":
        try:
            anasyn.compiler.saveInstructions(outputFilename)
        except FileNotFoundError:
            sys.exit(f"Le chemin '{outputFilename}' n'est pas valide")
        except IOError as e:
            sys.exit(
                f"Une erreur est survenue lors de la sauvegarde des instructions:\n{e}"
            )
    else:
        print(anasyn.compiler)


########################################################################

if __name__ == "__main__":
    main()
