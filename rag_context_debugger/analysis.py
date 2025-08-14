from typing import Dict, Any, List, TypedDict, Optional
from datetime import datetime

# Library imports
from tecton.framework.data_frame import FeatureVector

# Using TypedDict for well-defined, type-checked dictionary structures.
# This makes the data flow between modules much safer and easier to reason about.

class SloReport(TypedDict):
    is_eligible: bool
    server_time_seconds: Optional[float]
    dynamodb_time_seconds: Optional[float]

class TemporalReport(TypedDict):
    min_effective_time: str
    max_effective_time: str
    time_spread_seconds: float
    risk_level: str
    feature_timestamps: Dict[str, Optional[str]]

class AnalysisResult(TypedDict):
    features: Dict[str, Any]
    slo_report: Optional[SloReport]
    temporal_report: Optional[TemporalReport]
    raw_metadata: Dict[str, Any]
    error: Optional[str]

def analyze_feature_vector(fv_object: FeatureVector) -> AnalysisResult:
    """
    Takes a Tecton FeatureVector object and returns a structured dictionary of analysis results.
    This function is the heart of the debugger's logic.

    Args:
        fv_object: The FeatureVector object returned by the Tecton SDK.

    Returns:
        An AnalysisResult dictionary containing the full diagnosis.
    """
    # 1. Extract Feature Values
    features_dict: Dict[str, Any] = fv_object.to_dict()  # type: ignore

    # 2. Analyze SLO Information
    slo_info: Optional[Dict[str, str]] = fv_object.slo_info
    slo_report: Optional[SloReport] = None
    if slo_info:
        slo_report = {
            "is_eligible": slo_info.get("slo_eligible", "false").lower() == "true",
            "server_time_seconds": float(slo_info.get("slo_server_time_seconds", 0)) if slo_info.get("slo_server_time_seconds") else None,
            "dynamodb_time_seconds": float(slo_info.get("slo_store_response_time_seconds", 0)) if slo_info.get("slo_store_response_time_seconds") else None
        }

    # 3. Perform Temporal Cohesion Analysis
    # Use return_effective_times parameter for to_dict
    raw_metadata_dict = fv_object.to_dict(return_effective_times=True)  # type: ignore
    
    # Type assertion for the metadata dictionary
    raw_metadata: Dict[str, Any] = {}
    if '__metadata__' in raw_metadata_dict:
        metadata_value = raw_metadata_dict['__metadata__']  # type: ignore
        if isinstance(metadata_value, dict):
            raw_metadata = metadata_value  # type: ignore
    
    # Type assertion for effective times
    effective_times: Dict[str, Optional[str]] = {}
    if 'effective_times' in raw_metadata:
        effective_times_value = raw_metadata['effective_times']  # type: ignore
        if isinstance(effective_times_value, dict):
            effective_times = effective_times_value  # type: ignore
    
    timestamps: List[datetime] = []
    for t in effective_times.values():
        if t:
            try:
                timestamps.append(datetime.fromisoformat(t.replace("Z", "+00:00")))
            except ValueError:
                continue
    
    temporal_report: Optional[TemporalReport] = None
    if len(timestamps) > 1:
        min_time = min(timestamps)
        max_time = max(timestamps)
        spread_seconds = (max_time - min_time).total_seconds()
        
        # Heuristic-based risk assessment. This is a simple but effective starting point.
        risk_level = "LOW"
        if spread_seconds > 3600:  # > 1 hour
            risk_level = "HIGH"
        elif spread_seconds > 60:  # > 1 minute
            risk_level = "MEDIUM"

        temporal_report = {
            "min_effective_time": min_time.isoformat(),
            "max_effective_time": max_time.isoformat(),
            "time_spread_seconds": spread_seconds,
            "risk_level": risk_level,
            "feature_timestamps": effective_times
        }
    
    # 4. Assemble the final, comprehensive report
    analysis_result: AnalysisResult = {
        "features": features_dict,
        "slo_report": slo_report,
        "temporal_report": temporal_report,
        "raw_metadata": raw_metadata,
        "error": None
    }
    return analysis_result