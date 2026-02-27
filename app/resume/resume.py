from pydantic import BaseModel
from typing import List, Optional

class Site(BaseModel):
    type: str
    id: str
    website: str
    url: str

class Skill(BaseModel):
    id: str
    type: str
    label: str
    text: str

class BulletPoint(BaseModel):
    label: str
    text: str

class Experience(BaseModel):
    id: str
    type: str
    title: str
    company: str
    dates: str
    summary: Optional[str] = ""
    bullets: List[BulletPoint]

class Education(BaseModel):
    degree: str
    detail: str

class InfoSite(BaseModel):
    type: str
    id: str
    website: str
    url: str

class Certification(BaseModel):
    id: str
    name: str
    issuer: str
    date: str

class ResumeSchema(BaseModel):
    pk: str
    sk: str
    entityType: str
    id: str
    name: str
    location: str
    phone: str
    email: str
    title: str
    professionalSummary: str
    sites: List[Site]
    skills: List[Skill]
    experience: List[Experience]
    education: List[Education]
    infoSites: List[InfoSite]
    certifications: List[Certification]

    class Config:
        # Allows the model to work if you pass it a dict with extra fields
        extra = "ignore"