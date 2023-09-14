#!PYTHONINTERPRETER

import argparse
import logging
import sys

from src.vm import VM, ExceptionVM


########################################################################
def main():
    parser = argparse.ArgumentParser(
        description="Exécute avec une machine virtuelle le code assembleur d'un programme NNP compilé"
    )
    parser.add_argument(
        "inputfile", type=str, nargs=1, help="Chemin du fichier assembleur"
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_const",
        const=logging.DEBUG,
        default=logging.INFO,
        help="active le mode débogage",
    )
    parser.add_argument(
        "-s",
        "--stepped",
        action="store_const",
        const=True,
        default=False,
        help="active une exécution par étape; mode débogage activé implicitement",
    )
    parser.add_argument(
        "-b",
        "--board",
        action="store_const",
        const=True,
        default=False,
        help="active le tableau de bord; modes débogage et par étape activés implicitement",
    )
    parser.add_argument("-v", "--version", action="version", version="%(prog)s 1.0")

    args = parser.parse_args()

    filename = args.inputfile[0]

    instructions = []
    try:
        with open(filename, "r") as f:
            for line in f:
                instructionName = line.split("(")[0]
                extractedParameters = line.split("(")[1].split(")")[0].split(",")
                parameters = []
                for strParam in extractedParameters:
                    if strParam:
                        parameters.append(int(strParam))
                instructions.append([instructionName, parameters])
    except FileNotFoundError:
        sys.exit(f"Le chemin '{filename}' ne mène vers aucun fichier.")
    except IOError as e:
        sys.exit(f"Une erreur lors de la lecture de {filename} est survenue:\n{e}\n")

    if args.board:
        args.stepped = True

    if args.stepped:
        args.debug = logging.DEBUG

    virtualMachine = VM(instructions, args.debug, args.stepped, args.board)
    try:
        virtualMachine.run()
    except ExceptionVM as e:
        sys.exit(
            f"\033[38;2;255;0;0mUne erreur lors de l'exécution de la machine virtuelle est survenue:\033[0m\n{e}"
        )


########################################################################

if __name__ == "__main__":
    main()
