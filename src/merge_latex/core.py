"""Core functionality for merging LaTeX files.

This module provides the core functionality for the merge-latex package,
including functions to extract macros, replace macros in paths, and merge
multiple LaTeX files into one consolidated document.
"""
import glob
import os
import re
import zipfile
from typing import Dict

def extract_macros(content: str) -> Dict[str, str]:
    """Extract newcommand definitions as a dictionary.
    
    Parameters
    ----------
    content : str
        The LaTeX content to extract macros from
        
    Returns
    -------
    Dict[str, str]
        Dictionary mapping macro names to their values
    """
    macro_pattern = r'\\newcommand\{\\(\w+)\}\{([^\}]+)\}'
    macros = {}
    for match in re.finditer(macro_pattern, content):
        macros[match.group(1)] = match.group(2)
    return macros


def replace_macros_in_path(path: str, macros: Dict[str, str]) -> str:
    """Replace macros only in paths used in include and input commands.
    
    Parameters
    ----------
    path : str
        The path to replace macros in
    macros : Dict[str, str]
        Dictionary mapping macro names to their values
        
    Returns
    -------
    str
        Path with macros replaced
    """
    for macro, value in macros.items():
        path = path.replace(f"\\{macro}", value)
    return path


def expand_main(content: str, files: Dict[str, str], macros: Dict[str, str], current_path: str = "") -> str:
    """Expand include and input commands in the content.
    
    Parameters
    ----------
    content : str
        The LaTeX content to expand
    files : Dict[str, str]
        Dictionary mapping file paths to their contents
    macros : Dict[str, str]
        Dictionary mapping macro names to their values
    current_path : str, optional
        Current working directory path, by default ""
        
    Returns
    -------
    str
        Content with all includes expanded
    """
    include_pattern = r'\\(?:include|input)\{([^}]+)\}'
    
    def find_file(included_path):
        # Try different possible paths
        possible_paths = [
            included_path + '.tex',
            included_path,
            os.path.join(current_path, included_path + '.tex'),
            os.path.join(current_path, included_path)
        ]
        
        for path in possible_paths:
            if path in files:
                return path

            # replace path separators and normalize
            norm_path = os.path.normpath(path.replace('\\', '/'))
            if norm_path in files:
                return norm_path
        return None

    while re.search(include_pattern, content):
        match = re.search(include_pattern, content)
        included_path = replace_macros_in_path(match.group(1), macros)
        included_path = os.path.join(current_path, included_path)

        include_file = find_file(included_path)
        
        if include_file:
            included_content = files[include_file]
            # Update current_path for nested includes
            new_current_path = os.path.dirname(include_file)
            # Recursively expand includes in the included content
            included_content = expand_main(included_content, files, macros, new_current_path)
            # TODO: handle include and input differently, with include adding a new page
            content = content.replace(match.group(0), included_content)
        else:
            content = content.replace(match.group(0), "")
    
    return content


def merge_tex_files(main_content: str, files: Dict[str, str], main_dir: str = '') -> str:
    """Merge multiple LaTeX files into one.
    
    Parameters
    ----------
    main_content : str
        Content of the main LaTeX file
    files : Dict[str, str]
        Dictionary mapping file paths to their contents
    main_dir : str, optional
        Directory of the main file, by default ''
        
    Returns
    -------
    str
        Merged LaTeX content
    """
    # Extract macros without altering their original definition
    macros = extract_macros(main_content)

    # Expand includes while resolving paths with macros
    expanded_content = expand_main(
        main_content, files, macros, current_path=main_dir
    )

    return expanded_content


def read_tex_files(source: str) -> Dict[str, str]:
    """Read all .tex files from a directory or zip file.
    
    Parameters
    ----------
    source : str
        Path to a directory or zip file containing LaTeX files
        
    Returns
    -------
    Dict[str, str]
        Dictionary mapping file paths to their contents
        
    Raises
    ------
    ValueError
        If the source is neither a valid directory nor a zip file
    """
    files = {}
    
    # Check if source is a zip file
    if os.path.isfile(source) and source.lower().endswith('.zip'):
        try:
            with zipfile.ZipFile(source, 'r') as zip_ref:
                # Get list of .tex files in the zip
                tex_files = [f for f in zip_ref.namelist() if f.lower().endswith('.tex')]
                
                # Determine common prefix to remove (if any)
                common_prefix = os.path.commonprefix(tex_files) if tex_files else ""
                if common_prefix and not common_prefix.endswith('/'):
                    common_prefix = os.path.dirname(common_prefix) + '/'
                    if common_prefix == '/':  # Avoid removing root
                        common_prefix = ""
                
                # Read each .tex file
                for tex_file in tex_files:
                    # Create path relative to the common prefix
                    rel_path = tex_file
                    if common_prefix and tex_file.startswith(common_prefix):
                        rel_path = tex_file[len(common_prefix):]
                    
                    # Read file content
                    with zip_ref.open(tex_file) as f:
                        content = f.read().decode('utf-8', errors='replace')
                        files[rel_path] = content
                
        except zipfile.BadZipFile:
            raise ValueError(f"The file '{source}' is not a valid zip file.")
    
    # Check if source is a directory
    elif os.path.isdir(source):
        # Use relative paths from the provided directory
        for filepath in glob.glob(os.path.join(source, "**", "*.tex"), recursive=True):
            rel_path = os.path.relpath(filepath, source)
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                files[rel_path] = f.read()
    
    else:
        raise ValueError(f"The source '{source}' is neither a directory nor a zip file.")
    
    return files
