"""
════════════════════════════════════════════════════════════════════
🔍 SMARTSPORTS - Production Monitoring System
Real-time monitoring for errors, performance, and stability
════════════════════════════════════════════════════════════════════
"""

import time
import logging
import traceback
from datetime import datetime, date
from typing import Dict, Optional, Callable
from pathlib import Path
from dataclasses import dataclass, asdict
import json
from collections import defaultdict

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ErrorRecord:
    """Record of a system error"""
    timestamp: str
    endpoint: str
    error_type: str
    error_message: str
    stack_trace: str
    user_id: Optional[str] = None
    request_id: Optional[str] = None


@dataclass
class PerformanceRecord:
    """Record of endpoint performance"""
    timestamp: str
    endpoint: str
    method: str
    status_code: int
    response_time_ms: float
    user_id: Optional[str] = None


class MonitoringSystem:
    """
    🔍 Production Monitoring System

    Tracks:
    - ❌ Errors and exceptions
    - ⚡ Response times and latency
    - 📊 Endpoint usage statistics
    - 🔥 Error rates and patterns
    """

    def __init__(self, data_dir: str = "data/monitoring"):
        """Initialize monitoring system"""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Today's metrics (in-memory for speed)
        self.today_metrics = {
            "date": date.today().isoformat(),
            "errors": [],
            "performance": [],
            "endpoint_stats": defaultdict(lambda: {
                "count": 0,
                "total_time_ms": 0.0,
                "errors": 0,
                "status_codes": defaultdict(int)
            })
        }

        # Load today's data if exists
        self._load_today_metrics()

    def log_error(
        self,
        endpoint: str,
        error: Exception,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None
    ):
        """
        Log an error/exception

        Args:
            endpoint: API endpoint where error occurred
            error: The exception object
            user_id: User who triggered the error
            request_id: Request ID for tracing
        """
        # Reset if new day
        if date.today().isoformat() != self.today_metrics["date"]:
            self._save_today_metrics()
            self._reset_daily_metrics()

        # Create error record
        record = ErrorRecord(
            timestamp=datetime.now().isoformat(),
            endpoint=endpoint,
            error_type=type(error).__name__,
            error_message=str(error),
            stack_trace=traceback.format_exc(),
            user_id=user_id,
            request_id=request_id
        )

        # Store error
        self.today_metrics["errors"].append(asdict(record))

        # Update endpoint error count
        self.today_metrics["endpoint_stats"][endpoint]["errors"] += 1

        # Save periodically
        if len(self.today_metrics["errors"]) % 5 == 0:
            self._save_today_metrics()

        logger.error(
            f"❌ Error in {endpoint}: {type(error).__name__} - {str(error)}"
        )

    def log_performance(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        response_time_ms: float,
        user_id: Optional[str] = None
    ):
        """
        Log endpoint performance

        Args:
            endpoint: API endpoint
            method: HTTP method (GET, POST, etc.)
            status_code: Response status code
            response_time_ms: Response time in milliseconds
            user_id: User who made the request
        """
        # Reset if new day
        if date.today().isoformat() != self.today_metrics["date"]:
            self._save_today_metrics()
            self._reset_daily_metrics()

        # Create performance record
        record = PerformanceRecord(
            timestamp=datetime.now().isoformat(),
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            response_time_ms=response_time_ms,
            user_id=user_id
        )

        # Store (only keep last 1000 records in memory)
        if len(self.today_metrics["performance"]) < 1000:
            self.today_metrics["performance"].append(asdict(record))

        # Update endpoint stats
        stats = self.today_metrics["endpoint_stats"][endpoint]
        stats["count"] += 1
        stats["total_time_ms"] += response_time_ms
        stats["status_codes"][status_code] += 1

        # Log slow requests (>3s)
        if response_time_ms > 3000:
            logger.warning(
                f"⚠️ Slow request: {method} {endpoint} - {response_time_ms:.0f}ms"
            )

    def get_error_stats(self) -> Dict:
        """
        Get error statistics

        Returns:
            dict: Error statistics
        """
        errors = self.today_metrics["errors"]

        if not errors:
            return {
                "total_errors": 0,
                "error_rate": 0.0,
                "by_type": {},
                "by_endpoint": {},
                "recent_errors": []
            }

        # Count by type
        by_type = defaultdict(int)
        for error in errors:
            by_type[error["error_type"]] += 1

        # Count by endpoint
        by_endpoint = defaultdict(int)
        for error in errors:
            by_endpoint[error["endpoint"]] += 1

        # Total requests
        total_requests = sum(
            stats["count"]
            for stats in self.today_metrics["endpoint_stats"].values()
        )

        return {
            "total_errors": len(errors),
            "error_rate": (len(errors) / total_requests * 100) if total_requests > 0 else 0,
            "by_type": dict(by_type),
            "by_endpoint": dict(by_endpoint),
            "recent_errors": errors[-5:]  # Last 5 errors
        }

    def get_performance_stats(self) -> Dict:
        """
        Get performance statistics

        Returns:
            dict: Performance statistics
        """
        endpoint_stats = {}

        for endpoint, stats in self.today_metrics["endpoint_stats"].items():
            if stats["count"] == 0:
                continue

            avg_time = stats["total_time_ms"] / stats["count"]

            endpoint_stats[endpoint] = {
                "count": stats["count"],
                "avg_response_time_ms": round(avg_time, 2),
                "errors": stats["errors"],
                "error_rate": round((stats["errors"] / stats["count"]) * 100, 2),
                "status_codes": dict(stats["status_codes"])
            }

        # Calculate p95 latency from stored performance records
        all_times = [p["response_time_ms"] for p in self.today_metrics["performance"]]
        p95_latency = self._calculate_percentile(all_times, 95) if all_times else 0

        return {
            "total_requests": sum(stats["count"] for stats in self.today_metrics["endpoint_stats"].values()),
            "avg_response_time_ms": round(
                sum(stats["total_time_ms"] for stats in self.today_metrics["endpoint_stats"].values()) /
                sum(stats["count"] for stats in self.today_metrics["endpoint_stats"].values())
                if sum(stats["count"] for stats in self.today_metrics["endpoint_stats"].values()) > 0 else 0,
                2
            ),
            "p95_latency_ms": round(p95_latency, 2),
            "by_endpoint": endpoint_stats
        }

    def _calculate_percentile(self, values: list, percentile: int) -> float:
        """Calculate percentile of values"""
        if not values:
            return 0.0

        sorted_values = sorted(values)
        index = int(len(sorted_values) * (percentile / 100))
        return sorted_values[min(index, len(sorted_values) - 1)]

    def _load_today_metrics(self):
        """Load today's metrics from file if exists"""
        today_file = self.data_dir / f"{date.today().isoformat()}.json"

        if today_file.exists():
            try:
                with open(today_file, 'r') as f:
                    data = json.load(f)
                    self.today_metrics["errors"] = data.get("errors", [])
                    self.today_metrics["performance"] = data.get("performance", [])

                    # Rebuild endpoint_stats from loaded data
                    for perf in self.today_metrics["performance"]:
                        endpoint = perf["endpoint"]
                        stats = self.today_metrics["endpoint_stats"][endpoint]
                        stats["count"] += 1
                        stats["total_time_ms"] += perf["response_time_ms"]
                        stats["status_codes"][perf["status_code"]] += 1

                    for error in self.today_metrics["errors"]:
                        endpoint = error["endpoint"]
                        self.today_metrics["endpoint_stats"][endpoint]["errors"] += 1

                logger.info(f"📂 Loaded monitoring data for {date.today().isoformat()}")
            except Exception as e:
                logger.error(f"❌ Error loading monitoring data: {e}")

    def _save_today_metrics(self):
        """Save today's metrics to file"""
        today_file = self.data_dir / f"{self.today_metrics['date']}.json"

        try:
            # Convert defaultdict to regular dict for JSON serialization
            save_data = {
                "date": self.today_metrics["date"],
                "errors": self.today_metrics["errors"],
                "performance": self.today_metrics["performance"],
                "endpoint_stats": {
                    k: {
                        "count": v["count"],
                        "total_time_ms": v["total_time_ms"],
                        "errors": v["errors"],
                        "status_codes": dict(v["status_codes"])
                    }
                    for k, v in self.today_metrics["endpoint_stats"].items()
                }
            }

            with open(today_file, 'w') as f:
                json.dump(save_data, f, indent=2)

            logger.debug(f"💾 Saved monitoring data for {self.today_metrics['date']}")
        except Exception as e:
            logger.error(f"❌ Error saving monitoring data: {e}")

    def _reset_daily_metrics(self):
        """Reset daily metrics for new day"""
        logger.info(f"🔄 Resetting daily metrics for {date.today().isoformat()}")

        self.today_metrics = {
            "date": date.today().isoformat(),
            "errors": [],
            "performance": [],
            "endpoint_stats": defaultdict(lambda: {
                "count": 0,
                "total_time_ms": 0.0,
                "errors": 0,
                "status_codes": defaultdict(int)
            })
        }


class MonitoringMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for automatic monitoring

    Automatically tracks:
    - Response times for all endpoints
    - Status codes
    - Errors (logged separately via log_error)
    """

    def __init__(self, app: ASGIApp, monitoring: MonitoringSystem):
        super().__init__(app)
        self.monitoring = monitoring



# ═══════════════════════════════════════════════════════════════════════════════
# Global Instance
# ═══════════════════════════════════════════════════════════════════════════════

_monitoring_instance: Optional[MonitoringSystem] = None


def get_monitoring() -> MonitoringSystem:
    """
    Get monitoring system singleton

    Returns:
        MonitoringSystem: Monitoring instance
    """
    global _monitoring_instance

    if _monitoring_instance is None:
        _monitoring_instance = MonitoringSystem()

    return _monitoring_instance


# ═══════════════════════════════════════════════════════════════════════════════
# CLI Interface
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="SmartSports Monitoring System")
    parser.add_argument(
        "action",
        choices=["errors", "performance", "summary"],
        help="Action to perform"
    )

    args = parser.parse_args()

    print("═" * 70)
    print("🔍 SMARTSPORTS - Monitoring System")
    print("═" * 70)
    print()

    monitoring = get_monitoring()

    if args.action == "errors":
        print("❌ Error Statistics:")
        print()
        stats = monitoring.get_error_stats()
        print(f"  Total Errors: {stats['total_errors']}")
        print(f"  Error Rate: {stats['error_rate']:.2f}%")
        print()

        if stats['by_type']:
            print("  By Type:")
            for error_type, count in stats['by_type'].items():
                print(f"    {error_type}: {count}")
            print()

        if stats['by_endpoint']:
            print("  By Endpoint:")
            for endpoint, count in stats['by_endpoint'].items():
                print(f"    {endpoint}: {count}")
            print()

    elif args.action == "performance":
        print("⚡ Performance Statistics:")
        print()
        stats = monitoring.get_performance_stats()
        print(f"  Total Requests: {stats['total_requests']}")
        print(f"  Avg Response Time: {stats['avg_response_time_ms']:.2f}ms")
        print(f"  P95 Latency: {stats['p95_latency_ms']:.2f}ms")
        print()

        if stats['by_endpoint']:
            print("  By Endpoint:")
            for endpoint, endpoint_stats in stats['by_endpoint'].items():
                print(f"    {endpoint}:")
                print(f"      Count: {endpoint_stats['count']}")
                print(f"      Avg Time: {endpoint_stats['avg_response_time_ms']:.2f}ms")
                print(f"      Errors: {endpoint_stats['errors']} ({endpoint_stats['error_rate']:.2f}%)")
                print()

    elif args.action == "summary":
        print("📊 System Summary:")
        print()

        error_stats = monitoring.get_error_stats()
        perf_stats = monitoring.get_performance_stats()

        print(f"  Requests: {perf_stats['total_requests']}")
        print(f"  Errors: {error_stats['total_errors']} ({error_stats['error_rate']:.2f}%)")
        print(f"  Avg Response: {perf_stats['avg_response_time_ms']:.2f}ms")
        print(f"  P95 Latency: {perf_stats['p95_latency_ms']:.2f}ms")
        print()

        # Top 3 slowest endpoints
        if perf_stats['by_endpoint']:
            print("  Slowest Endpoints:")
            sorted_endpoints = sorted(
                perf_stats['by_endpoint'].items(),
                key=lambda x: x[1]['avg_response_time_ms'],
                reverse=True
            )[:3]

            for endpoint, stats in sorted_endpoints:
                print(f"    {endpoint}: {stats['avg_response_time_ms']:.2f}ms")
            print()

        # Top error types
        if error_stats['by_type']:
            print("  Top Error Types:")
            sorted_errors = sorted(
                error_stats['by_type'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:3]

            for error_type, count in sorted_errors:
                print(f"    {error_type}: {count}")

    print("═" * 70)
