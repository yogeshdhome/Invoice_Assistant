from pydantic import BaseModel, Field
from typing import List, Optional

class POInvoice(BaseModel):
    po_number: str = Field(..., description="Purchase Order Number")
    invoice_number: str = Field(..., description="Invoice Number")

class NonPOInvoice(BaseModel):
    acr_number: Optional[str] = Field(default=None, description="ACR Number")
    invoice_number: Optional[str] = Field(default=None, description="Invoice Number")
    invoice_document_date: str = Field(..., description="Invoice Document Date in YYYY-MM-DD format")

class UserQuery(BaseModel):
    po_invoices: List[POInvoice] = []
    non_po_invoices: List[NonPOInvoice] = []
    check_all_invoices_for_po: bool = False
