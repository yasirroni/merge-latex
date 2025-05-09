"""FastAPI server for LaTeX merging service.

This module provides a REST API for merging multiple LaTeX files into
a single consolidated document.
"""
import json
import os
from typing import Dict

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Import core functionality from src module
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.merge_latex.core import merge_tex_files


class TexFiles(BaseModel):
    """Model for LaTeX files data received from the client."""
    main_file: str
    files: Dict[str, str]
    main_dir: str = ''


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
    """Get the current version from package.json."""
    with open(os.path.join(os.path.dirname(__file__), '../package.json')) as f:
        package_json = json.load(f)
        return package_json.get('version', '0.0.0')


def get_main_file(tex_files: TexFiles) -> str:
    """Find the main file directory path.
    
    Parameters
    ----------
    tex_files : TexFiles
        The TexFiles object containing main_file and files
        
    Returns
    -------
    str
        Directory path of the main file
        
    Raises
    ------
    HTTPException
        If the main file is not found
    """
    if tex_files.main_file in tex_files.files:
        return os.path.dirname(tex_files.main_file)
    
    for k in tex_files.files:
        if tex_files.main_file in k:
            tex_files.main_file = k
            return os.path.dirname(k)

    raise HTTPException(
        status_code=404,
        detail=f"Main file {tex_files.main_file} not found."
    )


@app.get("/version")
def read_version():
    """Endpoint to get the current version."""
    version = get_version()
    return {"version": version}


@app.post("/merge")
async def merge_latex(tex_files: TexFiles):
    """Endpoint to merge LaTeX files.
    
    Parameters
    ----------
    tex_files : TexFiles
        Model containing main_file path and a dictionary of all files
        
    Returns
    -------
    JSONResponse
        JSON response containing the merged content
        
    Raises
    ------
    HTTPException
        If an error occurs during merging
    """
    try:
        tex_files.main_dir = get_main_file(tex_files)

        # Update keys based on new_dirname
        old_keys = list(tex_files.files.keys())
        for k in old_keys:
            new_k = k.replace(tex_files.main_dir + '/', '', 1)
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
        merged_content = merge_tex_files(main_content, tex_files.files, tex_files.main_dir)

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
