import argparse
import sys
from pathlib import Path
import logging
import re

sys.path.insert(0, "/Users/adar/Desktop/compiler/sly/src")


from parser import CPLParser
from lexer import CPLLexer


def main():

    print('Adar Agai', file=sys.stderr)
    parser = argparse.ArgumentParser(description='Compiler')
    parser.add_argument('-f', '--file', type=Path, help='Path file to compile', required=True)

    args = parser.parse_args()
    if args.file.suffix != '.ou':
        print('Invalid file extension', file=sys.stderr)
        return

    lexer = CPLLexer()
    parser = CPLParser()

    try:
        data = Path(args.file).read_text()

        # for tok in lexer.tokenize(data):
        #     print(f"Token: {tok.type} - {tok.value} (line {tok.lineno})")

        result = parser.parse(lexer.tokenize(data))

        if parser.errors_found == True:
            print("Errors found during parsing", file=sys.stderr)
            return

        output_file = args.file.with_suffix('.qud')

        output_code = result.code + '\nHALT\n' + 'Adar Agai'

        output_file.write_text(re.sub(r"\n\s*\n", "\n", output_code).strip())

    except FileNotFoundError as e:
        print('Input file not found', file=sys.stderr)


if __name__ == '__main__':
    main()
