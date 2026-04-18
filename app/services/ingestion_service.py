from haystack import Document
from haystack.components.converters import PyPDFToDocument, DOCXToDocument
from typing import List
from fastapi import UploadFile
import tempfile
import os
from app.haystack.pipelines.indexing_pipeline import indexing_pipeline


async def ingest_files(files: List[UploadFile], user_id: str, document_id: str) -> int:
    documents = []
    
    for file in files:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.filename.split('.')[-1]}") as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            # Convert file to Haystack documents based on type
            file_ext = file.filename.lower().split(".")[-1]
            
            if file_ext == "pdf":
                converter = PyPDFToDocument()
                result = converter.run(sources=[tmp_file_path])
                converted_docs = result["documents"]
            elif file_ext in ["docx", "doc"]:
                converter = DOCXToDocument()
                result = converter.run(sources=[tmp_file_path])
                converted_docs = result["documents"]
            else:
                continue
            
            # Add metadata to each document
            for doc in converted_docs:
                doc.meta.update({
                    "user_id": user_id,
                    "document_id": document_id,
                    "filename": file.filename,
                    "source": "api"
                })
                documents.append(doc)
        
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
    
    if not documents:
        return 0
    
    result = indexing_pipeline.run({"splitter": {"documents": documents}})
    return result["writer"]["documents_written"]
