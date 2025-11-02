from fastapi import APIRouter, HTTPException
from database import db

router = APIRouter(prefix="/parks", tags=["Parks"])

collection = db.collection("parques")

@router.get("/helloWorld")
async def default():
    return {"_id": str("Hello World Park")}

@router.get("/")
async def get_all_parks():
    docs = collection.stream()
    print("TESte, ", docs)
    return [{"id": doc.id, **doc.to_dict()} for doc in docs]

@router.get("/{park_id}")
async def get_park(park_id: str):
    print("TESTE",)
    doc = collection.document(park_id).get()
    return {"id": doc.id, **doc.to_dict()}

@router.post("reserva/{park_id}")
async def reserva_lugar(park_id: str):
    print("Reserva = ", park_id)
    return {"status": "OK"}

@router.post("/atualizaLugar/{park_id}")
async def atualiza_lugar(park_id: str):
    # Reference to the document
    doc_ref = db.collection("parques").document(park_id)
    
    # Check if the park exists
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Park not found")

    # Update the estado to "ocupado"
    doc_ref.update({
        "estado": "ocupado"
    })

    print(f"Parque {park_id} atualizado para 'ocupado'")
    return {"status": "OK", "park_id": park_id, "estado": "ocupado"}