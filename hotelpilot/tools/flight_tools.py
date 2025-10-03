"""
Flight Signal Tools
===================
Tools for monitoring flight demand signals and computing lift indices.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, date, timedelta
import logging

logger = logging.getLogger(__name__)

def get_flight_arrivals(
    airport_code: str,
    date: str,
    time_band: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get flight arrival data for specific airport and date.

    Args:
        airport_code: IATA airport code (DCA, IAD, BWI)
        date: Date (YYYY-MM-DD)
        time_band: Optional time band (morning, midday, evening, late)

    Returns:
        Flight arrival statistics
    """
    logger.info(f"Fetching flight arrivals for {airport_code} on {date}")

    # Simulated flight data
    # In production, would connect to FlightAware, FlightRadar24, or FAA API

    time_bands = {
        "morning": {"start": "05:00", "end": "11:00", "flights": 12, "seats": 1850},
        "midday": {"start": "11:00", "end": "17:00", "flights": 18, "seats": 2700},
        "evening": {"start": "17:00", "end": "23:00", "flights": 22, "seats": 3400},
        "late": {"start": "23:00", "end": "02:00", "flights": 4, "seats": 550}
    }

    if time_band and time_band in time_bands:
        band_data = time_bands[time_band]
        return {
            "status": "success",
            "airport": airport_code,
            "date": date,
            "time_band": time_band,
            "flight_count": band_data["flights"],
            "total_seats": band_data["seats"],
            "aircraft_mix": {
                "narrow_body": 0.7,
                "regional": 0.25,
                "wide_body": 0.05
            },
            "confidence": 0.85
        }

    # Return all time bands if not specified
    total_flights = sum(band["flights"] for band in time_bands.values())
    total_seats = sum(band["seats"] for band in time_bands.values())

    return {
        "status": "success",
        "airport": airport_code,
        "date": date,
        "time_bands": time_bands,
        "total_flights": total_flights,
        "total_seats": total_seats,
        "year_over_year_change": 0.12,  # 12% increase YoY
        "confidence": 0.85
    }

def calculate_baseline_capacity(
    airport_code: str,
    date: str,
    lookback_weeks: int = 4
) -> Dict[str, Any]:
    """
    Calculate baseline capacity for comparison.

    Args:
        airport_code: IATA airport code
        date: Target date
        lookback_weeks: Weeks to look back for baseline

    Returns:
        Baseline capacity metrics
    """
    # Simulated baseline calculation
    # In production, would average historical data

    baseline_seats = {
        "DCA": 7500,
        "IAD": 12000,
        "BWI": 6000
    }

    baseline = baseline_seats.get(airport_code, 8000)

    return {
        "status": "success",
        "airport": airport_code,
        "date": date,
        "baseline_seats": baseline,
        "baseline_flights": 45,
        "lookback_weeks": lookback_weeks,
        "data_points": lookback_weeks * 7,
        "confidence": 0.90
    }

def compute_demand_lift_index(
    current_seats: int,
    baseline_seats: int,
    fare_pressure: Optional[float] = None,
    event_weight: float = 0.0
) -> Dict[str, Any]:
    """
    Compute demand lift index from flight signals.

    Args:
        current_seats: Current period seat capacity
        baseline_seats: Baseline seat capacity
        fare_pressure: Optional fare pressure indicator (0-1)
        event_weight: Event impact weight (0-1)

    Returns:
        Demand lift index and components
    """
    # Calculate seat capacity delta
    seat_capacity_delta = (current_seats - baseline_seats) / baseline_seats

    # Apply the PRD formula
    # demand_lift_index = 0.7 * seat_capacity_delta + 0.3 * fare_pressure_proxy + event_weight

    if fare_pressure is None:
        # Estimate fare pressure from capacity delta
        fare_pressure = min(max(seat_capacity_delta * 0.8, 0), 1)

    demand_lift_index = (0.7 * seat_capacity_delta +
                         0.3 * fare_pressure +
                         event_weight)

    # Normalize to 0-1 range
    demand_lift_index = min(max(demand_lift_index, 0), 1)

    # Determine confidence based on data quality
    confidence = 0.85
    if abs(seat_capacity_delta) < 0.05:
        confidence = 0.60  # Low confidence for small changes

    return {
        "status": "success",
        "demand_lift_index": round(demand_lift_index, 3),
        "seat_capacity_delta": round(seat_capacity_delta, 3),
        "fare_pressure": round(fare_pressure, 3),
        "event_weight": event_weight,
        "confidence": confidence,
        "components": {
            "seat_contribution": round(0.7 * seat_capacity_delta, 3),
            "fare_contribution": round(0.3 * fare_pressure, 3),
            "event_contribution": event_weight
        }
    }

def get_event_calendar(
    date_from: str,
    date_to: str,
    location: str = "Northern Virginia"
) -> Dict[str, Any]:
    """
    Get events that might impact demand.

    Args:
        date_from: Start date
        date_to: End date
        location: Geographic location

    Returns:
        Events and their weights
    """
    # Simulated event data
    # In production, would integrate with event APIs

    events = [
        {
            "date": "2024-03-29",
            "name": "Cherry Blossom Festival",
            "type": "festival",
            "weight": 0.3,
            "impact_radius_miles": 20
        },
        {
            "date": "2024-05-15",
            "name": "GMU Graduation",
            "type": "graduation",
            "weight": 0.2,
            "impact_radius_miles": 10
        },
        {
            "date": "2024-07-04",
            "name": "Independence Day",
            "type": "federal_holiday",
            "weight": 0.4,
            "impact_radius_miles": 50
        }
    ]

    # Filter events by date range
    filtered_events = [
        e for e in events
        if date_from <= e["date"] <= date_to
    ]

    return {
        "status": "success",
        "location": location,
        "date_from": date_from,
        "date_to": date_to,
        "events": filtered_events,
        "total_events": len(filtered_events),
        "max_weight": max((e["weight"] for e in filtered_events), default=0)
    }

def check_ops_disruption_risk(
    airport_code: str,
    date: str
) -> Dict[str, Any]:
    """
    Check for operational disruption risks.

    Args:
        airport_code: IATA airport code
        date: Date to check

    Returns:
        Disruption risk assessment
    """
    # Simulated disruption check
    # In production, would check weather, ATC delays, etc.

    import random

    risk_level = random.choice(["low", "medium", "high"])
    risk_score = {"low": 0.2, "medium": 0.5, "high": 0.8}[risk_level]

    factors = []
    if risk_level == "high":
        factors = ["weather", "atc_delays"]
    elif risk_level == "medium":
        factors = ["construction"]

    return {
        "status": "success",
        "airport": airport_code,
        "date": date,
        "risk_level": risk_level,
        "risk_score": risk_score,
        "factors": factors,
        "recommendation": "freeze_pricing" if risk_level == "high" else "proceed",
        "checked_at": datetime.now().isoformat()
    }

def aggregate_airport_signals(
    property_location: str,
    date: str
) -> Dict[str, Any]:
    """
    Aggregate signals from multiple airports based on property location.

    Args:
        property_location: Property location string
        date: Date for signals

    Returns:
        Aggregated demand signals
    """
    # Determine airport weights based on location
    if "Arlington" in property_location or "Alexandria" in property_location:
        weights = {"DCA": 0.6, "IAD": 0.3, "BWI": 0.1}
    elif "Reston" in property_location or "Tysons" in property_location:
        weights = {"IAD": 0.6, "DCA": 0.3, "BWI": 0.1}
    elif "Fairfax" in property_location:
        weights = {"IAD": 0.5, "DCA": 0.35, "BWI": 0.15}
    else:
        weights = {"DCA": 0.5, "IAD": 0.4, "BWI": 0.1}

    # Simulate getting data from each airport
    airport_data = {}
    for airport in weights.keys():
        arrivals = get_flight_arrivals(airport, date)
        baseline = calculate_baseline_capacity(airport, date)

        airport_data[airport] = {
            "current_seats": arrivals.get("total_seats", 8000),
            "baseline_seats": baseline["baseline_seats"],
            "weight": weights[airport]
        }

    # Calculate weighted average
    weighted_current = sum(data["current_seats"] * data["weight"]
                          for data in airport_data.values())
    weighted_baseline = sum(data["baseline_seats"] * data["weight"]
                           for data in airport_data.values())

    # Check for events
    events = get_event_calendar(date, date, property_location)
    event_weight = events["max_weight"]

    # Compute overall demand lift
    lift_result = compute_demand_lift_index(
        current_seats=int(weighted_current),
        baseline_seats=int(weighted_baseline),
        event_weight=event_weight
    )

    return {
        "status": "success",
        "property_location": property_location,
        "date": date,
        "airport_weights": weights,
        "airport_data": airport_data,
        "weighted_current_seats": int(weighted_current),
        "weighted_baseline_seats": int(weighted_baseline),
        "demand_lift_index": lift_result["demand_lift_index"],
        "confidence": lift_result["confidence"],
        "has_events": len(events["events"]) > 0,
        "recommendation": get_pricing_recommendation(lift_result["demand_lift_index"])
    }

def get_pricing_recommendation(demand_index: float) -> str:
    """Get pricing recommendation based on demand index."""
    if demand_index < 0.2:
        return "maintain_rates"
    elif 0.2 <= demand_index < 0.4:
        return "increase_5_8_percent"
    elif 0.4 <= demand_index < 0.7:
        return "increase_9_15_percent"
    else:
        return "increase_to_cap_with_approval"