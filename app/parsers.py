import pandas as pd
from typing import Dict, Any
from fastapi import UploadFile, HTTPException
from .schemas import BusinessProfile, KpiSnapshot, GrowthGoal, PlanRequest


def parse_csv_to_plan_request(file: UploadFile) -> PlanRequest:
    """
    Parse uploaded CSV and extract business KPIs.
    
    Expected CSV format:
    - Either a simple key-value format
    - Or a time-series with the latest row being used
    """
    try:
        # Read CSV
        df = pd.read_csv(file.file)
        
        # Strip whitespace from column names
        df.columns = df.columns.str.strip()
        
        # Check if it's time-series (has date column) or single-row
        if len(df) > 1 and any(col.lower() in ['date', 'period', 'month'] for col in df.columns):
            # Use most recent row
            row = df.iloc[-1]
        else:
            # Use first/only row
            row = df.iloc[0]
        
        # Extract business profile
        business_profile = BusinessProfile(
            business_id=str(row.get('business_id', 'csv_upload_001')),
            name=str(row.get('business_name', row.get('name', 'My Business'))),
            industry=str(row.get('industry', 'General')),
            region=str(row.get('region', 'Unknown')),
            main_channels=_parse_list_field(row.get('channels', 'email,website')),
            target_audience=str(row.get('target_audience', None)) if pd.notna(row.get('target_audience')) else None,
            tone_of_voice=str(row.get('tone', None)) if pd.notna(row.get('tone')) else None,
        )
        
        # Extract KPIs
        kpis = KpiSnapshot(
            period=str(row.get('period', 'last_30_days')),
            visits=int(row.get('visits', 0)),
            leads=int(row.get('leads', 0)),
            signups=int(row.get('signups', 0)),
            purchases=int(row.get('purchases', 0)),
            revenue=float(row.get('revenue', 0.0)),
            retention_rate=float(row.get('retention_rate', 0.0)) if pd.notna(row.get('retention_rate')) else None,
        )
        
        # Extract goal
        goal = GrowthGoal(
            objective=str(row.get('goal', row.get('objective', 'increase revenue'))),
            horizon_weeks=int(row.get('horizon_weeks', 8)),
            constraints=str(row.get('constraints', None)) if pd.notna(row.get('constraints')) else None,
        )
        
        return PlanRequest(
            business_profile=business_profile,
            kpis=kpis,
            goal=goal,
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to parse CSV: {str(e)}. Please check your CSV format.",
        )


def _parse_list_field(value: Any) -> list:
    """Parse comma-separated string into list"""
    if pd.isna(value):
        return []
    if isinstance(value, str):
        return [item.strip() for item in value.split(',')]
    return [str(value)]