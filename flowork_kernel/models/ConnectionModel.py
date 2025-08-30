#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\models\ConnectionModel.py
# JUMLAH BARIS : 21
#######################################################################

from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID, uuid4
class ConnectionModel(BaseModel):
    """
    Represents the data structure for a connection between two nodes.
    Uses an alias for 'from' as it is a reserved keyword in Python.
    """
    id: UUID = Field(default_factory=uuid4)
    from_node: UUID = Field(..., alias='from')
    to_node: UUID = Field(..., alias='to')
    source_port_name: Optional[str] = None
    class Config:
        allow_population_by_field_name = True # Memungkinkan kita mengisi 'from_node' menggunakan 'from'
