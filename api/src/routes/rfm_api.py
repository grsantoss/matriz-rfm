# RFM Insights - API Module

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from fastapi.responses import JSONResponse
import pandas as pd
import io
import json
import datetime
import os
from typing import Optional, List, Dict, Any

# Import response utilities
from .api_utils import success_response, error_response, paginated_response
from .schemas import ResponseSuccess, ResponseError, PaginatedResponseSuccess

# Import RFM Analysis module
from .rfm_analysis import analyze_rfm_data

# Create router
router = APIRouter()

# Directory to store analysis history
HISTORY_DIR = "analysis_history"
os.makedirs(HISTORY_DIR, exist_ok=True)

@router.post("/analyze-rfm", response_model=ResponseSuccess[Dict[str, Any]], description="Analyze RFM data from uploaded CSV file and generate customer segments")
async def analyze_rfm(
    file: UploadFile = File(...),
    segment_type: str = Form(...),
    user_id_col: str = Form(...),
    recency_col: str = Form(...),
    frequency_col: str = Form(...),
    monetary_col: str = Form(...)
):
    """
    Analyze RFM data from uploaded CSV file
    """
    try:
        # Read CSV file
        contents = await file.read()
        data = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Validate required columns
        required_cols = [user_id_col, recency_col, frequency_col, monetary_col]
        missing_cols = [col for col in required_cols if col not in data.columns]
        
        if missing_cols:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required columns: {', '.join(missing_cols)}"
            )
        
        # Perform RFM analysis
        results = analyze_rfm_data(
            data=data,
            user_id_col=user_id_col,
            recency_col=recency_col,
            frequency_col=frequency_col,
            monetary_col=monetary_col,
            segment_type=segment_type
        )
        
        # Save analysis to history
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        
        history_entry = {
            "filename": file.filename,
            "timestamp": datetime.datetime.now().isoformat(),
            "segment_type": segment_type,
            "record_count": len(data),
            "column_mapping": {
                "user_id": user_id_col,
                "recency": recency_col,
                "frequency": frequency_col,
                "monetary": monetary_col
            },
            "summary": {
                "segment_counts": results["rfm_analysis"]["segment_counts"],
                "total_customers": sum(results["rfm_analysis"]["segment_counts"].values())
            }
        }
        
        # Save history entry
        with open(os.path.join(HISTORY_DIR, f"{timestamp}_meta.json"), "w") as f:
            json.dump(history_entry, f)
        
        # Add history entry to results
        results["history_entry"] = history_entry
        
        return success_response(
            data=results,
            message="RFM analysis completed successfully"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}"
        )

@router.get("/analysis-history", response_model=ResponseSuccess[Dict[str, List[Dict[str, Any]]]], description="Get analysis history with optional limit parameter")
async def get_analysis_history(limit: int = 5):
    """
    Get analysis history (limited to the most recent entries)
    """
    try:
        history_files = [f for f in os.listdir(HISTORY_DIR) if f.endswith("_meta.json")]
        history_files.sort(reverse=True)  # Sort by timestamp (newest first)
        
        history = []
        for i, file in enumerate(history_files):
            if i >= limit:
                break
                
            with open(os.path.join(HISTORY_DIR, file), "r") as f:
                history_entry = json.load(f)
                history.append(history_entry)
        
        return success_response(
            data={"history": history},
            message=f"Retrieved {len(history)} analysis history records"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving analysis history: {str(e)}"
        )

@router.get("/segment-descriptions", response_model=ResponseSuccess[Dict[str, Dict[str, str]]], description="Get descriptions for RFM segments")
async def get_segment_descriptions():
    """
    Get descriptions for RFM segments
    """
    segment_descriptions = {
        "Campeões": "Clientes que compraram recentemente, compram com frequência e gastam muito. Eles são seus melhores clientes.",
        "Clientes Fiéis": "Clientes que compram regularmente. Respondem bem a programas de fidelidade.",
        "Fiéis em Potencial": "Clientes recentes que gastam um bom valor. Podem ser convertidos em clientes fiéis com atenção adequada.",
        "Novos Clientes": "Clientes que compraram recentemente, mas não compraram com frequência.",
        "Clientes Promissores": "Clientes recentes que gastam um bom valor, mas não compram com frequência.",
        "Clientes que Precisam de Atenção": "Clientes médios em termos de recência, frequência e valor monetário.",
        "Clientes Quase Dormentes": "Clientes que não compram há algum tempo, mas têm frequência e valor médios.",
        "Clientes que Não Posso Perder": "Clientes que não compram há algum tempo, mas têm alta frequência e valor.",
        "Clientes em Risco": "Clientes que não compram há algum tempo e têm frequência média.",
        "Clientes Hibernando": "Clientes que não compram há muito tempo, têm baixa frequência e baixo valor.",
        "Clientes Perdidos": "Clientes que não compram há muito tempo e têm baixa frequência."
    }
    
    return success_response(
        data={"segment_descriptions": segment_descriptions},
        message="Segment descriptions retrieved successfully"
    )

@router.get("/segment-recommendations", response_model=ResponseSuccess[Dict[str, Dict[str, List[str]]]], description="Get marketing recommendations for each RFM segment")
async def get_segment_recommendations():
    """
    Get marketing recommendations for each RFM segment
    """
    segment_recommendations = {
        "Campeões": [
            "Recompense com programas de fidelidade exclusivos",
            "Peça feedback e avaliações de produtos",
            "Ofereça acesso antecipado a novos produtos",
            "Transforme-os em embaixadores da marca"
        ],
        "Clientes Fiéis": [
            "Ofereça programas de fidelidade e recompensas",
            "Comunique-se regularmente com ofertas personalizadas",
            "Incentive compras recorrentes com assinaturas",
            "Solicite indicações e ofereça benefícios"
        ],
        "Fiéis em Potencial": [
            "Ofereça incentivos para aumentar a frequência de compra",
            "Envie comunicações personalizadas baseadas em interesses",
            "Crie programas de fidelidade para incentivar compras regulares",
            "Ofereça descontos em produtos complementares"
        ],
        "Novos Clientes": [
            "Envie emails de boas-vindas com ofertas especiais",
            "Eduque sobre os benefícios dos seus produtos/serviços",
            "Ofereça suporte proativo para garantir satisfação",
            "Incentive a segunda compra com descontos"
        ],
        "Clientes Promissores": [
            "Ofereça produtos complementares aos já adquiridos",
            "Crie ofertas personalizadas baseadas nas compras anteriores",
            "Incentive compras mais frequentes com programas de pontos",
            "Envie lembretes de recompra para produtos consumíveis"
        ],
        "Clientes que Precisam de Atenção": [
            "Reative o engajamento com ofertas especiais",
            "Solicite feedback para entender necessidades",
            "Ofereça descontos em produtos populares",
            "Crie campanhas educativas sobre novos produtos"
        ],
        "Clientes Quase Dormentes": [
            "Envie campanhas de reativação com ofertas atrativas",
            "Ofereça descontos significativos para incentivar o retorno",
            "Solicite feedback sobre a experiência anterior",
            "Apresente novos produtos ou melhorias nos serviços"
        ],
        "Clientes que Não Posso Perder": [
            "Crie ofertas personalizadas baseadas no histórico de compras",
            "Ofereça atendimento VIP para reconquistar",
            "Envie comunicações exclusivas com benefícios especiais",
            "Solicite feedback e resolva possíveis problemas"
        ],
        "Clientes em Risco": [
            "Envie campanhas de reativação urgentes",
            "Ofereça descontos significativos para incentivar o retorno",
            "Crie programas de fidelidade para incentivar compras regulares",
            "Solicite feedback para entender razões de afastamento"
        ],
        "Clientes Hibernando": [
            "Envie campanhas de 'sentimos sua falta'",
            "Ofereça descontos agressivos para primeira recompra",
            "Apresente novos produtos ou serviços",
            "Solicite feedback sobre motivos de abandono"
        ],
        "Clientes Perdidos": [
            "Envie campanhas de reconquista com ofertas irrecusáveis",
            "Apresente mudanças e melhorias nos produtos/serviços",
            "Ofereça benefícios exclusivos para retorno",
            "Considere segmentar para campanhas específicas de reativação"
        ]
    }
    
    return success_response(
        data={"segment_recommendations": segment_recommendations},
        message="Segment recommendations retrieved successfully"
    )