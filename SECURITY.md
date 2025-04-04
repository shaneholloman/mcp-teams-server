# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Currently supported versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

We take the security of MCP Teams Server seriously. If you believe you have found a security vulnerability, please report it to us as described below.

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to [vuln.disclosure@inditex.com](mailto:vuln.disclosure@inditex.com). You should receive a response within 48 hours. If for some reason you do not, please follow up via email to ensure we received your original message.

Please include the requested information listed below (as much as you can provide) to help us better understand the nature and scope of the possible issue:

* Type of issue (e.g. buffer overflow, SQL injection, cross-site scripting, etc.)
* Full paths of source file(s) related to the manifestation of the issue
* The location of the affected source code (tag/branch/commit or direct URL)
* Any special configuration required to reproduce the issue
* Step-by-step instructions to reproduce the issue
* Proof-of-concept or exploit code (if possible)
* Impact of the issue, including how an attacker might exploit it

This information will help us triage your report more quickly.

## Preferred Languages

We prefer all communications to be in English.

## Process

1. Security report received
2. Security team acknowledges receipt within 48 hours
3. Team investigates and determines severity
4. Team develops and tests fix
5. Team prepares advisory and patches
6. Advisory published, patches released

## Safe Harbor

We support safe harbor for security researchers who:

1. Make a good faith effort to avoid privacy violations, destruction of data, and interruption or degradation of our services
2. Only interact with accounts you own or with explicit permission of the account holder
3. Provide us with a reasonable amount of time to resolve vulnerabilities prior to any disclosure to the public or a third-party
4. Do not exploit a security issue for purposes other than immediate testing

## Security Controls

The MCP Teams Server implements several security controls:

1. All authentication tokens and credentials must be provided via environment variables
2. Communications with the Teams API use HTTPS/TLS encryption
3. Input validation and sanitization for all API endpoints
4. Rate limiting to prevent abuse
5. Regular security updates and dependency checks

## Security-related Configuration

For secure operation, please ensure:

1. Environment variables are properly secured and not logged
2. Access tokens have minimum required permissions
3. Production deployments use HTTPS/TLS
4. Regular security updates are applied
5. Proper logging and monitoring is configured

## Third-party Security Notifications

We review security reports for our dependencies and follow responsible disclosure guidelines.
