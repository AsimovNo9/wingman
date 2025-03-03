# email_validator.py
# Modified from https://github.com/syrusakbary/validate_email/blob/master/validate_email.py

import re
import smtplib
import logging
import socket

import dns.resolver

try:
    import dns.resolver
    DNS = dns.resolver
except ImportError:
    DNS = None


class ServerError(Exception):
    pass


def resolve_domain(domain):
    if DNS is None:
        raise ServerError(
            "DNS resolution unavailable - dns.resolver not installed")
    try:
        return DNS.resolve(domain)
    except DNS.NXDOMAIN:
        raise ServerError(f"Could not resolve domain: {domain}")


# RFC 2822 patterns
WSP = r'[\s]'
CRLF = r'(?:\r\n)'
NO_WS_CTL = r'\x01-\x08\x0b\x0c\x0f-\x1f\x7f'
QUOTED_PAIR = r'(?:\\.)'
FWS = r'(?:(?:' + WSP + r'*' + CRLF + r')?' + WSP + r'+)'
CTEXT = r'[' + NO_WS_CTL + r'\x21-\x27\x2a-\x5b\x5d-\x7e]'
CCONTENT = r'(?:' + CTEXT + r'|' + QUOTED_PAIR + r')'
COMMENT = r'\((?:' + FWS + r'?' + CCONTENT + r')*' + FWS + r'?\)'
CFWS = r'(?:' + FWS + r'?' + COMMENT + ')*(?:' + \
    FWS + '?' + COMMENT + '|' + FWS + ')'
ATEXT = r'[\w!#$%&\'\*\+\-/=\?\^`\{\|\}~]'
ATOM = CFWS + r'?' + ATEXT + r'+' + CFWS + r'?'
DOT_ATOM_TEXT = ATEXT + r'+(?:\.' + ATEXT + r'+)*'
DOT_ATOM = CFWS + r'?' + DOT_ATOM_TEXT + CFWS + r'?'
QTEXT = r'[' + NO_WS_CTL + r'\x21\x23-\x5b\x5d-\x7e]'
QCONTENT = r'(?:' + QTEXT + r'|' + QUOTED_PAIR + r')'
QUOTED_STRING = CFWS + r'?' + \
    r'"(?:' + FWS + r'?' + QCONTENT + r')*' + FWS + r'?' + r'"' + CFWS + r'?'
LOCAL_PART = r'(?:' + DOT_ATOM + r'|' + QUOTED_STRING + r')'
DTEXT = r'[' + NO_WS_CTL + r'\x21-\x5a\x5e-\x7e]'
DCONTENT = r'(?:' + DTEXT + r'|' + QUOTED_PAIR + r')'
DOMAIN_LITERAL = CFWS + r'?' + \
    r'\[' + r'(?:' + FWS + r'?' + DCONTENT + r')*' + FWS + r'?\]' + CFWS + r'?'
DOMAIN = r'(?:' + DOT_ATOM + r'|' + DOMAIN_LITERAL + r')'
ADDR_SPEC = LOCAL_PART + r'@' + DOMAIN

# A valid address will match exactly the 3.4.1 addr-spec.
VALID_ADDRESS_REGEXP = '^' + ADDR_SPEC + '$'

# Cache for DNS lookups and checks
MX_DNS_CACHE = {}
MX_CHECK_CACHE = {}


def get_mx_ip(hostname):
    """
    Get MX record for hostname.

    Args:
        hostname (str): Domain to check

    Returns:
        list: List of MX records or None if not found

    Raises:
        ServerError: If DNS server returns an unexpected error
    """
    if hostname not in MX_DNS_CACHE:
        try:
            if DNS is None:
                raise ImportError("pyDNS is required for MX record checks")
            MX_DNS_CACHE[hostname] = DNS.mxlookup(hostname)
        except ServerError as e:
            # NXDOMAIN (Non-Existent Domain) or SERVFAIL
            if e.rcode == 3 or e.rcode == 2:
                MX_DNS_CACHE[hostname] = None
            else:
                raise

    return MX_DNS_CACHE[hostname]


def validate_email(email, check_mx=False, verify=False, debug=False, smtp_timeout=10):
    """
    Validate an email address according to RFC 2822 standards with options for MX validation 
    and SMTP verification.

    Args:
        email (str): Email address to validate
        check_mx (bool): Whether to check if the domain has valid MX records
        verify (bool): Whether to connect to the mail server to verify the mailbox exists
        debug (bool): Whether to enable debug logging
        smtp_timeout (int): Timeout for SMTP connections in seconds

    Returns:
        bool or None: True if valid, False if invalid, None if result is uncertain

    Raises:
        ValueError: If email is invalid according to RFC 2822
        ImportError: If DNS checking is requested but pyDNS is not installed
        smtplib.SMTPException: If there are SMTP-related errors during verification
        socket.error: If there are network issues during verification
    """
    if debug:
        logger = logging.getLogger('validate_email')
        logger.setLevel(logging.DEBUG)
    else:
        logger = None

    # Basic format validation
    if not re.match(VALID_ADDRESS_REGEXP, email):
        raise ValueError(
            f"'{email}' is not a valid email address format according to RFC 2822")

    # Check MX records and/or verify email existence
    check_mx |= verify
    if check_mx:
        if not DNS:
            raise ImportError('For checking MX records or verifying email existence, '
                              'you must install the pyDNS package')

        hostname = email[email.find('@') + 1:]
        mx_hosts = get_mx_ip(hostname)

        if mx_hosts is None:
            raise ValueError(
                f"Domain '{hostname}' does not have valid MX records")

        if not verify:
            return True

        # Verify email by connecting to SMTP server
        for mx in mx_hosts:
            try:
                if not verify and mx[1] in MX_CHECK_CACHE:
                    return MX_CHECK_CACHE[mx[1]]

                smtp = smtplib.SMTP(timeout=smtp_timeout)
                smtp.connect(mx[1])
                MX_CHECK_CACHE[mx[1]] = True

                if not verify:
                    try:
                        smtp.quit()
                    except smtplib.SMTPServerDisconnected:
                        pass
                    return True

                status, _ = smtp.helo()
                if status != 250:
                    smtp.quit()
                    if debug:
                        logger.debug(f'{mx[1]} answer: {status} - {_}')
                    continue

                smtp.mail('')
                status, _ = smtp.rcpt(email)

                if status == 250:
                    smtp.quit()
                    return True

                if debug:
                    logger.debug(f'{mx[1]} answer: {status} - {_}')

                smtp.quit()
            except smtplib.SMTPServerDisconnected:
                if debug:
                    logger.debug(f'{mx[1]} disconnected.')
            except smtplib.SMTPConnectError:
                if debug:
                    logger.debug(f'Unable to connect to {mx[1]}.')

        # If we got here, we couldn't verify the email
        return None

    # If no MX checking or verification was requested, just return True for valid format
    return True
