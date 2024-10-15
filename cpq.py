import argparse
import sys
from pathlib import Path
import logging


sys.path.insert(0, "/Users/adar/Desktop/compiler/sly/src")

from parser import CPLParser
from lexer import CPLLexer

def main():
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

        tokens = lexer.tokenize(data)

        for token in tokens:
            print(token)

        result = parser.parse(lexer.tokenize(data))

        if parser.errors_found:
            print('Errors found during parsing', file=sys.stderr)

        print(result)
        output_file = args.file.with_suffix('.qud')
        output_file.write_text(result)
 
    except FileNotFoundError as e:
        print('Input file not found', file=sys.stderr)


if __name__ == '__main__':
    main()
