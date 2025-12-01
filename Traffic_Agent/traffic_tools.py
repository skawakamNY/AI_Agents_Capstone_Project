from tomtom_client import TomTomTrafficClient
from config import TOMTOM_API_KEY

tomtom_client = TomTomTrafficClient(api_key=TOMTOM_API_KEY)

def tool_get_traffic_flow(lat: float, lon: float):
    data = tomtom_client.get_traffic_flow(lat, lon)
    speed = data.get("flowSegmentData", {}).get("currentSpeed", "unknown")
    free_flow = data.get("flowSegmentData", {}).get("freeFlowSpeed", "unknown")
    return {
        "current_speed": speed,
        "free_flow_speed": free_flow,
        "lat": lat,
        "lon": lon
    }

def tool_get_incidents(bbox):
    data = tomtom_client.get_incidents(bbox)
    return data.get("incidents", [])

def tool_get_eta(origin, destination):
    data = tomtom_client.get_eta(origin, destination)
    route = data.get("routes", [{}])[0]
    summary = route.get("summary", {})
    return {
        "travel_time_seconds": summary.get("travelTimeInSeconds"),
        "traffic_delay_seconds": summary.get("trafficDelayInSeconds"),
        "length_meters": summary.get("lengthInMeters")
    }