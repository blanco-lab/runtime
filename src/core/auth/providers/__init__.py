"""Proveedores de autenticación registrables en Runtime.

Hoy: solo Spotify. El resto (google, github, telegram...) se añadirá sin
tocar AuthManager ni ProviderAdapter (ADR-0007, ajuste 2).
"""
from .spotify import SpotifyProvider

__all__ = ["SpotifyProvider"]
