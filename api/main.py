import json
import os
import re
from typing import Dict

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel

class TexFiles(BaseModel):
    main_file: str
    files: Dict[str, str]

app = FastAPI()

# CORS middleware to allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_version():
    with open(os.path.join(os.path.dirname(__file__), '../package.json')) as f:
        package_json = json.load(f)
        return package_json.get('version', '0.0.0')

def extract_macros(content):
    """Extract newcommand definitions as a dictionary."""
    macro_pattern = r'\\newcommand\{\\(\w+)\}\{([^\}]+)\}'
    macros = {}
    for match in re.finditer(macro_pattern, content):
        macros[match.group(1)] = match.group(2)
    return macros

def replace_macros_in_path(path, macros):
    """Replace macros only in paths used in include and input commands."""
    for macro, value in macros.items():
        path = path.replace(f"\\{macro}", value)
    return path

def expand_includes(content, files, macros, current_path=""):
    """Expand include and input commands in the content."""
    include_pattern = r'\\(?:include|input)\{([^}]+)\}'
    
    def find_file(included_path):
        # Try different possible paths
        possible_paths = [
            included_path + '.tex',
            included_path,
            f"src/{included_path}.tex",
            f"chapters/{included_path}.tex",
            os.path.join(current_path, included_path + '.tex'),
            os.path.join(current_path, included_path)
        ]
        
        for path in possible_paths:
            if path in files:
                return path
            # Normalize path separators
            norm_path = path.replace('\\', '/').replace('//', '/')
            if norm_path in files:
                return norm_path
        return None

    while re.search(include_pattern, content):
        match = re.search(include_pattern, content)
        included_path = replace_macros_in_path(match.group(1), macros)
        
        include_file = find_file(included_path)
        
        if include_file:
            included_content = files[include_file]
            # Update current_path for nested includes
            new_current_path = os.path.dirname(include_file)
            # Recursively expand includes in the included content
            included_content = expand_includes(included_content, files, macros, new_current_path)
            # TODO: handle include and input differently, with include adding a new page
            content = content.replace(match.group(0), included_content)
        else:
            print(f"Warning: File {included_path} not found!")
            content = content.replace(match.group(0), "")
    
    return content

def merge_tex_files(main_content, files):
    """Merge multiple LaTeX files into one."""
    # Extract macros without altering their original definition
    macros = extract_macros(main_content)

    # Expand includes while resolving paths with macros
    expanded_content = expand_includes(main_content, files, macros)

    return expanded_content

def get_main_file(tex_files):
    if tex_files.main_file in tex_files.files:
        return None
    for k in tex_files.files:
        if tex_files.main_file in k:
            tex_files.main_file = k
            return os.path.dirname(k)
    tex_files.main_file = None
    return None

@app.get("/version")
def read_version():
    version = get_version()
    return {"version": version}

@app.post("/merge")
async def merge_latex(tex_files: TexFiles):
    try:
        new_dirname = get_main_file(tex_files)
        if tex_files.main_file is None:
            raise HTTPException(
                status_code=404,
                detail=f"Main file {tex_files.main_file} not found."
            )

        old_keys = list(tex_files.files.keys())
        if new_dirname is not None:
            for k in old_keys:
                # if k == tex_files.main_file:
                #     continue
                new_k = k.replace(new_dirname + '/', '', 1)
                tex_files.files[new_k] = tex_files.files[k]

        # Get main file content
        if tex_files.main_file not in tex_files.files:
            for k in tex_files.files:
                if tex_files.main_file in k:
                    tex_files.main_file = k
                    break

        main_content = tex_files.files[tex_files.main_file]

        # # Save main file
        # merged_file_path = os.path.join(temp_dir, 'main.tex')
        # with open(merged_file_path, 'w', encoding='utf-8') as f:
        #     f.write(main_content)

        # Merge the files
        merged_content = merge_tex_files(main_content, tex_files.files)

        # # Save merged file
        # merged_file_path = os.path.join(temp_dir, 'merged.tex')
        # with open(merged_file_path, 'w', encoding='utf-8') as f:
        #     f.write(merged_content)

        return JSONResponse(content={"merged_content": merged_content})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Serve static files
app.mount("/", StaticFiles(directory="pages", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
