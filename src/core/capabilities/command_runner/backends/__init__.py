"""Backends de la capability command_runner.

Cada módulo implementa CommandBackend (ver ../backend.py) con un modo de
ejecución concreto. Son intercambiables (ADR-0004): LocalCommandBackend
hoy; SSHBackend, DockerBackend... en el futuro.
"""
