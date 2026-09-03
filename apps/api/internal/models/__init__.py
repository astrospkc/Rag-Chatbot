from internal.models.doc_model import UploadedDocument
from internal.models.doc_vector_model import DocumentVector
from internal.core.db import Base


__all__ = [
    "Base",
    "UploadedDocument",
    "DocumentVector",
    ]



#     rom internal.core.db import Base
# from internal.models.doc_model import UploadedDocument
# from internal.models.user_model import User          # <-- Example new model
# from internal.models.chunk_model import DocumentChunk # <-- Example new model
# __all__ = [
#     "Base",
#     "UploadedDocument",
#     "User",
#     "DocumentChunk",
# ]