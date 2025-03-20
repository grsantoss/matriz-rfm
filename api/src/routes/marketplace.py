# RFM Insights Marketplace API

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import os
import openai
import json
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib.units import inch

# Import response utilities
from backend.api_utils import success_response, error_response, paginated_response
from backend.schemas import ResponseSuccess, ResponseError, PaginatedResponseSuccess

from backend import models
from config import config
from backend.auth import get_current_user
from backend.database import get_db

router = APIRouter()

# Configure OpenAI API
openai.api_key = config.OPENAI_API_KEY

# PDF directory
PDF_DIR = "pdfs"
os.makedirs(PDF_DIR, exist_ok=True)

# Message generation endpoint
@router.post("/generate-message", response_model=ResponseSuccess[Dict[str, Any]], description="Generate marketing messages for RFM segments")
async def generate_message(
    data: dict,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Extract data from request
    message_type = data.get("messageType")
    company_name = data.get("companyName")
    company_website = data.get("companyWebsite")
    company_description = data.get("companyDescription")
    segment = data.get("rfmSegment")
    objective = data.get("objective")
    seasonality = data.get("seasonality")
    tone = data.get("tone")
    
    # Validate required fields
    if not all([message_type, company_name, company_description, segment, objective, tone]):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Campos obrigatórios não preenchidos")
    
    # Get character limit based on message type
    char_limit = config.MESSAGE_LIMITS.get(message_type, 500)
    
    # Get prompt template based on message type
    prompt_template = config.PROMPT_TEMPLATES.get(message_type)
    if not prompt_template:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tipo de mensagem inválido")
    
    # Number of messages to generate in sequence
    num_messages = 5
    messages_content = []
    message_ids = []
    
    try:
        for i in range(num_messages):
            # Format prompt with data and message number
            prompt = prompt_template.format(
                limit=char_limit,
                segment=segment,
                objective=objective,
                tone=tone,
                company=company_name
            )
            
            # Add message number context to prompt for sequence
            sequence_context = f"Esta é a mensagem {i+1} de uma sequência de {num_messages} mensagens. "
            if i == 0:
                sequence_context += "Esta é a primeira mensagem da sequência para iniciar o contato."
            elif i == num_messages - 1:
                sequence_context += "Esta é a última mensagem da sequência para finalizar o contato."
            else:
                sequence_context += f"Esta é a mensagem de acompanhamento número {i+1}."
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model=config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Você é um especialista em marketing que cria mensagens promocionais personalizadas para segmentos RFM."},
                    {"role": "user", "content": sequence_context + " " + prompt}
                ],
                max_tokens=char_limit,
                n=1,
                temperature=0.7,
            )
            
            # Extract message from response
            message_content = response.choices[0].message.content.strip()
            messages_content.append(message_content)
            
            # Create new message in database
            new_message = models.Message(
                user_id=current_user.id,
                message_type=message_type,
                company_name=company_name,
                company_website=company_website,
                company_description=company_description,
                segment=segment,
                objective=objective,
                seasonality=seasonality,
                tone=tone,
                message=message_content,
                regeneration_attempts=0,
                sequence_number=i+1,
                sequence_total=num_messages
            )
            
            db.add(new_message)
            db.commit()
            db.refresh(new_message)
            message_ids.append(new_message.id)
            
            # Generate PDF in background
            background_tasks.add_task(
                generate_pdf_for_message,
                new_message.id,
                message_content,
                company_name,
                message_type,
                db
            )
        
        # Return all messages and their IDs
        return {
            "messages": messages_content,
            "ids": message_ids,
            "primary_id": message_ids[0] if message_ids else None
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao gerar mensagem: {str(e)}")

# Regenerate message endpoint
@router.post("/regenerate-message")
async def regenerate_message(
    data: dict,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Extract data from request
    message_id = data.get("messageId")
    
    # Get original message
    original_message = db.query(models.Message).filter(models.Message.id == message_id).first()
    if not original_message:
        raise HTTPException(status_code=404, detail="Mensagem não encontrada")
    
    # Check if user owns the message
    if original_message.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acesso não autorizado")
    
    # Check regeneration attempts
    if original_message.regeneration_attempts >= config.MAX_REGENERATION_ATTEMPTS:
        raise HTTPException(status_code=400, detail="Limite de regenerações atingido")
    
    # Get character limit based on message type
    message_type = original_message.message_type
    char_limit = config.MESSAGE_LIMITS.get(message_type, 500)
    
    # Get prompt template based on message type
    prompt_template = config.PROMPT_TEMPLATES.get(message_type)
    if not prompt_template:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tipo de mensagem inválido")
    
    # Format prompt with data
    prompt = prompt_template.format(
        limit=char_limit,
        segment=original_message.segment,
        objective=original_message.objective,
        tone=original_message.tone,
        company=original_message.company_name
    )
    
    # Add sequence context to prompt
    sequence_context = f"Esta é a mensagem {original_message.sequence_number} de uma sequência de {original_message.sequence_total} mensagens. "
    if original_message.sequence_number == 1:
        sequence_context += "Esta é a primeira mensagem da sequência para iniciar o contato."
    elif original_message.sequence_number == original_message.sequence_total:
        sequence_context += "Esta é a última mensagem da sequência para finalizar o contato."
    else:
        sequence_context += f"Esta é a mensagem de acompanhamento número {original_message.sequence_number}."
    
    try:
        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model=config.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "Você é um especialista em marketing que cria mensagens promocionais personalizadas para segmentos RFM."},
                {"role": "user", "content": sequence_context + " " + prompt}
            ],
            max_tokens=char_limit,
            n=1,
            temperature=0.8,  # Slightly higher temperature for variation
        )
        
        # Extract message from response
        message_content = response.choices[0].message.content.strip()
        
        # Create new message in database as a regeneration
        new_message = models.Message(
            user_id=current_user.id,
            message_type=original_message.message_type,
            company_name=original_message.company_name,
            company_website=original_message.company_website,
            company_description=original_message.company_description,
            segment=original_message.segment,
            objective=original_message.objective,
            seasonality=original_message.seasonality,
            tone=original_message.tone,
            message=message_content,
            regeneration_attempts=original_message.regeneration_attempts + 1,
            parent_id=original_message.id,
            sequence_number=original_message.sequence_number,
            sequence_total=original_message.sequence_total
        )
        
        db.add(new_message)
        
        # Update original message's regeneration count
        original_message.regeneration_attempts += 1
        
        db.commit()
        db.refresh(new_message)
        
        # Generate PDF in background
        background_tasks.add_task(
            generate_pdf_for_message,
            new_message.id,
            message_content,
            original_message.company_name,
            original_message.message_type,
            db
        )
        
        return {"message": message_content, "id": new_message.id}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao regenerar mensagem: {str(e)}")

# Get message history endpoint
@router.get("/message-history")
async def get_message_history(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Calculate date threshold (7 days ago)
    threshold_date = datetime.utcnow() - timedelta(days=config.MESSAGE_HISTORY_DAYS)
    
    # Query messages
    messages = db.query(models.Message).filter(
        models.Message.user_id == current_user.id,
        models.Message.created_at >= threshold_date
    ).order_by(models.Message.created_at.desc()).all()
    
    # Convert to list of dictionaries
    result = []
    for msg in messages:
        result.append({
            "id": msg.id,
            "message_type": msg.message_type,
            "segment": msg.segment,
            "objective": msg.objective,
            "seasonality": msg.seasonality,
            "created_at": msg.created_at.isoformat(),
            "has_pdf": bool(msg.pdf_path)
        })
    
    return result

# Get specific message endpoint
@router.get("/message/{message_id}")
async def get_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Query message
    message = db.query(models.Message).filter(
        models.Message.id == message_id,
        models.Message.user_id == current_user.id
    ).first()
    
    if not message:
        raise HTTPException(status_code=404, detail="Mensagem não encontrada")
    
    return {
        "id": message.id,
        "message": message.message,
        "message_type": message.message_type,
        "company_name": message.company_name,
        "segment": message.segment,
        "objective": message.objective,
        "created_at": message.created_at.isoformat()
    }

# Download message as PDF endpoint
@router.get("/download-message/{message_id}")
async def download_message(
    message_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Query message
    message = db.query(models.Message).filter(
        models.Message.id == message_id,
        models.Message.user_id == current_user.id
    ).first()
    
    if not message:
        raise HTTPException(status_code=404, detail="Mensagem não encontrada")
    
    # Check if PDF exists, if not generate it
    if not message.pdf_path or not os.path.exists(message.pdf_path):
        pdf_path = generate_pdf_for_message(
            message.id,
            message.message,
            message.company_name,
            message.message_type,
            db
        )
    else:
        pdf_path = message.pdf_path
    
    # Return file
    return FileResponse(
        path=pdf_path,
        filename=f"mensagem-{message_id}.pdf",
        media_type="application/pdf"
    )

# Helper function to generate PDF
def generate_pdf_for_message(message_id, message_content, company_name, message_type, db):
    # Create PDF filename
    pdf_filename = f"{PDF_DIR}/message_{message_id}.pdf"
    
    # Create PDF
    doc = SimpleDocTemplate(pdf_filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Add title
    title_style = styles['Title']
    title = Paragraph(f"Mensagem de {message_type.upper()} - {company_name}", title_style)
    story.append(title)
    story.append(Spacer(1, 0.5 * inch))
    
    # Add date
    date_style = styles['Normal']
    date_text = Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", date_style)
    story.append(date_text)
    story.append(Spacer(1, 0.25 * inch))
    
    # Add message content
    content_style = styles['BodyText']
    content = Paragraph(message_content.replace('\n', '<br/>'), content_style)
    story.append(content)
    
    # Add footer
    story.append(Spacer(1, 1 * inch))
    footer_style = styles['Italic']
    footer = Paragraph("Gerado por RFM Insights", footer_style)
    story.append(footer)
    
    # Build PDF
    doc.build(story)
    
    # Update message in database with PDF path
    message = db.query(models.Message).filter(models.Message.id == message_id).first()
    if message:
        message.pdf_path = pdf_filename
        db.commit()
    
    return pdf_filename