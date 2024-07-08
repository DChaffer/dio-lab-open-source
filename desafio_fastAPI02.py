###### database.py ######
from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient('mongodb://localhost:27017')
database = client.store_db
product_collection = database.get_collection("products")

###### models.py ######
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

class Product(BaseModel):
    id: Optional[str] = None
    name: str
    quantity: int
    price: float
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

###### schemas.py ######
from pydantic import BaseModel
from typing import Optional

class ProductCreate(BaseModel):
    name: str
    quantity: int
    price: float
    status: str

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    quantity: Optional[int] = None
    price: Optional[float] = None
    status: Optional[str] = None

###### crud.py ######
from .database import product_collection
from .models import Product
from .schemas import ProductCreate, ProductUpdate
from bson import ObjectId
from datetime import datetime

class CRUDProduct:
    @staticmethod
    async def create(product: ProductCreate):
        product_data = product.dict()
        product_data["created_at"] = datetime.utcnow()
        product_data["updated_at"] = datetime.utcnow()
        result = await product_collection.insert_one(product_data)
        if result.inserted_id:
            return await CRUDProduct.get(result.inserted_id)
        else:
            raise Exception("Erro ao inserir o produto")

    @staticmethod
    async def get(product_id: str):
        product = await product_collection.find_one({"_id": ObjectId(product_id)})
        if product:
            return Product(**product)

    @staticmethod
    async def update(product_id: str, product: ProductUpdate):
        update_data = {k: v for k, v in product.dict().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        result = await product_collection.update_one(
            {"_id": ObjectId(product_id)}, {"$set": update_data}
        )
        if result.modified_count == 1:
            return await CRUDProduct.get(product_id)
        else:
            raise Exception("Produto não encontrado")

    @staticmethod
    async def filter_by_price(min_price: float, max_price: float):
        products = await product_collection.find(
            {"price": {"$gt": min_price, "$lt": max_price}}
        ).to_list(100)
        return [Product(**product) for product in products]

    @staticmethod
    async def delete(product_id: str):
        result = await product_collection.delete_one({"_id": ObjectId(product_id)})
        if result.deleted_count == 1:
            return True
        return False

###### main.py ######
from fastapi import FastAPI, HTTPException
from .schemas import ProductCreate, ProductUpdate
from .crud import CRUDProduct
from .models import Product

app = FastAPI()

@app.post("/products/", response_model=Product)
async def create_product(product: ProductCreate):
    try:
        return await CRUDProduct.create(product)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.patch("/products/{product_id}", response_model=Product)
async def update_product(product_id: str, product: ProductUpdate):
    try:
        return await CRUDProduct.update(product_id, product)
    except Exception as e:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

@app.get("/products/filter/", response_model=list[Product])
async def filter_products(min_price: float, max_price: float):
    return await CRUDProduct.filter_by_price(min_price, max_price)

###### tests/test_crud.py ######
import pytest
from ..crud import CRUDProduct
from ..schemas import ProductCreate, ProductUpdate

@pytest.mark.asyncio
async def test_create_product():
    product = ProductCreate(name="Product1", quantity=10, price=1000, status="Available")
    created_product = await CRUDProduct.create(product)
    assert created_product.name == "Product1"

@pytest.mark.asyncio
async def test_update_product():
    product = ProductCreate(name="Product2", quantity=5, price=5000, status="Available")
    created_product = await CRUDProduct.create(product)
    update_data = ProductUpdate(price=6000)
    updated_product = await CRUDProduct.update(created_product.id, update_data)
    assert updated_product.price == 6000

@pytest.mark.asyncio
async def test_filter_products():
    await CRUDProduct.create(ProductCreate(name="Product3", quantity=7, price=7000, status="Available"))
    products = await CRUDProduct.filter_by_price(5000, 8000)
    assert len(products) > 0

###### tests/test_schemas.py ######
from pydantic import ValidationError
from ..schemas import ProductCreate

def test_product_create():
    product = ProductCreate(name="Test", quantity=5, price=100, status="Available")
    assert product.name == "Test"

def test_product_create_invalid():
    with pytest.raises(ValidationError):
        ProductCreate(name="Test", quantity=-5, price=-100, status="Available")

###### tests/test_controllers.py ######
from fastapi.testclient import TestClient
from ..main import app

client = TestClient(app)

def test_create_product():
    response = client.post("/products/", json={"name": "Test Product", "quantity": 10, "price": 1000, "status": "Available"})
    assert response.status_code == 200
    assert response.json()["name"] == "Test Product"

def test_update_product():
    create_response = client.post("/products/", json={"name": "Product4", "quantity": 8, "price": 4000, "status": "Available"})
    product_id = create_response.json()["id"]
    response = client.patch(f"/products/{product_id}", json={"price": 4500})
    assert response.status_code == 200
    assert response.json()["price"] == 4500

def test_filter_products():
    response = client.get("/products/filter/?min_price=5000&max_price=8000")
    assert response.status_code == 200
    assert len(response.json()) > 0
