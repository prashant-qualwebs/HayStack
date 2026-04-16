from haystack.components.converters import PyPDFToDocument, DOCXToDocument
from app.haystack.pipelines.indexing_pipeline import indexing_pipeline
import tempfile
import os


async def ingest_file(content: bytes, filename: str, user_id: str) -> int:
    file_ext = filename.lower().split('.')[-1]
    
    if file_ext == 'pdf':
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        try:
            converter = PyPDFToDocument()
            result = converter.run(sources=[tmp_path])
            docs = result["documents"]
            
            for doc in docs:
                doc.meta["source"] = filename
                doc.meta["file_type"] = "pdf"
                doc.meta["user_id"] = user_id
        finally:
            os.unlink(tmp_path)
            
    elif file_ext == 'docx':
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx', mode='wb') as tmp_file:
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        try:
            converter = DOCXToDocument()
            result = converter.run(sources=[tmp_path])
            docs = result["documents"]
            
            for doc in docs:
                doc.meta["source"] = filename
                doc.meta["file_type"] = "docx"
                doc.meta["user_id"] = user_id
        finally:
            os.unlink(tmp_path)
    else:
        raise ValueError(f"Unsupported file type: {file_ext}")
    
    result = indexing_pipeline.run({"splitter": {"documents": docs}})
    return result["writer"]["documents_written"]
