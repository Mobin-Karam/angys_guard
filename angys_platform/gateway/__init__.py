"""Server-only fixed-action provider gateway boundary."""

from .router import GatewayDenied, GatewayRouter, RoutedCommand

__all__ = ["GatewayDenied", "GatewayRouter", "RoutedCommand"]
