import pytest
import io
from fastapi import UploadFile
from app.parsers import parse_csv_to_plan_request


def test_parse_basic_csv():
    """Test parsing a simple CSV file"""
    csv_content = """business_id,business_name,industry,region,channels,visits,leads,signups,purchases,revenue,goal,horizon_weeks
test_001,Test Cafe,Food & Beverage,Toronto,email,1000,200,150,100,10000,increase sales,6"""
    
    file = UploadFile(
        filename="test.csv",
        file=io.BytesIO(csv_content.encode())
    )
    
    request = parse_csv_to_plan_request(file)
    
    assert request.business_profile.business_id == "test_001"
    assert request.business_profile.name == "Test Cafe"
    assert request.kpis.visits == 1000
    assert request.kpis.leads == 200
    assert request.goal.objective == "increase sales"
    assert request.goal.horizon_weeks == 6


def test_parse_csv_with_comma_separated_channels():
    """Test parsing comma-separated channel list"""
    csv_content = """business_name,channels,visits,leads,signups,purchases,revenue,goal
Cafe,"email,social,in-store",2000,400,300,200,20000,grow"""
    
    file = UploadFile(
        filename="test.csv",
        file=io.BytesIO(csv_content.encode())
    )
    
    request = parse_csv_to_plan_request(file)
    
    assert len(request.business_profile.main_channels) == 3
    assert "email" in request.business_profile.main_channels
    assert "social" in request.business_profile.main_channels


def test_parse_csv_missing_optional_fields():
    """Test CSV with only required fields works"""
    csv_content = """business_name,industry,region,visits,leads,signups,purchases,revenue,goal
Simple Store,Retail,NYC,1000,500,400,300,30000,increase revenue"""
    
    file = UploadFile(
        filename="test.csv",
        file=io.BytesIO(csv_content.encode())
    )
    
    request = parse_csv_to_plan_request(file)
    
    assert request.business_profile.name == "Simple Store"
    assert request.kpis.visits == 1000
    # Optional fields should have defaults
    assert request.business_profile.target_audience is None


def test_parse_csv_handles_zeros():
    """Test CSV with zero values doesn't crash"""
    csv_content = """business_name,industry,region,visits,leads,signups,purchases,revenue,goal
Zero Test,Tech,Boston,0,0,0,0,0,test goal"""
    
    file = UploadFile(
        filename="test.csv",
        file=io.BytesIO(csv_content.encode())
    )
    
    request = parse_csv_to_plan_request(file)
    
    assert request.kpis.visits == 0
    assert request.kpis.revenue == 0.0
    # Should not crash