"""File processing utilities for RFM analysis."""

import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple, List
import os
from datetime import datetime
import json
from sqlalchemy.orm import Session

from ..models import RFMAnalysis, CustomerRecord

class FileProcessor:
    def __init__(self, upload_dir: str):
        """Initialize the file processor.
        
        Args:
            upload_dir: Directory for storing uploaded files
        """
        self.upload_dir = upload_dir
        os.makedirs(upload_dir, exist_ok=True)

    def process_upload(self, file, analysis_id: str) -> Tuple[str, str]:
        """Process uploaded file and save it.
        
        Args:
            file: Uploaded file object
            analysis_id: ID of the analysis
            
        Returns:
            Tuple of (original_file_path, processed_file_path)
        """
        # Create directory for this analysis
        analysis_dir = os.path.join(self.upload_dir, analysis_id)
        os.makedirs(analysis_dir, exist_ok=True)

        # Save original file
        original_filename = file.filename
        original_path = os.path.join(analysis_dir, f"original_{original_filename}")
        with open(original_path, "wb") as f:
            f.write(file.read())

        # Path for processed file
        processed_path = os.path.join(analysis_dir, f"processed_{original_filename}")
        
        return original_path, processed_path

    def analyze_and_save(
        self,
        db: Session,
        analysis: RFMAnalysis,
        df: pd.DataFrame,
        column_mapping: Dict[str, str]
    ) -> None:
        """Perform RFM analysis and save results.
        
        Args:
            db: Database session
            analysis: RFMAnalysis instance
            df: DataFrame with customer data
            column_mapping: Mapping of DataFrame columns to RFM fields
        """
        # Calculate RFM scores
        recency_col = column_mapping['recency']
        frequency_col = column_mapping['frequency']
        monetary_col = column_mapping['monetary']
        customer_id_col = column_mapping['customer_id']

        # Calculate quintiles for scoring
        r_labels = range(1, 6)
        # Note: For recency, lower values are better (more recent)
        r_quintiles = pd.qcut(df[recency_col], q=5, labels=list(reversed(r_labels)))
        f_quintiles = pd.qcut(df[frequency_col], q=5, labels=r_labels)
        m_quintiles = pd.qcut(df[monetary_col], q=5, labels=r_labels)

        # Create customer records
        for idx, row in df.iterrows():
            customer_record = CustomerRecord(
                analysis_id=analysis.id,
                customer_id=str(row[customer_id_col]),
                recency_value=float(row[recency_col]),
                frequency_value=int(row[frequency_col]),
                monetary_value=float(row[monetary_col]),
                recency_score=int(r_quintiles[idx]),
                frequency_score=int(f_quintiles[idx]),
                monetary_score=int(m_quintiles[idx]),
                rfm_score=int(r_quintiles[idx] + f_quintiles[idx] + m_quintiles[idx]),
                segment=self._get_segment(
                    int(r_quintiles[idx]),
                    int(f_quintiles[idx]),
                    int(m_quintiles[idx])
                ),
                original_data=row.to_dict()
            )
            db.add(customer_record)

        # Save processed file with results
        results_df = df.copy()
        results_df['recency_score'] = r_quintiles
        results_df['frequency_score'] = f_quintiles
        results_df['monetary_score'] = m_quintiles
        results_df['rfm_score'] = results_df['recency_score'] + results_df['frequency_score'] + results_df['monetary_score']
        results_df['segment'] = results_df.apply(
            lambda x: self._get_segment(
                int(x['recency_score']),
                int(x['frequency_score']),
                int(x['monetary_score'])
            ),
            axis=1
        )

        # Save to processed file path
        results_df.to_excel(analysis.processed_file_path, index=False)

    def _get_segment(self, r_score: int, f_score: int, m_score: int) -> str:
        """Determine customer segment based on RFM scores.
        
        Segmentation rules:
        - Champions: Recent customers who buy often and spend the most
        - Loyal Customers: Buy regularly and spend significantly
        - Potential Loyalists: Recent customers with average frequency
        - New Customers: Bought recently but not frequently
        - Promising: Recent customers with low frequency but good monetary value
        - Need Attention: Above average recency and frequency but low monetary value
        - At Risk: Below average recency but good frequency/monetary
        - Cant Lose: Made big purchases but haven't bought recently
        - Hibernating: Low scores in all categories but not lost
        - Lost: Lowest scores across all metrics
        """
        # Calculate average scores
        avg_score = (r_score + f_score + m_score) / 3

        # Champions
        if r_score >= 4 and f_score >= 4 and m_score >= 4:
            return "Champions"
        
        # Loyal Customers
        elif f_score >= 4 and m_score >= 4:
            return "Loyal Customers"
        
        # Potential Loyalists
        elif r_score >= 4 and f_score >= 3:
            return "Potential Loyal Customers"
        
        # New Customers
        elif r_score >= 4 and f_score <= 2:
            return "New Customers"
        
        # Promising
        elif r_score >= 4 and m_score >= 3:
            return "Promising Customers"
        
        # Need Attention
        elif r_score >= 3 and f_score >= 3 and m_score <= 2:
            return "Customers Who Need Attention"
        
        # At Risk
        elif r_score <= 2 and (f_score >= 3 or m_score >= 3):
            return "Customers at Risk"
        
        # Can't Lose
        elif r_score <= 2 and m_score >= 4:
            return "Customers I Can't Lose"
        
        # Hibernating
        elif r_score <= 2 and avg_score >= 2:
            return "Hibernating Customers"
        
        # Lost
        else:
            return "Lost Customers"

    def get_analysis_summary(self, db: Session, analysis_id: str) -> Dict[str, Any]:
        """Generate summary of analysis results.
        
        Args:
            db: Database session
            analysis_id: ID of the analysis
            
        Returns:
            Dictionary with analysis summary
        """
        records = db.query(CustomerRecord).filter(
            CustomerRecord.analysis_id == analysis_id
        ).all()

        segments = {}
        for record in records:
            if record.segment not in segments:
                segments[record.segment] = 0
            segments[record.segment] += 1

        return {
            "total_customers": len(records),
            "segment_distribution": segments,
            "average_scores": {
                "recency": sum(r.recency_score for r in records) / len(records),
                "frequency": sum(r.frequency_score for r in records) / len(records),
                "monetary": sum(r.monetary_score for r in records) / len(records),
            }
        } 