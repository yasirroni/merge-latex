"""CLI entry point for the merge-latex package.

This module provides a command-line interface (CLI) to merge multiple LaTeX files 
into one consolidated document.

Example:
    $ merge-latex path/to/latex/dir
    $ merge-latex path/to/latex/zip_file.zip
    $ merge-latex --main main.tex --output merged.tex path/to/latex/dir
    $ merge-latex --main main.tex --output merged.tex path/to/latex/zip_file.zip
"""
import argparse
import os
import sys

from . import __version__
from .core import read_tex_files, merge_tex_files



def main():
    """
    Entry point for the merge-latex CLI.
    
    This function parses command-line arguments to merge LaTeX files.
    
    Parameters
    ----------
    None
    
    Returns
    -------
    None
    """
    parser = argparse.ArgumentParser(
        description="CLI for merging LaTeX files."
    )
        
    parser.add_argument(
        "source",
        type=str,
        help="Directory or zip file containing LaTeX files"
    )
    parser.add_argument(
        "--main",
        "-m",
        type=str,
        default="main.tex",
        help="Main LaTeX file to use as entry point (default: main.tex)"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="",
        help=(
            "Output file path (default: <main>_merged.tex if <source> is a"
            " directory, else the zip)"
        )
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"merge-latex {__version__}",
        help="Show the version and exit"
    )
    
    args = parser.parse_args()
    
    try:
        # Read all .tex files from the directory or zip
        files = read_tex_files(args.source)
        
        if not files:
            print(f"No .tex files found in '{args.source}'.")
            sys.exit(1)
            
        # Find main file
        main_file = args.main
        if main_file not in files:
            # Try to find it with relative path
            for k in files:
                if main_file in k or k.endswith('/' + main_file) or k.endswith('\\' + main_file):
                    main_file = k
                    print(f"Using '{main_file}' as the main file.")
                    break
            else:
                print(f"Error: Main file '{main_file}' not found.")
                print("Available files:")
                for f in sorted(files.keys()):
                    print(f"  {f}")
                sys.exit(1)
        
        # Get main content
        main_content = files[main_file]
        main_dir = os.path.dirname(main_file)
        
        # Merge files
        merged_content = merge_tex_files(main_content, files, main_dir)
        
        # Write merged content to output file
        if not args.output:
            if os.path.isdir(args.source):
                base, _ = os.path.splitext(os.path.join(args.source, main_file))
            else:
                base, _ = os.path.splitext(args.source)
            args.output = f"{base}_merged.tex"

        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(merged_content)
        
        for i in files.keys():
            print(i)
        print(main_file)
        print(f"Merged files successfully into '{args.output}'")
        
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
