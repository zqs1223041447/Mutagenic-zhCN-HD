#!/usr/bin/env python3
"""Dummy secrets for the redaction test. REAL secret scanners must report only
redacted findings; the raw values in this file must never appear in output.
"""
import os

api_key = "sk-abcdefghijklmnopqrstuvwxyz123456"
aws_key = "AKIAIOSFODNN7EXAMPLE"
github_pat = "ghp_" + "A" * 36
slack_token = "xoxb-123456789012-abcdefghij"